# 数据契约与导入说明

本包是可运行的研究参考实现，不含作者的原始 MBGN 源码、工业数据或预训练权重。默认二分类目标是 Normal / Undercut。其他缺陷不作为 Normal。所有合成数据只能证明软件流程可执行。

## 1. 数据目录

根目录必须有 `manifest.csv`。所有路径均相对数据根目录，用正斜杠；绝对路径、越界 `..`、指向外部的符号链接会被拒绝。不要使用 pickle 或对象 NPZ。

| 文件 | 必须字段 | 含义 |
|---|---|---|
| manifest.csv | seam_id,segment_id,split,signal_path,frames_path,trajectory_path,events_path,material,thickness_mm,view_offset_mm,position_sigma_mm,inspection_start_mm,inspection_end_mm,initial_power_w,synthetic | 一个单调前进焊接段一行；一个 seam 只能归入一个 split |
| 原始电信号 NPZ | t_s,current_a,voltage_v | 同一校正时钟的原生采样，一维等长有限数组；不得预先降采样后冒充原生数据 |
| frames.csv | sample_id,t_s,available_t_s,image_path,width_rel,length_rel,area_rel,geom_valid | 图像时间、可用时间、可选几何监督；sample_id 全局唯一 |
| trajectory.csv | t_s,s_mm | 已同步的实际轨迹；时间和沿焊缝位置严格增加 |
| events.csv | event_id,start_mm,end_mm,class_name,confidence,boundary_sigma_mm | 焊后检查区段；event_id 在 seam/segment 内唯一 |

`split` 是 train、val、test。`synthetic` 是 true/false。`view_offset_mm` 表示当前目标位置相对电弧位置的几何偏移，必须由相机/工件几何或独立标定获得，不能利用测试 RT 标签来调参。`inspection_start_mm/end_mm` 表示已确认完成检查的范围，而非模型猜测的正常范围。范围之外不参加分类训练或评分。

`initial_power_w` 是记录的起始功率/初始代理状态设定。起弧前明确冷态可设0；中途截断的热态记录不能无依据设0。应保留较长前缀并用 warmup 排除初始过渡，或提供上段连续状态的合法重建。本实现尚不支持任意磁盘分块的热状态自动接续。

`width_rel/length_rel/area_rel` 是同一固定 ROI 中的相对几何量，取值0到1，不是毫米、温度或真实熔池体积。必须一致标定和注释。没有几何观察时设 `geom_valid=0`，数值可留空；目标损失自动屏蔽。ROI 检测框不等于熔池分割真值。

## 2. 严格的因果输入

每个样本的电波形使用 `[t-0.1,t]`，不使用原论文的中心±50ms窗。所有图像历史的帧时刻不晚于当前帧。决策可用时间取所有已使用图像的最大 `available_t_s` 与当前采样时刻的最大值；尚不包含模型运行、通信及执行器延迟。

机器人位置使用当前时刻之前最后一个已观测轨迹点；速度使用两个过去点的差分。不会用未来轨迹点插值给在线模型。轨迹采样太稀疏以至相邻图像目标位置重复时拒绝加载，不能伪造运动分辨率。

电功率先由原生 `U(t)*I(t)` 计算，再以原生样本左端保持积分。125ms功率均值由该积分得到；严禁以平均U乘平均I替代，也不使用降采样波形重新计算能量。该积分是采样保持近似，不宣称精确热输入。电源侧功率与实际工件吸收功率有区别。

热代理在整个焊接段的125ms网格（加入实际图像锚点）上递推，随后取各帧状态；不会在每个监督窗口起点清零。状态由 `physics.thermal_filter_bank` 提供，时间常数来自配置，初值来自 manifest。所有输入功率非负；负功率需要事先确认极性/采集规则，不会被静默截断。

波形重采样使用 `scipy.signal.resample_poly` 的多相低通抗混叠。原生时间可有少量抖动，先在过去窗口内重建均匀网格，再重采样；滤波边界用线性延拓，延拓只依赖窗口内过去值。上采样不会恢复原数据没有的频率信息。I和U分别以固定400A、40V缩放，避免训练/测试统计混用。

`geom_target` 是未来指定帧的几何监督标签，始终与 `geom_mask` 单列；不进入模型前向计算。在训练中用于辅助损失，在验证和测试中只用于离线几何误差评估。跨缺帧间隔或缺几何观察时屏蔽。改变未来几何标签不能改变当前输入及预测。

## 3. 物理对齐与RT标签隔离

对齐先验只依赖历史电弧位置、当前目标位置、预先指定的几何支持范围和位置不确定性。RT事件坐标、缺陷类别、confidence均不参与先验或输入构造。没有合法几何支持的样本跳过并记录原因。

对于目标区间 `[a,b]` 和位置 `s`，合成标准差为：

`sigma_eff = sqrt(boundary_sigma_mm^2 + position_sigma_mm^2)`。

单个区间的软目标为 `Phi((s-a)/sigma_eff)-Phi((s-b)/sigma_eff)`；零标准差时退化为区间指示。多区间取最大值，属于保守软目标，不能解释为各事件并集的精确概率。硬标签仍按原始区间定义。距任一边界不超过 `2*sigma_eff` 的样本标记不确定。

confidence只降低对应邻域的标签权重，不把低可信缺陷改成正常。其他缺陷、Unknown等区间扩张2倍合成标准差后排除；零权重样本也排除。它们造成的覆盖空洞同时从评分单元中切除。

## 4. 覆盖、事件与导出

预测记录包含 `sample_id,seam_id,segment_id,s_mm,cell_start_mm,cell_end_mm,t_frame_s,t_decision_s,y_hard,y_soft,label_weight,boundary_uncertain,synthetic`。单元以相邻原始帧位置中点构造，限制在实际可用/检查覆盖内；缺帧、warmup和其他缺陷排除形成的空白不能被扩大成已评估正常区域。

目标事件表另含 `reference_t_s`：由完整已观测轨迹离线求得电弧经过真实事件起点的时间，仅供评估延迟，不是模型输入。轨迹未覆盖起点时该参考时间缺失，不向外假造。事件覆盖截断及未覆盖事件由评估模块报告。

数据对象提供 `.records`、`.events`、`.summary` 以及 `export_metadata(output_dir)`。汇总记录每一种样本跳过原因。验证指纹完整哈希 manifest、CSV与原始信号字节；图像仅记录相对路径和文件大小，因此指纹不证明图像内容逐字节不可变。如需档案级可复现，应另行对全部图像做内容哈希。

## 5. 使用

```bash
python -m gmaw_phys.demo --output dataset_demo --seed 42
python scripts/validate_data.py --data dataset_demo --output results/validation.json
python scripts/import_csv.py --source /path/to/explicit_csv_dataset --output /path/to/imported_dataset
```

CSV导入要求源目录已具备上述完整 manifest/frames/trajectory/events。仅原始信号用CSV，列名必须是 `t_s,current_a,voltage_v`；导入器只复制原有记录并转换存储格式，不生成时间戳、轨迹、检查覆盖、缺陷或训练划分。若工业文件命名或列格式不同，必须编写经核验的适配层，并保留单位、时钟与工件关系的证据。

合成fixture为9条独立seam、每条16至24秒、2kHz原生电信号、8Hz的64×64图像、每条2个人工事件，5/2/2分配train/val/test。它含人为设定的缺陷相关模式，无真实焊接机理或工业效能含义。

## 6. 内存和已知限制

波形及图像按帧惰性缓存，最多各256帧；不预先复制每个历史窗口。原始信号采用1个焊接段的LRU缓存。压缩NPZ无法内存映射，100kHz长段仍可能占用大量内存；随机打乱不同焊接段会反复解压，适合先做可控规模子集。工业大数据应进一步开发按段采样、支持记忆映射的原始存储和热状态连续接续；不能仅为节省内存切段后丢掉物理历史。

数据验证默认以原生间隔中位数的2.1倍检查明显采集空洞；构建器同时执行配置中的 `max_signal_gap_factor`。缺口需要在上游显式处理，不会用长距离线性插值补成真实观测。模型内的低维热状态和几何时间先验均是研究假设，必须通过真实独立焊缝及受控试验验证。
