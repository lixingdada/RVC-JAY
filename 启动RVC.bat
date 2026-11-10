@echo off
chcp 65001 >nul
title RVC WebUI

:: 自动切换到脚本所在目录，不再硬编码 D 盘路径
cd /d "%~dp0"

:: 让 ffmpeg.exe / ffprobe.exe 对 gradio(pydub) 等子进程可见
:: 缺 ffprobe 时上传 mp3/m4a/flac 会报 UnboundLocalError
set PATH=%~dp0;%PATH%

:: 关键修复:解决 train/preprocess.py 子进程的循环导入
:: 1. PYTHONSAFEPATH=1 禁止把脚本目录 train/ 加到 sys.path
:: 2. PYTHONPATH 指向项目根,让 train 解析为包而非 train.py 文件
set PYTHONSAFEPATH=1
set PYTHONPATH=%~dp0

call .venv\Scripts\activate
python webui.py

pause
