#!/usr/bin/env python3
"""Check dependencies without downloading weights or accessing the network."""
import importlib
import json
import platform
import sys


def main():
    status = {"python": platform.python_version(), "ok": True, "packages": {}}
    for package in ["numpy", "pandas", "scipy", "sklearn", "PIL", "yaml", "torch", "matplotlib"]:
        try:
            module = importlib.import_module(package)
            status["packages"][package] = getattr(module, "__version__", "available")
        except Exception as error:
            status["ok"] = False
            status["packages"][package] = str(error)
    if status["ok"]:
        import torch
        status["cuda_available"] = torch.cuda.is_available()
    print(json.dumps(status, indent=2, ensure_ascii=False))
    return 0 if status["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
