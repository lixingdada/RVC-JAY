@echo off
chcp 65001 >nul

echo.
echo ============================================
echo   RVC 临时文件清理工具
echo ============================================
echo.

set "ROOT=%~dp0"

echo [1/4] 清理 RVC 分离临时文件夹...
for /d %%p in ("%ROOT%\TEMP\rvc-pymss-*") do (
    rmdir "%%p" /s /q 2>nul
    echo   - 已删除: %%~nxp
)

echo.
echo [2/4] 清理 TEMP 里的音频文件...
for %%e in (wav mp3 flac m4a) do (
    if exist "%ROOT%\TEMP\*.%%e" (
        del /q /s "%ROOT%\TEMP\*.%%e" 2>nul
        echo   - 已删除 *.%%e
    )
)

echo.
echo [3/4] 清理 opt 里的伴奏文件(保留人声)...
if exist "%ROOT%\opt\*instrumental*" (
    del /q /s "%ROOT%\opt\*instrumental*" 2>nul
    echo   - 已删除伴奏文件
)

echo.
echo [4/4] 清空回收站...
echo Y|rd /s %systemdrive%\$Recycle.bin 2>nul
echo   回收站已清空

echo.
echo ============================================
echo   清理完成!
echo ============================================
echo.
pause
