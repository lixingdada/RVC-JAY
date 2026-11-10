@echo off
setlocal
set "ROOT=%~dp0"

echo.
echo ==============================================
echo   Cleanup: vocal separation / dereverb
echo   KEEP : *_noreverb  *_vocals  *_main_vocal
echo   DEL  : *_reverb  *_instrumental  *_off_vocal
echo   DEL  : TEMP audio files
echo ==============================================
echo.

echo [1/3] Delete reverb / instrumental / off_vocal...
del /q "%ROOT%opt\*_reverb.*" 2>nul
del /q "%ROOT%opt\*_instrumental.*" 2>nul
del /q "%ROOT%opt\*_off_vocal.*" 2>nul
echo        done

echo [2/3] Delete TEMP audio files...
del /q "%ROOT%TEMP\*.wav" 2>nul
del /q "%ROOT%TEMP\*.mp3" 2>nul
del /q "%ROOT%TEMP\*.flac" 2>nul
del /q "%ROOT%TEMP\*.m4a" 2>nul
del /q "%ROOT%TEMP\*.ogg" 2>nul
echo        done

echo [3/3] Delete TEMP temp folders...
for /d %%d in ("%ROOT%TEMP\rvc-pymss-*") do rmdir "%%d" /s /q 2>nul
echo        done

echo.
echo ==============================================
echo   Cleanup finished.
echo   Your *_noreverb files in opt are KEPT.
echo ==============================================
echo.
pause
