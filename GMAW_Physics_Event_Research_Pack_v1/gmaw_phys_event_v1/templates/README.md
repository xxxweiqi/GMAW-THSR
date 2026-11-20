# 数据与研究记录模板

本目录提供空白格式，不包含新的真实实验记录，也不生成可训练的占位数据。`data/*.csv`只有表头，故不能直接通过validate_data作为完整数据集。请把它们复制到实际数据目录并填入已核实的数据。

## 数据表

| 模板 | 填写要点 |
| --- | --- |
| data/manifest.csv | 每个连续、单向前进的segment一行；同一seam只能有一个split |
| data/signals_native.csv | 原生共同时间t_s、A、V；可由import_csv转NPZ |
| data/frames.csv | 曝光锚点t_s与实际可用available_t_s分别记录；image_path相对数据根目录 |
| data/trajectory.csv | t_s和沿焊接前进方向s_mm严格递增；停顿/反向需上游分段 |
| data/events.csv | 只写缺陷/Unknown事件；Normal由已检测且未被事件占据的背景定义 |
| data/predictions.csv | 外部模型统一评价的输出模板，复制真实dataset.records后添加p_defect |
| data/evaluation_events.csv | 统一评价真值；由数据加载器导出并含reference_t_s |

所有时间单位秒，长度单位毫米，功率单位瓦。manifest中的view_offset_mm按`s_target=s_arc+view_offset`定义。position_sigma_mm和boundary_sigma_mm来自误差评估，不能为了提分任意缩小。inspection_start/end只覆盖已确认检查的区间。initial_power_w为热代理初值依据；从稳定焊接中途截取的段不能无条件设为0。

split只允许train/val/test。synthetic只填true/false或1/0，真实记录填false；禁止把未取得的数据伪装成真实样本。路径采用正斜杠相对路径，不能指向目录外。sample_id全局唯一，event_id在每段唯一。

frames中的width_rel、length_rel、area_rel为固定ROI内[0,1]比例。没有有效几何时geom_valid=false，几何列可空；不要填写虚构的0尺寸。已知其他缺陷如Hollow、L-Crack会成为排除区域；不得重命名为Normal。空事件表仅在确实完成检查且没有事件时适用。

## 过程记录

- metadata_record.yaml：实验来源、设备、接头、文件身份、数据状态及缺失项。
- calibration_record.yaml：时钟、曝光、视场偏置、RT空间映射和独立核查残差。
- annotation_review.csv：两位审核者、原始区间、分歧与最终决议。
- experiment_log.yaml：假设、冻结划分、配置、阈值策略、种子、实际结果路径与偏离记录。

YAML中的null表示尚未填写；这些记录文件不被模型自动读入，也不自动替代manifest中的数值。填写它们是为了保留校准和实验依据。校准公式与误差先完成，再把明确结果写入标准数据表。

检查模板是否与代码表头一致：

```bash
python templates/check_templates.py
```

该检查只验证模板结构，不验证真实测量正确性。整理真实数据后，另执行：

```bash
python scripts/validate_data.py --data dataset_real --output results/real_validation.json
```
