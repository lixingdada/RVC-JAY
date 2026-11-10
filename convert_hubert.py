import re
import sys
import types

import torch


class _Any:
    def __init__(self, *a, **k):
        pass

    def __call__(self, *a, **k):
        return _Any()

    def __setstate__(self, state):
        if isinstance(state, dict):
            self.__dict__.update(state)


class _StubModule(types.ModuleType):
    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return _Any


for _n in [
    "fairseq", "fairseq.data", "fairseq.data.dictionary", "fairseq.data.audio",
    "fairseq.data.audio.feature_transforms", "fairseq.dataclass",
    "fairseq.dataclass.configs", "fairseq.dataclass.utils", "fairseq.models",
    "fairseq.models.hubert", "fairseq.models.hubert.hubert", "fairseq.models.wav2vec",
    "fairseq.tasks", "fairseq.criterions", "fairseq.optim", "fairseq.optim.lr_scheduler",
    "fairseq.modules", "fairseq.logging", "fairseq.distributed",
    "omegaconf", "omegaconf.dictconfig", "omegaconf.listconfig",
]:
    sys.modules[_n] = _StubModule(_n)
    if "." in _n:
        _p, _c = _n.rsplit(".", 1)
        setattr(sys.modules[_p], _c, sys.modules[_n])

SRC = "assets/hubert_base/pytorch_model.bin"
ck = torch.load(SRC, map_location="cpu", weights_only=False)
sd = ck["model"]

out = {}
dropped = []
pos_g = pos_v = pos_b = None

for k, v in sd.items():
    if k.startswith("encoder.layers."):
        nk = k
        nk = nk.replace(".self_attn.", ".attention.")
        nk = nk.replace(".self_attn_layer_norm.", ".layer_norm.")
        nk = nk.replace(".fc1.", ".feed_forward.intermediate_dense.")
        nk = nk.replace(".fc2.", ".feed_forward.output_dense.")
        out[nk] = v
    elif k.startswith("feature_extractor.conv_layers."):
        nk = re.sub(r"(conv_layers\.\d+)\.0\.", r"\1.conv.", k)
        nk = re.sub(r"(conv_layers\.\d+)\.2\.", r"\1.layer_norm.", nk)
        out[nk] = v
    elif k == "post_extract_proj.weight":
        out["feature_projection.projection.weight"] = v
    elif k == "post_extract_proj.bias":
        out["feature_projection.projection.bias"] = v
    elif k == "encoder.pos_conv.0.weight_g":
        out["encoder.pos_conv_embed.conv.parametrizations.weight.original0"] = v
    elif k == "encoder.pos_conv.0.weight_v":
        out["encoder.pos_conv_embed.conv.parametrizations.weight.original1"] = v
    elif k == "encoder.pos_conv.0.bias":
        out["encoder.pos_conv_embed.conv.bias"] = v
    elif k == "mask_emb":
        out["masked_spec_embed"] = v
    elif k == "layer_norm.weight":
        out["feature_projection.layer_norm.weight"] = v
    elif k == "layer_norm.bias":
        out["feature_projection.layer_norm.bias"] = v
    elif k in ("final_proj.weight", "final_proj.bias", "encoder.layer_norm.weight", "encoder.layer_norm.bias"):
        out[k] = v
    else:
        dropped.append(k)

print(f"转换后参数个数: {len(out)}")
print(f"丢弃的键: {dropped}")

from transformers import HubertConfig
from infer.hubert import HubertModelWithFinalProj

cfg = HubertConfig.from_pretrained("assets/hubert_base")
model = HubertModelWithFinalProj(cfg)
msd = model.state_dict()

print(f"\ntransformers 模型参数个数: {len(msd)}")
missing = [k for k in msd if k not in out]
unexpected = [k for k in out if k not in msd]
shape_bad = [k for k in out if k in msd and out[k].shape != msd[k].shape]

print(f"缺失(模型有、转换后没有): {len(missing)}")
for k in missing:
    print("   ", k, tuple(msd[k].shape))
print(f"多余(转换后有、模型没有): {len(unexpected)}")
for k in unexpected:
    print("   ", k, tuple(out[k].shape))
print(f"形状不匹配: {len(shape_bad)}")
for k in shape_bad:
    print("   ", k, tuple(out[k].shape), "vs", tuple(msd[k].shape))

if not missing and not unexpected and not shape_bad:
    print("\n=== 映射完全匹配，正在写入 ===")
    torch.save(out, SRC)
    print(f"已覆盖写入 {SRC} ({__import__('os').path.getsize(SRC)} bytes)")
