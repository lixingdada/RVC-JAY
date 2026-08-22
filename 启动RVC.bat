@echo off
chcp 65001 >nul
title RVC WebUI

d:
cd \Retrieval-based-Voice-Conversion-WebUI

:: 关键修复:解决 train/preprocess.py 子进程的循环导入
:: 1. PYTHONSAFEPATH=1 禁止把脚本目录 train/ 加到 sys.path
:: 2. PYTHONPATH 指向项目根,让 train 解析为包而非 train.py 文件
set PYTHONSAFEPATH=1
set PYTHONPATH=D:\Retrieval-based-Voice-Conversion-WebUI

call .venv\Scripts\activate
python webui.py

pause
