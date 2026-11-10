# -*- coding: utf-8 -*-
"""
扫描 RVC 训练切片，统计静音/爆音/超短片段分布，并剔除坏片段。
确定性纯函数：只读文件、按显式规则计算指标，不依赖运行时 AI 推断。

用法：
  python tools/scan_slices.py                 # 只扫描并输出报告（dry-run，不改动任何文件）
  python tools/scan_slices.py --apply         # 把坏片段的 wav 移出 0_gt_wavs 和 1_16k_wavs

说明：RVC 的 filelist.txt 在点击「训练」时自动重建（取 0_gt_wavs/特征/f0 四目录交集），
因此正确剔除方式是直接移走坏片段的 wav 文件，让「特征提取」与「训练」自动跳过它们。
被移走的 wav 统一放到 logs/<实验名>/bad_slices/ 备份，可随时恢复，不真正删除。

阈值（保守，只删明显坏片段）：
  SILENCE_DB  = -45.0   # RMS 低于此值视为近静音（整片几乎无人声）
  PEAK_MAX    = 0.98    # peak 高于此值视为异常爆音（切片归一化后正常峰值 <= 0.925）
  MIN_DUR     = 1.2     # 时长低于此秒数视为碎尾
"""
import os
import sys
import glob
import shutil

import numpy as np
import soundfile as sf

EXP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "singer")
WAV_DIR = os.path.join(EXP_DIR, "0_gt_wavs")
WAV16_DIR = os.path.join(EXP_DIR, "1_16k_wavs")
BAD_DIR = os.path.join(EXP_DIR, "bad_slices")

SILENCE_DB = -45.0
PEAK_MAX = 0.98
MIN_DUR = 1.2


def measure(path):
    """返回 (rms_db, peak, dur)。转单声道后计算。"""
    x, sr = sf.read(path, always_2d=False)
    if x.ndim > 1:
        x = x.mean(axis=1)
    x = x.astype(np.float64)
    rms = float(np.sqrt(np.mean(x ** 2)))
    rms_db = 20.0 * np.log10(rms + 1e-9)
    peak = float(np.max(np.abs(x)))
    dur = float(len(x) / sr)
    return rms_db, peak, dur


def main():
    apply = "--apply" in sys.argv
    files = sorted(glob.glob(os.path.join(WAV_DIR, "*.wav")))
    if not files:
        print("[扫描] 未找到切片文件：%s" % WAV_DIR)
        return 1

    rows = []
    bad = []  # (basename, reason)
    for f in files:
        base = os.path.basename(f)
        rms_db, peak, dur = measure(f)
        rows.append((base, rms_db, peak, dur))
        reason = None
        if rms_db < SILENCE_DB:
            reason = "静音(%.1f dBFS)" % rms_db
        elif peak > PEAK_MAX:
            reason = "爆音(peak=%.3f)" % peak
        elif dur < MIN_DUR:
            reason = "超短(%.2fs)" % dur
        if reason:
            bad.append((base, reason))

    rms_arr = np.array([r[1] for r in rows])
    peak_arr = np.array([r[2] for r in rows])
    dur_arr = np.array([r[3] for r in rows])

    print("=" * 60)
    print("切片扫描报告  目录: %s" % WAV_DIR)
    print("=" * 60)
    print("总数: %d 片" % len(rows))
    print("-" * 60)
    print("RMS (dBFS)   min=%.1f  5%%=%.1f  50%%=%.1f  95%%=%.1f  max=%.1f"
          % (rms_arr.min(), np.percentile(rms_arr, 5), np.percentile(rms_arr, 50),
             np.percentile(rms_arr, 95), rms_arr.max()))
    print("Peak         min=%.3f  50%%=%.3f  95%%=%.3f  max=%.3f"
          % (peak_arr.min(), np.percentile(peak_arr, 50), np.percentile(peak_arr, 95), peak_arr.max()))
    print("时长(s)      min=%.2f  50%%=%.2f  max=%.2f"
          % (dur_arr.min(), np.percentile(dur_arr, 50), dur_arr.max()))
    print("-" * 60)
    print("坏片段候选（按阈值 静音<%.0f dB / 爆音>%.2f / 超短<%.1fs）: %d 片"
          % (SILENCE_DB, PEAK_MAX, MIN_DUR, len(bad)))
    for base, reason in bad:
        print("  - %-20s %s" % (base, reason))

    if not apply:
        print("-" * 60)
        print("[dry-run] 未改动任何文件。确认阈值后加 --apply 执行剔除。")
        return 0

    # 执行剔除：把坏片段 wav 从 0_gt_wavs 和 1_16k_wavs 移到 bad_slices/
    os.makedirs(BAD_DIR, exist_ok=True)
    moved = []
    for base, reason in bad:
        for src_dir in (WAV_DIR, WAV16_DIR):
            src = os.path.join(src_dir, base)
            if os.path.exists(src):
                shutil.move(src, os.path.join(BAD_DIR, base))
        moved.append(base)

    print("-" * 60)
    print("[剔除] 完成。坏片段已移出训练目录，统一备份到：%s" % BAD_DIR)
    print("[剔除] 原切片数: %d | 移走坏片段: %d | 剩余: %d"
          % (len(rows), len(moved), len(rows) - len(moved)))
    print("[剔除] 已同时处理 0_gt_wavs(40k) 与 1_16k_wavs(16k)；未真正删除，可手动移回复原。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
