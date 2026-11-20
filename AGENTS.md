# 热历史与时空配准约束的 GMAW 多模态缺陷事件识别方法

## 研究目标

融合焊接电流、电压与熔池图像，研究热历史、因果时空配准和标注边界不确定性对咬边事件识别的影响。当前任务为正常（Normal）与咬边（Undercut）二分类。在独立焊缝上评价咬边事件的检出情况，以及单位评估焊长上的误报数。

## 数据路径

研究包位于 `GMAW_Physics_Event_Research_Pack_v1/gmaw_phys_event_v1/`。下表与代码入口中的相对路径均从该目录起算。

| 数据 | 路径 |
| --- | --- |
| 真实工业数据根目录 | |
| 合成演示数据与样本清单 | `dataset_demo/`、`dataset_demo/manifest.csv` |
| 数据导入格式与表头模板 | `docs/data_contract.md`、`templates/data/` |

## 代码入口与实验迭代

| 用途 | 入口 |
| --- | --- |
| 运行合成数据演示 | `python run_demo.py` |
| 校验数据 | `scripts/validate_data.py` |
| 训练与评估单项实验 | `scripts/run_experiment.py` |
| 批量运行预定义实验 | `scripts/run_suite.py`，实验定义见 `configs/experiments.yaml` |
| 预测与事件级评价 | `scripts/predict.py`、`scripts/evaluate_predictions.py` |

研究方案见 `docs/experiment_plan_zh.md`。记录新实验时使用 `templates/experiment_log.yaml`，为每次运行指定独立输出目录，保留对应配置、数据划分和评价结果。随包 `results/` 中的数据来自合成演示，仅用于验证流程。

## 论文与 LaTeX

以下路径从 **Git 仓库根目录** 起算。

| 用途 | 路径 |
| --- | --- |
| 论文源文件 | `初稿.tex` |
| 论文模板路径 | |
