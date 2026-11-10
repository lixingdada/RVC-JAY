# -*- coding: utf-8 -*-
"""
RVC 训练数据清洗 —— 第一阶段（切片前，对完整干声）

策略：保守、可复现、不伤音色（不做激进降噪，避免引入金属感）
  1. 高通滤波 50 Hz：去除直流偏移与低频隆隆声（人声基频 > 80 Hz，绝对安全）
  2. 响度归一：RMS 统一到 -18 dBFS，消除 20 首歌之间的音量差异
  3. 防削波：整体衰减使 peak 不超过 -1 dBFS（修复几首 peak > 0 的削波隐患）

输入：C:\\Users\\21704\\Music\\干净原声\\*.wav （只读，不改原文件）
输出：C:\\Users\\21704\\Music\\干净原声_清洗后\\ （新目录）

说明：呼吸声属于真实演唱的一部分，训练数据中保留是正确的；
      真正的"呼吸声杂音"来自推理输入源音频，在推理阶段处理，不在本脚本范围。
"""
import os
import glob
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfiltfilt

SRC = r"C:\Users\21704\Music\干净原声"
DST = r"C:\Users\21704\Music\干净原声_清洗后"

TARGET_RMS_DB = -18.0   # 目标响度（RMS，dBFS）
HP_FC = 50.0            # 高通截止频率（Hz）
PEAK_LIMIT_DB = -1.0    # 峰值上限（dBFS）


def highpass(sig, sr, fc):
    sos = butter(4, fc, btype="highpass", fs=sr, output="sos")
    return sosfiltfilt(sos, sig, axis=0)


def process(path):
    x, sr = sf.read(path, always_2d=True)  # shape (n_samples, n_channels)
    x = x.astype(np.float64)

    # 1. 高通去低频
    x = highpass(x, sr, HP_FC)

    # 2. 响度归一（整段同一增益，保持立体声平衡）
    rms = float(np.sqrt(np.mean(x ** 2)))
    if rms > 1e-8:
        target = 10 ** (TARGET_RMS_DB / 20)
        x = x * (target / rms)

    # 3. 防削波
    peak = float(np.max(np.abs(x)))
    limit = 10 ** (PEAK_LIMIT_DB / 20)
    if peak > limit:
        x = x * (limit / peak)

    return x, sr


def main():
    os.makedirs(DST, exist_ok=True)
    files = sorted(glob.glob(os.path.join(SRC, "*.wav")))
    if not files:
        print("未找到源文件：", SRC)
        return
    print(f"待处理 {len(files)} 首，输出到：{DST}\n")
    for i, f in enumerate(files, 1):
        name = os.path.basename(f)
        x, sr = process(f)
        out = os.path.join(DST, name)
        sf.write(out, x.astype(np.float32), sr, subtype="FLOAT")
        rms = 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)
        peak = 20 * np.log10(np.max(np.abs(x)) + 1e-9)
        print(f"[{i:2d}/{len(files)}] {name[:26]:26s} -> RMS {rms:5.1f} dB  Peak {peak:5.1f} dB")
    print(f"\n全部完成，共 {len(files)} 首，输出目录：{DST}")


if __name__ == "__main__":
    main()
