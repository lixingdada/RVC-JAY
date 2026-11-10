import os
import sys
import numpy as np
from scipy.io import wavfile

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")
os.environ.setdefault("weight_root", "assets/weights")
os.environ.setdefault("weight_pymss_root", "assets/pymss_weights")
os.environ.setdefault("index_root", "logs")
os.environ.setdefault("outside_index_root", "assets/indices")
os.environ.setdefault("rmvpe_root", "assets/rmvpe")

from configs.config import Config
from infer.vc.modules import VC

SR = 16000
DUR = 4.0
TEST_IN = "smoke_input.wav"
TEST_OUT = "smoke_output.wav"

t = np.linspace(0, DUR, int(SR * DUR), endpoint=False)
f0 = 140.0 + 25.0 * np.sin(2 * np.pi * 0.7 * t)
phase = 2 * np.pi * np.cumsum(f0) / SR
sig = np.zeros_like(phase)
for k, amp in zip(range(1, 13), [1.0, 0.5, 0.33, 0.25, 0.2, 0.16, 0.13, 0.11, 0.09, 0.07, 0.05, 0.04]):
    sig += amp * np.sin(k * phase)
env = 0.6 + 0.4 * np.sin(2 * np.pi * 3.0 * t)
sig = sig * env
sig = sig / np.abs(sig).max() * 0.7
wavfile.write(TEST_IN, SR, (sig * 32767).astype(np.int16))
print(f"[1/4] 测试音频已生成: {TEST_IN} ({os.path.getsize(TEST_IN)} bytes)")

print("[2/4] 初始化 VC ...")
config = Config()
print(f"      device={config.device} is_half={config.is_half} gpu={config.gpu_name}")
vc = VC(config)

sid = "singer.pth"
print(f"[3/4] 加载模型 sid={sid} ...")
vc.get_vc(sid)
print(f"      net_g 已加载: {vc.net_g is not None}")
print(f"      hubert 已加载: {vc.hubert_model is not None}")
print(f"      version={vc.version} if_f0={vc.if_f0} tgt_sr={vc.tgt_sr} n_spk={vc.n_spk}")

SPK_ID = 0
print(f"[4/4] 执行推理 (说话人 id={SPK_ID}) ...")
info, (sr_out, audio_out) = vc.vc_single(
    sid=SPK_ID,
    input_audio_path=TEST_IN,
    f0_up_key=0,
    f0_method="rmvpe",
    file_index="assets/indices/singer_added_IVF256_Flat_nprobe_1_singer_v2.index",
    index_rate=0.75,
    resample_sr=0,
    rms_mix_rate=0.25,
    protect=0.33,
)
print(f"      推理信息: {info}")
print(f"      输出采样率: {sr_out}")
print(f"      输出长度: {len(audio_out)} samples ({len(audio_out)/sr_out:.2f} 秒)")
peak = float(np.abs(audio_out).max())
print(f"      输出峰值: {peak:.4f}")
assert len(audio_out) > 0, "输出为空"
assert peak > 1e-4, "输出近乎静音"
print(f"\n=== 冒烟测试通过，输出已写入 {TEST_OUT} ===")
wavfile.write(TEST_OUT, sr_out, (audio_out * 32767).astype(np.int16))
