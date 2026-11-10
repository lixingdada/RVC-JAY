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


_MODS = [
    "fairseq",
    "fairseq.data",
    "fairseq.data.dictionary",
    "fairseq.data.audio",
    "fairseq.data.audio.feature_transforms",
    "fairseq.data.audio.speech_to_text_dataset",
    "fairseq.dataclass",
    "fairseq.dataclass.configs",
    "fairseq.dataclass.utils",
    "fairseq.models",
    "fairseq.models.hubert",
    "fairseq.models.hubert.hubert",
    "fairseq.models.wav2vec",
    "fairseq.tasks",
    "fairseq.criterions",
    "fairseq.optim",
    "fairseq.optim.lr_scheduler",
    "fairseq.modules",
    "fairseq.logging",
    "fairseq.distributed",
    "omegaconf",
    "omegaconf.dictconfig",
    "omegaconf.listconfig",
]
for name in _MODS:
    m = _StubModule(name)
    sys.modules[name] = m
    if "." in name:
        parent, child = name.rsplit(".", 1)
        setattr(sys.modules[parent], child, m)

ck = torch.load("assets/hubert_base/pytorch_model.bin", map_location="cpu", weights_only=False)
print("顶层类型:", type(ck).__name__)
if isinstance(ck, dict):
    print("顶层键:", list(ck.keys()))
sd = ck["model"] if isinstance(ck, dict) and "model" in ck else ck
print()
print("state_dict 参数个数:", len(sd))
print("--- 全部键名 ---")
for k in sd.keys():
    v = sd[k]
    shape = tuple(v.shape) if hasattr(v, "shape") else type(v).__name__
    print(f"  {k}  {shape}")
