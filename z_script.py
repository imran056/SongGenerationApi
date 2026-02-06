from hmac import new
import sys
import os
import argparse
from safetensors.torch import save_file

import time
import json
import torch
import torchaudio
import numpy as np
from omegaconf import OmegaConf
from codeclm.models import builders
import gc
from codeclm.trainer.codec_song_pl import CodecLM_PL
from codeclm.models import CodecLM
from third_party.demucs.models.pretrained import get_model_from_yaml

cfg_path = "/apdcephfs_cq11/share_300883980/tanwei/SongGeneration-LeVo/ckpt/songgeneration_base/config.yaml"
cfg = OmegaConf.load(cfg_path)
cfg.mode = 'inference'
# audio_tokenizer = builders.get_audio_tokenizer_model(cfg.audio_tokenizer_checkpoint, cfg)
# model = audio_tokenizer.model.model
# weights = {k: v.half() for k, v in model.state_dict().items() if isinstance(v, torch.Tensor) and v.numel() > 0}
# save_file(weights, '/apdcephfs_cq11/share_300883980/tanwei/SongGeneration-LeVo/ckpt/encoder_fp16.safetensors')
# print(weights)

# seperate_tokenizer = builders.get_audio_tokenizer_model(cfg.audio_tokenizer_checkpoint_sep, cfg)
# model = seperate_tokenizer.model.model
# weights = {}
# for k, v in model.state_dict().items():
#     if k.startswith("rvq_bestrq_bgm_emb") or k.startswith("rvq_bestrq_emb") or k.startswith("bestrq"):
#         weights[k] = v.half()
#     else:
#         weights[k] = v
# # weights = {k: v.half() for k, v in model.state_dict().items() if isinstance(v, torch.Tensor) and v.numel() > 0}
# save_file(weights, '/apdcephfs_cq11/share_300883980/tanwei/SongGeneration-LeVo/ckpt/encoder_fp16.safetensors')
# print(weights.keys())

ckpt_path = "/apdcephfs_cq11/share_300883980/tanwei/SongGeneration-WX/ckpt/songgeneration_new_small/model_32.pt"
# audiolm = builders.get_lm_model(cfg)
checkpoint = torch.load(ckpt_path, map_location='cpu')
audiolm_state_dict = {k: v.half() for k, v in checkpoint.items()}
torch.save(audiolm_state_dict, "/apdcephfs_cq11/share_300883980/tanwei/SongGeneration-WX/ckpt/songgeneration_new_small/model.pt")
