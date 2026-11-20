# 现有MBGN的接入设计与外部预测评价

## 1. 这份文档的身份

这是接口设计和实施检查单，不是已经完成的原始MBGN集成。当前包没有原始MBGN源码、原训练权重或全部工业数据。`gmaw_phys/models.py`中的轻量CNN是可执行参考结构，不能通过更改名称充当原始MBGN。

接入前需要：原代码和版本/提交身份；真实1D/2D编码器输出形状；BiFPN和Gate实现；五类类别顺序；裁剪、标准化和时间窗口规则；权重和训练划分；可回溯的原生信号、图像时间戳、机器人轨迹及RT区间。论文中给出的名称和结构示意不能替代这些材料。

## 2. 最小改动与严格物理支持是两种不同实验

**保留原始当前融合分支，再追加热/历史残差分支**，是容易实施的工程方案。但原始分支仍直接使用当前电信号；若该信号位于相机观察位置的物理支持之外，完整网络仍有绕过掩码的路径。因此只能说“新增历史分支有物理支持”，不能声称“模型全部电信息都满足支持”。这一路线可以保留作显式对照，不能混入严格对齐消融。

**在原有BiFPN/Gate之前对电特征作受限历史聚合**，才适合检验本方案H1。保留原1D编码器、2D编码器及原融合模块的定义与权重初始化，把原本当前时刻的电特征替换为物理支持内历史特征的加权聚合。当前图像分支保持可用。各尺度输出形状必须与实际原融合模块匹配；必要的投影需记录参数数并接受重新训练。

改变输入时序与分布后，原权重只是初始化，不是原模型行为的无修改复现。应同时保留未修改原模型的可追溯外部结果，和采用因果窗口后重新训练的适配结果。

## 3. 建议的数据与特征接口

使用本包 `build_dataset(root,cfg,split)`生成共同样本索引、因果历史、热状态和物理支持。一个batch的主要字段是：

| 字段 | 形状 | 来源 |
| --- | --- | --- |
| signal | B×L×2×N | 当前及过去向后窗口 |
| image | B×L×3×H×W | 已可用图像，当前适配先用最后一帧 |
| power | B×L×1 | 完整功率bin内原生U×I平均 |
| thermal | B×L×K | 全段积分后切片的固定热状态 |
| condition | B×2 | 厚度与实际速度的固定尺度归一化 |
| alignment_prior / mask | B×L | 轨迹、视场偏置及位置误差 |
| index | B | 回到dataset.records的唯一索引 |

未来 `geom_target` 和事件标签只进入训练损失或评价，不进入编码器、对齐或融合。热状态不能在模型forward内按每个batch窗口从零积分。原MBGN若只接收标准化后的100 ms切片，尚不足以恢复连续125 ms功率驱动，必须返回原生流或完整连续功率bin。

将原1D编码器作用于各历史窗口，取得每个尺度的特征S[l,j]；当前图像产生V[l]。如果原融合实际接收向量，按其原池化方式处理；如果接收特征图，聚合需在保持兼容形状的轴上执行，不能凭论文示意假定256维即可。

## 4. 对齐聚合示例

以下是数学/接口示例，名称 `original_encoder`、`original_fusion` 不是本包已提供的原MBGN类，需拿到真实源代码后实现适配：

```python
# Conceptual interface only; not a completed original-MBGN adapter.
# S_l: [B, L, D_l], obtained from the real electrical encoder.
# V: current image features from the real image encoder.
thermal_weight = torch.softmax(global_thermal_logits, dim=0)
z = (batch["thermal"] * thermal_weight[None, None, :]).sum(-1, keepdim=True)
keys = key_projection(torch.cat([electrical_tokens, batch["power"], z], dim=-1))
query = query_projection(current_image_features)
score = (keys * query[:, None, :]).sum(-1) / keys.shape[-1]**0.5
score = score + batch["alignment_prior"].clamp_min(torch.finfo(score.dtype).tiny).log()
mask = batch["alignment_mask"].bool()
if not mask.any(dim=1).all():
    raise ValueError("Unsupported samples must be excluded upstream")
alpha = score.masked_fill(~mask, -torch.inf).softmax(dim=1)
S_aligned = [(alpha[:, :, None] * scale).sum(dim=1) for scale in electrical_scales]
# Feed the aligned scales and the current visual scales into the REAL fusion.
# No additional unmasked electrical skip connection in the strict-support run.
```

key/value不能先经过跨时间GRU，否则支持外信号可能进入支持内隐藏状态。全段热状态中的早期历史是物理热记忆，允许保留；这是与“直接电token应在局部支持内”不同的一条假设。记录两者的作用范围，避免错误地声称模型不使用任何更早信息。

热支路可以通过带零初始化输出层的残差投影接入原融合特征，也可仅用于key和门控。两者改变的参数、监督和梯度路径不同，应分别命名。不得同时更换原backbone、类别采样、增强、损失和输入时间范围，再把总变化归因于热约束。

## 5. 输出与类别映射

二分类适配头输出单个raw logit，`sigmoid(logit)`作为p_defect。若原模型仍输出五类，必须记录类别顺序并在验证前固定映射政策。例如可使用Undercut的原softmax概率，或对Normal/Undercut两类logit做条件归一化；两种概率定义不同，不能看测试结果后挑选较好者。使用条件归一化时还应导出其他类别概率总和，保留范围外预测诊断。

本评价的真实类别只纳入已确认Normal和Undercut；其他缺陷/Unknown及未检查位置必须在cell构建阶段排除。不要把五类中的其他类在真值端强行改成Normal，也不要以预测类别决定是否剔除困难样本。

外部预测CSV推荐完整保留以下字段：

```text
sample_id,seam_id,segment_id,s_mm,cell_start_mm,cell_end_mm,t_frame_s,t_decision_s,y_hard,y_soft,label_weight,boundary_uncertain,synthetic,split,p_defect
```

`cell_start_mm/cell_end_mm`必须来自实际采样与检测覆盖，不能为稀疏预测人为扩展大区间。对同一数据集，推荐复制 `dataset.records` 并按index加入p_defect，避免排序后按行号误配。下面的导出片段可用于外部工程，但 `p_defect_by_index` 须由真实模型生成：

```python
import pandas as pd

rows = []
for index, probability in p_defect_by_index.items():
    row = dict(dataset.records[int(index)])
    row["p_defect"] = float(probability)
    row["split"] = "test"
    rows.append(row)
pd.DataFrame(rows).to_csv("external/test_predictions.csv", index=False)
dataset.events.to_csv("external/test_events.csv", index=False)
```

应确认恰好覆盖冻结评估集合，无重复index、无缺失sample_id，且概率有限并落在[0,1]。验证集合以独立文件导出，保持焊缝身份互斥。

## 6. 使用统一评价

```bash
python scripts/evaluate_predictions.py --predictions external/test_predictions.csv --events external/test_events.csv --validation-predictions external/val_predictions.csv --validation-events external/val_events.csv --save-threshold-json external/threshold.json --method-name original_MBGN_external --output external/test_metrics.json --bootstrap 1000
```

首次选择只使用独立验证文件；评价工具检查验证与测试seam_id不重叠。后续重用已冻结阈值：

```bash
python scripts/evaluate_predictions.py --predictions external/test_predictions.csv --events external/test_events.csv --threshold-json external/threshold.json --method-name original_MBGN_external --output external/test_metrics_repeat.json
```

method-name只是来源标签，不会让评价工具自动证明原模型已复现。原训练划分、权重、居中窗口造成的未来50 ms等待、离线裁剪及真实数据读取仍由外部实验记录负责。统一事件评价不能修复上游数据泄漏。

## 7. 原始代码接入后的验收

先核对无改动原模型在同一冻结输入上的输出，建立身份基准；再核对改为因果窗口后需要重新训练的范围。检查每个尺度形状、归一化、单位、热初值、全局混合和空支持处理。通过改变未来数据、RT标签和无效电token分别确认输入因果性与掩码作用；检查电、图像、热支路梯度。最后在独立焊缝上运行同结构消融。

仅在上述源代码、数据和实际结果齐备后，才可以把“原MBGN集成完成”列入交付。当前包完成的是参考实现、接口设计与外部预测统一评价能力。
