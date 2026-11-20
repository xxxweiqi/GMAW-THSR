# 本版实际验证记录

## 1 验证范围

交付版本1.0在Python 3.12.14、PyTorch 2.6.0+cpu环境实际执行。全部随包数据与结果属于合成流程验证，没有执行附件对应的工业原始数据实验，也没有训练原始MBGN。运行细节和精确依赖版本见各run的 `run_info.json`。

## 2 已执行并通过

| 项目 | 实际执行范围 | 可追溯文件 |
| --- | --- | --- |
| 科学软件单元测试 | 59项，0失败、0错误、0跳过 | results/verification/test_summary.json与test_run.log |
| 参考完整模型 | seed 42，3 epoch，575/286/318个train/val/test样本 | results/smoke_full |
| 基线与消融 | 8组均seed 42、3 epoch；非3种子正式研究 | results/demo_suite |
| 简单固定热响应基线 | 固定滤波特征加逻辑回归，训练集拟合scaler，验证集选阈值 | results/demo_linear |
| 严格配对比较 | B0与完整模型、简单热基线与完整模型；各100次焊缝bootstrap | results/paired_snapshot_vs_full_demo.json与paired_linear_vs_full_demo.json |
| 因果延迟压力检查 | 原始帧回退0/1/2/4帧；共同310个样本；当前图像与标签不变 | results/stress_delay |
| 数据/记录模板 | 11个模板结构通过 | templates/check_templates.py |
| 一条命令入口 | 包外独立1 epoch训练和绘图成功；重复输出路径被拒绝且旧指标未改变 | run_demo.py；入口检查摘要见release_verification.json |
| Word与PDF | 16页逐页视觉检查完成，22个章节，8篇参考来源 | docs/GMAW_Experiment_Plan_v1.docx与.pdf |

单元测试覆盖原生U×I积分、完整段热状态、无未来输入、全局凸混合与梯度、有限支持、焊缝隔离、路径与文件复用、未知/未检测区域排除、事件一对一匹配、覆盖分母、部分覆盖事件、验证阈值、配对重采样及延迟检查。

## 3 演示没有证明什么

生成器人为安排了图像/信号与标签相关性。简单热滤波逻辑回归在合成测试上的帧AP为1，完整参考模型约0.967；二者的事件F1均为1。这些数值既不能用于宣传完整模型更好，也不能反推实际焊接中线性模型一定更好。它们只证明多种方法和统一评价通路能够运行。

延迟压力试验中离散分类结果没有变化，概率和AP仅有微小变化。当前图像保持不变，并且合成数据具有简单的视觉相关性，因而这个结果不能证明系统已经对真实时间错位鲁棒。两条测试合成焊缝的bootstrap区间也不属于真实工业统计证据。

尚未执行的事项包括真实原生数据导入、现场同步与RT配准、实际热校准、原MBGN改造与复现、真实三种子完整训练、嵌套留一焊缝验证、硬软标注专门对照、误报约束阈值选择、生产在线服务和新焊缝试验。实验方案逐项给出设计和边界。

## 4 本地复查

安装requirements后，可执行以下命令。完整文件校验不需要PyTorch。

```bash
python scripts/verify_integrity.py
python -m unittest discover -s tests -v
python templates/check_templates.py
python run_demo.py --out results/my_demo
```

改变配置或代码后请使用新的实验目录。合成演示结果保留为软件验收记录，真实研究结果另外保存。
