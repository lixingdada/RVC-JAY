"""端到端验证：用用户报错的 model_bs_roformer_ep_368 跑一次真实人声分离。
完全复刻 tools/pymss_webui.py 第 330-352 行的调用参数。"""

import os
import sys
import time
from pathlib import Path

os.environ.setdefault("weight_pymss_root", "assets/pymss_weights")

import torch
from pymss import MSSeparator

AUDIO_PARAMS = {
    "wav_bit_depth": "FLOAT",
    "flac_bit_depth": "PCM_24",
    "mp3_bit_rate": "320k",
    "m4a_bit_rate": "320k",
    "m4a_codec": "aac",
    "m4a_aac_at_quality": 2,
}

MODEL_FILE = "model_bs_roformer_ep_368_sdr_12.9628.ckpt"
CONFIG_FILE = "model_bs_roformer_ep_368_sdr_12.9628.yaml"
model_path = str(Path("assets/pymss_weights") / MODEL_FILE)
config_path = str(Path("assets/pymss_weights") / CONFIG_FILE)

assert os.path.isfile(model_path), f"权重缺失: {model_path}"
assert os.path.isfile(config_path), f"配置缺失: {config_path}"

print(f"[1/3] 加载模型 {MODEL_FILE}")
t0 = time.time()
sep = MSSeparator(
    model_type="bs_roformer",
    model_path=model_path,
    config_path=config_path,
    device="cuda",
    device_ids=[0],
    output_format="wav",
    use_tta=False,
    store_dirs={},
    audio_params=AUDIO_PARAMS,
    debug=False,
    inference_params={
        "batch_size": 1,
        "chunk_size": 352800,
        "overlap_size": 264600,
        "standardize": False,
        "normalize": False,
        "use_amp": True,
        "model_dtype": "auto",
        "cuda_attention_backend": "default",
    },
)
print(f"      加载完成，耗时 {time.time() - t0:.1f}s")
print(f"      CUDA 可用: {torch.cuda.is_available()}  设备: {torch.cuda.get_device_name(0)}")

print("[2/3] 执行分离 (6 秒测试音频)")
t0 = time.time()
results = sep.separate("opt/pymss_test/test_mix.wav", pbar=False)
print(f"      分离完成，耗时 {time.time() - t0:.1f}s")

print("[3/3] 检查输出")
ok = True
for r in results:
    p = r[0] if isinstance(r, (tuple, list)) else r
    exists = os.path.isfile(p)
    size = os.path.getsize(p) if exists else 0
    print(f"      {'[OK]' if exists and size > 1024 else '[失败]'} {p}  {size} bytes")
    if not (exists and size > 1024):
        ok = False

print()
print("结论: 去伴奏模型端到端验证通过" if ok else "结论: 分离输出异常，需排查")
sys.exit(0 if ok else 1)
