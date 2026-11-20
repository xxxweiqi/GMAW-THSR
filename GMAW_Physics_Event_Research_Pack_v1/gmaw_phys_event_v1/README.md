# GMAW物理约束与咬边事件识别：可运行研究包

本包把“因果时空对齐、归一化热记忆、边界不确定性、事件级评价”组织成可运行的参考实验。主任务为 **Normal / Undercut二分类**，包含5种参考网络、8项预定义实验、简单固定滤波线性分类基线、合成数据、训练/预测/事件评价工具，以及中文实验方案和数据模板。

**本包没有包含用户的原始93,570组工业数据，也没有拿到并复现原始MBGN源代码。** B0是独立编写的轻量因果参考基线，不能称为原MBGN。随包dataset_demo全部为明确标记的合成数据，人工构造了信号、图像与标签之间的相关性。合成分数只验证软件流程，不证明真实咬边识别精度、物理机理或预期提分。

## 1. 先从这里开始

1. 需要看研究怎么做：阅读 `docs/GMAW_Experiment_Plan_v1.pdf` 或可编辑Word同名文件，Markdown源稿为 `docs/experiment_plan_zh.md`。
2. 需要直接运行演示：安装依赖后执行 `python run_demo.py`。
3. 需要导入真实数据：阅读第5节与 `templates/README.md`，先完成校准和文件整理。
4. 需要接现有MBGN：阅读 `docs/mbgn_integration.md`；其中是接口设计，不是已经完成的原始模型改造。
5. 需要检查评价口径：阅读 `docs/evaluation_protocol.md` 与 `docs/model_notes.md`。

代码在Python 3.12、PyTorch 2.6.0 CPU环境中开发与测试；requirements.txt列出依赖范围，CPU可以运行合成演示。真实100 kHz电流电压和128像素图像训练更耗时，可在匹配的GPU环境运行。代码不会在训练时下载预训练权重。

## 2. 安装

将整个文件夹解压到本地路径，打开终端并进入该文件夹。建议使用独立虚拟环境，避免修改已有研究环境。

Windows PowerShell（以下直接调用环境内Python，不要求更改脚本执行策略）：

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe scripts/check_environment.py
.venv\Scripts\python.exe run_demo.py
```

macOS / Linux：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/check_environment.py
.venv/bin/python run_demo.py
```

下文以 `python` 简写当前研究环境的解释器。若未激活虚拟环境，请替换为上面的环境内Python路径。依赖安装需要能够访问相应软件包源；安装完成后，数据处理、训练与演示本身不需要联网。`train.device: auto`按实际CUDA可用性选择设备；指定cuda但没有可用CUDA时会明确报错。

Windows/Linux仅做CPU演示时，可先在该虚拟环境中执行 `python -m pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu`，再安装requirements；macOS使用前述普通安装命令。GPU安装应按本机CUDA/驱动与PyTorch官方安装说明匹配。本交付实测为CPU环境，未声称完成GPU性能测试。

## 3. 一条命令演示、输出与重复运行

```bash
python run_demo.py
```

默认读取 `dataset_demo` 和 `configs/smoke.yaml`，训练P_full参考结构，验证集早停/选择阈值后评估测试集，并在新目录 `results/my_demo` 绘图。已存在的输出目录会被拒绝，避免覆盖旧记录。再次演示请换目录：

```bash
python run_demo.py --out results/my_demo_02 --epochs 3 --seed 42 --device cpu
```

主要输出如下：

| 文件 | 用途 |
| --- | --- |
| model.pt | 参考模型权重与配置；不是原始MBGN权重 |
| resolved_config.yaml | 本次实际解析后的配置 |
| data_validation.json | 原始数据结构、采样与分组核查 |
| train_data_summary.json、val_data_summary.json、test_data_summary.json | 各集合可用样本、排除与覆盖摘要 |
| training_history.csv | 训练及验证分类损失 |
| predictions_val.csv / predictions_test.csv | 冻结检查点的逐样本预测与物理cell |
| events_val.csv / events_test.csv | 对应集合的目标事件表 |
| threshold_selection.json | 验证集阈值政策及冻结结果 |
| metrics_test.json | 帧、事件、覆盖与辅助几何指标 |
| run_info.json | 参数数、软件版本、种子和运行身份 |
| prediction_diagnostic.png / .pdf | 某条测试焊缝上的预测与事件区间 |
| training_diagnostic.png | 训练曲线 |

包内合成数据为9条焊缝，按5/2/2条划分训练/验证/测试；图像8 Hz，原生合成电信号2 kHz，每条有两个人工构造的目标事件。它不是原论文100 kHz数据的替代品。smoke配置还把电窗口重采样为128点以加快运行，因此不能拿它研究原始高频物理特征。

需要生成另一组可重复合成数据时：

```bash
python -m gmaw_phys.demo --output dataset_demo_new --seed 123
python run_demo.py --data dataset_demo_new --out results/demo_new
```

生成器拒绝覆盖非空目录。run_demo只接受全部标记为synthetic的数据；真实研究请使用下述正式入口。

## 4. 模型与物理约束做了什么

电信号窗口使用 `[t−0.1 s,t]`，没有原论文居中窗口中的未来50 ms。全段原生U×I先作因果积分，再生成平均功率bin和热状态，避免只从100 ms图像配对窗口计算125 ms功率而漏掉间隔。热状态一次覆盖整个连续segment，之后切片，不在每个训练窗口重新置零。

归一化状态满足 `dz/dt=(P/P_ref−z)/tau`，tau为固定正数候选；模型只学习全局非负、和为1的混合权重。它是耗散代理，不是温度、热效率或三维能量场。research默认tau为0.15/0.35/0.75/1.5 s，未经实测热标定。

对齐依据 `s_target=s_arc+view_offset_mm`，由轨迹和相机几何建立Gaussian先验及有限空间支持。当前图像为query，历史电特征与热状态为key/value；支持外注意力严格为0。原始缺陷框、标签及未来几何不会被模型forward读取。

几何辅助任务预测未来一帧的相对宽、长、面积。未来观测只作为训练或离线评价目标；推理不需要未来真值。辅助量是ROI比例，不是毫米或温度。

## 5. 真实数据怎么准备与校验

先完成真实数据的共同时间轴、曝光/可用时间、轨迹、ROI视场偏置、RT物理标记配准和独立事件复核。仅有论文PDF、截图或随机抽出的配对数组不足以恢复这些信息。对缺失部分应保留缺失，不能让导入脚本猜测时间、正常标签或焊缝位置。

每个连续、单向前进的焊接segment提供以下文件；所有路径相对数据根目录，使用 `/`，不能越出根目录或使用Windows反斜杠路径。

| 文件 | 必要内容 |
| --- | --- |
| manifest.csv | 焊缝/段身份、train/val/test、文件路径、材料板厚、视场偏置、位置误差、检测覆盖、初始功率、synthetic |
| signals.npz | 数值一维数组t_s、current_a、voltage_v；allow_pickle=False可读取 |
| frames.csv | 全局唯一sample_id、t_s、available_t_s、image_path、三项可选几何及geom_valid |
| trajectory.csv | 严格递增的t_s与s_mm，已经转换到共同时间轴 |
| events.csv | event_id、start_mm、end_mm、class_name、confidence、boundary_sigma_mm |
| 图像文件 | 帧表引用的可读取图像 |

`templates/data`提供仅含表头的格式模板；它们不是可训练数据。模板与记录用法见 `templates/README.md`。真实数据的synthetic填false；不能把合成和真实数据混入同一研究集合后合并报告。

校验命令：

```bash
python scripts/validate_data.py --data dataset_real --output results/real_validation.json
```

校验检查文件、数值、严格时间/轨迹顺序、采样缺口、跨集合复用、全局sample_id及几何范围。它不能代替人工确认时钟标定、正确RT类别或检查图像是否真的看见熔池。一个已有焊缝的全部segment只能进入一个split；Known其他缺陷和Unknown区间排除，不作为Normal；检测覆盖外不作为已知负样本。

若原生电参量现为CSV，可先按标准manifest与帧/轨迹/事件格式整理source目录，再运行：

```bash
python scripts/import_csv.py --source source_csv --output dataset_real
```

该导入器仅把 `t_s,current_a,voltage_v` 原生CSV转为NPZ并复制明确引用的图像/表；不自动读厂家私有格式，不自动标定，不推断缺陷。输出目录必须与源目录分开，不能覆盖非空目录。已有合规NPZ则无需导入。

特别约束：U×I负值会报错，需在上游查明极性/零漂并记录；不自动剪成零。不完整电流采集、大幅时间跳变、停顿/回焊应在上游分段。没有有效几何时geom_valid=false，几何列可为空；真实图像和基本时序仍不可缺失。没有咬边事件的已检测段可使用仅表头events.csv，不要虚构一条Normal事件。

## 6. 单模型训练、预测与绘图

先复制并修改research配置，冻结焊缝划分、空间支持和预处理规则。配置内的位置误差下限、tau、历史长度和IoU阈值都是研究设置，不是已经验证的物理常数。

```bash
python scripts/run_experiment.py --data dataset_real --config configs/research.yaml --out results/real_P_full --model phys_align --seed 42
python scripts/plot_results.py --run results/real_P_full
```

运行不同参考基线：

```bash
python scripts/run_experiment.py --data dataset_real --config configs/research.yaml --out results/real_B0 --model snapshot_fusion --seed 42
```

`--model`接受snapshot_fusion、history_gru、power_features、thermal_filter、phys_align。使用非phys_align名称时入口关闭不适用的对齐/辅助开关，thermal_filter保留热支路。也可通过配置明确设置 `use_heat/use_alignment/use_aux`。

已训练模型只导出预测：

```bash
python scripts/predict.py --data dataset_real --checkpoint results/real_P_full/model.pt --split test --device cpu --out results/reexport/test_predictions.csv
```

该入口会同步导出 `test_predictions_events.csv`。预测不自动选择新的阈值，不需要重新训练。正式对比应保存原验证阈值并使用同一事件评价参数。

## 7. 八项消融与简单基线

```bash
python scripts/run_suite.py --data dataset_real --config configs/research.yaml --matrix configs/experiments.yaml --out results/real_suite --seeds 17,42,73
```

| 实验ID | 结构 | 热状态 | 物理对齐 | 几何辅助 |
| --- | --- | --- | --- | --- |
| B0_reference | snapshot_fusion | 否 | 否 | 否 |
| B1_history | history_gru | 否 | 否 | 否 |
| B2_power_features | power_features | 否 | 否 | 否 |
| B3_thermal_filter | thermal_filter | 是 | 否 | 否 |
| A1_no_heat | phys_align | 否 | 是 | 是 |
| A2_no_alignment | phys_align | 是 | 否 | 是 |
| A3_no_aux | phys_align | 是 | 是 | 否 |
| P_full | phys_align | 是 | 是 | 是 |

只运行指定实验，或先在合成数据做短流程检查：

```bash
python scripts/run_suite.py --data dataset_demo --config configs/smoke.yaml --out results/suite_smoke --seeds 42 --epochs 2 --only B0_reference,A2_no_alignment,P_full
```

同结构比较以P_full对A1/A2/A3为主。B0与完整模型的差别同时包括历史、结构和额外监督，不能把总增益都解释为物理约束。参数数会记录，但不保证相等。固定滤波+逻辑回归的低复杂度比较入口：

```bash
python scripts/run_linear_baseline.py --data dataset_real --config configs/research.yaml --out results/real_linear
```

该脚本使用因果热滤波、当前功率、工况及当前电/图像统计，训练集拟合标准化和逻辑回归；它不是ARX，也不是自动发现物理方程。若要区分热约束与普通指数平滑，仍需预注册匹配的额外对照。

## 8. 统一评价与配对比较

重新评价保存的参考或外部方法预测：

```bash
python scripts/evaluate_predictions.py --predictions results/real_P_full/predictions_test.csv --events results/real_P_full/events_test.csv --threshold-json results/real_P_full/threshold_selection.json --output results/real_P_full/evaluation_with_ci.json --bootstrap 1000 --method-name reference_phys_align
```

默认IoU、间距和最小长度应与冻结配置一致；修改过配置时，需传入对应 `--iou-threshold`、`--merge-gap-mm`、`--min-length-mm`。脚本拒绝在已保存阈值后悄悄改变这些参数。也可提供独立验证预测/事件选择阈值，详见集成文档。

事件匹配先最大化合格一对一匹配数，再最大化总IoU。未观察事件单列，部分覆盖保留身份；误报分母是实际可评估区间并集。first_threshold_hit_delay_s是离线首次命中统计，不包含模型运行、迟滞报警或执行器延迟。单类或空事件时不可定义的指标输出null。

配对比较两项使用相同测试样本、真值及评价设置的训练运行：

```bash
python scripts/compare_runs.py --run-a results/real_suite/P_full/seed_42 --run-b results/real_suite/A2_no_alignment/seed_42 --output results/comparison_alignment.json --label-a P_full --label-b A2_no_alignment --bootstrap 1000 --seed 42
```

该工具审查冻结阈值来源、事件参数和样本覆盖后，以相同焊缝cluster抽样计算差值。不能将训练种子重复当成新增焊缝。固定误报事件/米约束下选阈值、嵌套LOSO与硬/软标注专门消融目前不是默认流水线，实验方案将其列为需另外预注册的工作。

已有保存检查点还可运行因果延迟压力检查：

```bash
python scripts/stress_causal_delay.py --data dataset_demo --checkpoint results/smoke_full/model.pt --output results/my_stress --delays 0,1,2,4 --split test
```

该命令不重新训练，使用已冻结检查点和阈值，把电信号、功率与热状态历史向过去移动；当前图像、目标位置、工况及标签保持不变。delays单位是原始图像帧数，不是毫秒。在所有延迟条件共同可用的样本上重新计算0延迟基线，不能直接与原完整测试集分数比较；输出目录应为新目录。这是“电传感数据变旧”的离线敏感性检查，不是时钟校准，也不代表已经测得真实通信延迟。真实数据研究须预先登记延迟范围，不能借测试压力结果重新选择生产阈值。

## 9. 测试与模板检查

本版实际执行记录见 `docs/verification_zh.md`；原始测试日志及机器可读摘要在 `results/verification`。先核对整个交付包可运行 `python scripts/verify_integrity.py`。

```bash
python -m unittest discover -s tests -v
python templates/check_templates.py
```

测试包括物理响应、因果边界、对齐掩码、数据排除、事件匹配与统计比较等。测试通过只覆盖已编码的行为，不验证真实配准是否正确。模板检查仅核对表头和记录结构；空模板无法通过真实数据校验，这是预期行为。

## 10. 现有数据与原始MBGN的必要边界

原文93,570组配对样本、2,166组监督子集和936个咬边样本不是936个独立事件。正式研究应首先重建事件、焊缝与检测覆盖，避免帧级随机切分造成泄漏。没有足够独立焊缝时，应报告结论不确定，不能用更多相邻帧替代补试验。

8 Hz图像无法验证高速熔滴运动；热代理未经过测温校准；仅凭该数据不能声称恢复了完整温度场或证明所有缺陷成因。原始模型实现、权重、原始切分、原生信号、时间戳和RT配准材料齐备后，才能开展原MBGN复核与接口改造。当前文档中的适配示例不改变这一事实。

本包用于离线研究与方法比较；生产流式缓存、在线裁剪、硬件延迟、报警迟滞、设备控制和自动调参闭环没有实现。完整研究设计、18条新增焊缝先导建议、停止条件和论文图表清单均见中文实验方案。报告中请保留synthetic标记和这些证据边界。
