#!/usr/bin/env python3
"""Run the bundled SYNTHETIC reference experiment and create diagnostic figures."""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(
        description="一条命令训练合成演示并绘图；演示结果不是焊接实验或原MBGN复现。"
    )
    parser.add_argument("--data", type=Path, default=ROOT / "dataset_demo", help="合成数据目录，默认使用随包dataset_demo")
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "smoke.yaml", help="配置文件，默认smoke.yaml")
    parser.add_argument("--out", type=Path, default=ROOT / "results" / "my_demo", help="新输出目录；已存在时拒绝覆盖")
    parser.add_argument("--epochs", type=int, help="可选训练轮数覆盖；须为正整数")
    parser.add_argument("--seed", type=int, help="可选训练随机种子")
    parser.add_argument("--device", choices=["cpu", "auto", "cuda"], help="可选设备覆盖；CPU无需显卡")
    args = parser.parse_args()
    data, config, out = args.data.resolve(), args.config.resolve(), args.out.resolve()
    if out.exists():
        parser.error(f"输出目录已存在，拒绝覆盖：{out}；请使用 --out 指定新目录。")
    if not (data / "manifest.csv").is_file():
        parser.error(f"缺少 {data / 'manifest.csv'}。可在项目根目录运行 python -m gmaw_phys.demo --output dataset_demo_new 生成另一组合成数据。")
    if not config.is_file():
        parser.error(f"配置文件不存在：{config}")
    if args.epochs is not None and args.epochs <= 0:
        parser.error("--epochs 必须为正整数")
    # Imports follow argument parsing: --help is available without installing torch.
    from gmaw_phys.data import validate_dataset
    from gmaw_phys.train import read_config, run_training

    qc = validate_dataset(data)
    if not qc.get("ok"):
        parser.error("演示数据校验失败：" + "; ".join(qc.get("errors", [])))
    if qc.get("synthetic") is not True:
        parser.error("run_demo只接受全部标记为synthetic的演示数据；真实数据请使用 scripts/run_experiment.py 与research配置。")
    cfg = read_config(config)
    if args.epochs is not None:
        cfg["train"]["epochs"] = args.epochs
    if args.seed is not None:
        cfg["seed"] = args.seed
    if args.device is not None:
        cfg["train"]["device"] = args.device
    print("SYNTHETIC_PIPELINE_ONLY：以下只验证软件流程，不构成真实焊接性能证据。", flush=True)
    run_training(data, cfg, out)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "plot_results.py"), "--run", str(out)], check=True, cwd=ROOT)
    print(f"演示完成：{out}", flush=True)
    print(f"预测图：{out / 'prediction_diagnostic.png'}", flush=True)
    print(f"测试指标：{out / 'metrics_test.json'}", flush=True)


if __name__ == "__main__":
    main()
