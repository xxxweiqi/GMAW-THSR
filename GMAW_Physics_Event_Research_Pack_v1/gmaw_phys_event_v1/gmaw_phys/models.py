"""Small executable reference networks, NOT the published MBGN implementation.

All models read causal electrical inputs and the current available image. The
future geometry tensor is never accessed by a model; it is an optional training
target handled by the trainer. No pretrained weights are downloaded.
"""

from __future__ import annotations

import math
import torch
from torch import nn


MODEL_NAMES = ("snapshot_fusion", "history_gru", "power_features", "thermal_filter", "phys_align")


class ElectricalEncoder(nn.Module):
    def __init__(self, embed_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(2, 12, 9, stride=4, padding=4),
            nn.GroupNorm(3, 12), nn.SiLU(),
            nn.Conv1d(12, 24, 7, stride=4, padding=3),
            nn.GroupNorm(4, 24), nn.SiLU(),
            nn.Conv1d(24, 32, 5, stride=4, padding=2),
            nn.GroupNorm(4, 32), nn.SiLU(), nn.AdaptiveAvgPool1d(1),
        )
        self.project = nn.Linear(32, embed_dim)

    def forward(self, x):
        return self.project(self.net(x).squeeze(-1))


class ImageEncoder(nn.Module):
    def __init__(self, embed_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(3, 12, 5, stride=2, padding=2),
            nn.GroupNorm(3, 12), nn.SiLU(),
            nn.Conv2d(12, 24, 3, stride=2, padding=1),
            nn.GroupNorm(4, 24), nn.SiLU(),
            nn.Conv2d(24, 32, 3, stride=2, padding=1),
            nn.GroupNorm(4, 32), nn.SiLU(), nn.AdaptiveAvgPool2d(1),
        )
        self.project = nn.Linear(32, embed_dim)

    def forward(self, x):
        return self.project(self.net(x).flatten(1))


class ReferenceFusionModel(nn.Module):
    """Five reference variants with explicit heat/alignment/auxiliary flags.

    snapshot_fusion: current waveform + current image.
    history_gru: unidirectional electrical-history GRU + current image.
    power_features: content attention over electrical + mean-power history.
    thermal_filter: same attention with a fixed-filter thermal feature.
    phys_align: same attention, plus geometry log-prior and hard support.

    The three attention variants share the same token architecture. Their
    keys/values are pointwise functions of electrical/power/thermal features,
    not recurrent features, so a masked electrical token cannot enter through
    a later GRU state. Thermal features intentionally retain full-segment past
    heat history, as required by the dissipative model.
    """
    def __init__(self, cfg):
        super().__init__()
        model_cfg = cfg.get("model", {})
        data_cfg = cfg.get("data", {})
        self.name = model_cfg.get("name", "phys_align")
        if self.name not in MODEL_NAMES:
            raise ValueError(f"Unknown model {self.name!r}; choose from {MODEL_NAMES}")
        self.use_heat = bool(model_cfg.get("use_heat", self.name in ("thermal_filter", "phys_align")))
        self.use_alignment = bool(model_cfg.get("use_alignment", self.name == "phys_align"))
        self.use_aux = bool(model_cfg.get("use_aux", False))
        self.is_attention = self.name in ("power_features", "thermal_filter", "phys_align")
        if self.use_alignment and not self.is_attention:
            raise ValueError("use_alignment requires an attention variant; set baseline flags explicitly")
        self.use_power = self.is_attention
        hidden = int(model_cfg.get("hidden_dim", 64))
        embed = int(model_cfg.get("embed_dim", max(16, hidden // 2)))
        dropout = float(model_cfg.get("dropout", 0.1))
        if hidden < 4 or embed < 4 or not 0 <= dropout < 1:
            raise ValueError("hidden_dim/embed_dim must be >=4; dropout must lie in [0,1)")
        self.electrical_encoder = ElectricalEncoder(embed)
        self.image_encoder = ImageEncoder(embed)
        if self.use_heat:
            taus = data_cfg.get("thermal_taus_s", [0.15, 0.35, 0.75])
            if len(taus) == 0 or any(not math.isfinite(float(t)) or float(t) <= 0 for t in taus):
                raise ValueError("data.thermal_taus_s must contain finite positive fixed constants")
            self.register_buffer("thermal_taus_s", torch.as_tensor(taus, dtype=torch.float32))
            # One GLOBAL convex mixture. There are no per-window heat efficiencies
            # or free state scales that could cancel the physical constraint.
            self.thermal_logits = nn.Parameter(torch.zeros(len(taus)))
        else:
            self.register_buffer("thermal_taus_s", torch.empty(0))
            self.register_parameter("thermal_logits", None)
        token_dim = embed + 2 + int(self.use_power) + int(self.use_heat)
        self.token_projection = nn.Sequential(nn.Linear(token_dim, hidden), nn.SiLU())
        if self.name == "history_gru":
            self.gru = nn.GRU(hidden, hidden, batch_first=True, bidirectional=False)
        if self.is_attention:
            self.query_projection = nn.Linear(embed + 2, hidden)
            self.key_projection = nn.Linear(hidden, hidden)
            self.value_projection = nn.Linear(hidden, hidden)
        self.fusion = nn.Sequential(
            nn.Linear(hidden + embed + 2, hidden), nn.SiLU(), nn.Dropout(dropout)
        )
        self.classifier = nn.Linear(hidden, 1)
        self.geometry_head = nn.Linear(hidden, 3) if self.use_aux else None
        self.attention_scale = hidden ** -0.5

    def thermal_weights(self):
        """Global nonnegative weights summing to one, or an empty tensor."""
        if self.thermal_logits is None:
            return self.thermal_taus_s
        return torch.softmax(self.thermal_logits, dim=0)

    def forward(self, batch):
        # Deliberately do not iterate over/concatenate batch fields: labels,
        # future geometry, RT event positions, and metadata are never inputs.
        signal, images, condition = batch["signal"], batch["image"], batch["condition"]
        if signal.ndim != 4 or signal.shape[2] != 2:
            raise ValueError("signal must have shape [B,L,2,N]")
        b, length, _, n = signal.shape
        if length < 1 or images.ndim != 5 or images.shape[:2] != (b, length) or images.shape[2] != 3:
            raise ValueError("image must have shape [B,L,3,H,W] with the same nonempty history")
        if condition.shape != (b, 2):
            raise ValueError("condition must have shape [B,2]")
        current_image = self.image_encoder(images[:, -1])
        if self.name == "snapshot_fusion":
            electrical = self.electrical_encoder(signal[:, -1]).unsqueeze(1)
            token_length = 1
        else:
            electrical = self.electrical_encoder(signal.reshape(b * length, 2, n)).reshape(b, length, -1)
            token_length = length
        pieces = [electrical, condition.unsqueeze(1).expand(-1, token_length, -1)]
        result = {}
        if self.use_power:
            if batch["power"].shape != (b, length, 1):
                raise ValueError("power must have shape [B,L,1]")
            pieces.append(batch["power"])
        if self.use_heat:
            thermal = batch["thermal"]
            if thermal.shape != (b, length, self.thermal_logits.numel()):
                raise ValueError("thermal shape must agree with data.thermal_taus_s")
            mixed = (thermal * self.thermal_weights().view(1, 1, -1)).sum(dim=-1, keepdim=True)
            result["thermal_mix"] = mixed
            pieces.append(mixed[:, -1:] if self.name == "snapshot_fusion" else mixed)
        tokens = self.token_projection(torch.cat(pieces, dim=-1))
        if self.name == "history_gru":
            _, last = self.gru(tokens)
            context = last[-1]
        elif self.is_attention:
            query = self.query_projection(torch.cat((current_image, condition), dim=-1))
            scores = (self.key_projection(tokens) * query.unsqueeze(1)).sum(dim=-1) * self.attention_scale
            if self.use_alignment:
                mask = batch["alignment_mask"].to(dtype=torch.bool)
                prior = batch["alignment_prior"]
                if mask.shape != (b, length) or prior.shape != (b, length):
                    raise ValueError("alignment tensors must have shape [B,L]")
                if not bool(mask.any(dim=1).all()):
                    raise ValueError("Every sample needs physical support; skip unsupported samples in the loader")
                if not bool(torch.isfinite(prior).all()) or bool((prior < 0).any()):
                    raise ValueError("alignment_prior must be finite and nonnegative")
                if bool((prior.masked_fill(~mask, 0).sum(dim=1) <= 0).any()):
                    raise ValueError("alignment_prior must have positive mass on valid support")
                scores = scores + torch.log(prior.clamp_min(torch.finfo(scores.dtype).tiny))
                scores = scores.masked_fill(~mask, -torch.inf)
            attention = torch.softmax(scores, dim=1)
            if self.use_alignment:
                attention = attention.masked_fill(~mask, 0.0)  # exact zeros, also in exported diagnostics
            result["attention"] = attention
            context = (self.value_projection(tokens) * attention.unsqueeze(-1)).sum(dim=1)
        else:
            context = tokens[:, -1]
        fused = self.fusion(torch.cat((context, current_image, condition), dim=-1))
        result["logits"] = self.classifier(fused).squeeze(-1)
        result["geom_pred"] = torch.sigmoid(self.geometry_head(fused)) if self.geometry_head is not None else fused.new_zeros((b, 3))
        return result


def build_model(cfg):
    """Build a model without fetching any external assets."""
    return ReferenceFusionModel(cfg)
