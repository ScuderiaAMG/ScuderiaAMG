#!/usr/bin/env python3
"""
从零手写 Transformer —— 使用 PyTorch
涵盖：Multi-Head Self-Attention、Positional Encoding、Feed-Forward、
      Encoder/Decoder、LayerNorm、GPT 风格的自回归语言模型
完整实现，包含训练和推理
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Any


# ============================================================
# §1  Scaled Dot-Product Attention
# ============================================================

def scaled_dot_product_attention(
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    mask: torch.Tensor | None = None,
    dropout: nn.Dropout | None = None,
) -> torch.Tensor:
    """
    Q, K, V: (batch, num_heads, seq_len, d_k)
    返回: (batch, num_heads, seq_len, d_k)
    """
    d_k = query.size(-1)
    scores = torch.matmul(query, key.transpose(-2, -1)) / math.sqrt(d_k)

    if mask is not None:
        scores = scores.masked_fill(mask == 0, float("-inf"))

    attention_weights = F.softmax(scores, dim=-1)

    if dropout is not None:
        attention_weights = dropout(attention_weights)

    return torch.matmul(attention_weights, value)


# ============================================================
# §2  Multi-Head Attention
# ============================================================

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model: int = 512, num_heads: int = 8,
                 dropout: float = 0.1) -> None:
        super().__init__()
        assert d_model % num_heads == 0, "d_model 必须能被 num_heads 整除"

        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads

        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)

        self.dropout = nn.Dropout(dropout)

    def split_heads(self, x: torch.Tensor) -> torch.Tensor:
        """(batch, seq_len, d_model) -> (batch, num_heads, seq_len, d_k)"""
        batch_size, seq_len, _ = x.size()
        return x.view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)

    def combine_heads(self, x: torch.Tensor) -> torch.Tensor:
        """(batch, num_heads, seq_len, d_k) -> (batch, seq_len, d_model)"""
        batch_size, _, seq_len, _ = x.size()
        return x.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)

    def forward(self, query: torch.Tensor, key: torch.Tensor,
                value: torch.Tensor, mask: torch.Tensor | None = None) -> torch.Tensor:
        Q = self.split_heads(self.W_q(query))
        K = self.split_heads(self.W_k(key))
        V = self.split_heads(self.W_v(value))

        attn_output = scaled_dot_product_attention(Q, K, V, mask, self.dropout)
        output = self.W_o(self.combine_heads(attn_output))
        return output


# ============================================================
# §3  Positional Encoding
# ============================================================

class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int = 512, max_len: int = 5000,
                 dropout: float = 0.1) -> None:
        super().__init__()
        self.dropout = nn.Dropout(dropout)

        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len).unsqueeze(1).float()
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)                     # (1, max_len, d_model)
        self.register_buffer("pe", pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (batch, seq_len, d_model)
        返回: x + positional encoding
        """
        seq_len = x.size(1)
        return self.dropout(x + self.pe[:, :seq_len])


# ============================================================
# §4  Feed-Forward Network
# ============================================================

class FeedForward(nn.Module):
    def __init__(self, d_model: int = 512, d_ff: int = 2048,
                 dropout: float = 0.1, activation: str = "gelu") -> None:
        super().__init__()
        act_cls = nn.GELU if activation == "gelu" else nn.ReLU
        self.net = nn.Sequential(
            nn.Linear(d_model, d_ff),
            act_cls(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
            nn.Dropout(dropout),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


# ============================================================
# §5  Encoder Layer & Encoder
# ============================================================

class EncoderLayer(nn.Module):
    def __init__(self, d_model: int = 512, num_heads: int = 8,
                 d_ff: int = 2048, dropout: float = 0.1) -> None:
        super().__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.feed_forward = FeedForward(d_model, d_ff, dropout)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor,
                mask: torch.Tensor | None = None) -> torch.Tensor:
        # Self-attention + Residual + Norm
        attn_out = self.self_attn(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_out))

        # FFN + Residual + Norm
        ff_out = self.feed_forward(x)
        x = self.norm2(x + ff_out)
        return x


class Encoder(nn.Module):
    def __init__(self, vocab_size: int, d_model: int = 512,
                 num_heads: int = 8, num_layers: int = 6,
                 d_ff: int = 2048, max_len: int = 5000,
                 dropout: float = 0.1) -> None:
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoding = PositionalEncoding(d_model, max_len, dropout)
        self.layers = nn.ModuleList([
            EncoderLayer(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])
        self.norm = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor,
                mask: torch.Tensor | None = None) -> torch.Tensor:
        x = self.embedding(x) * math.sqrt(x.size(-1))   # 缩放嵌入
        x = self.pos_encoding(x)
        for layer in self.layers:
            x = layer(x, mask)
        return self.norm(x)


# ============================================================
# §6  Decoder Layer & Decoder
# ============================================================

class DecoderLayer(nn.Module):
    def __init__(self, d_model: int = 512, num_heads: int = 8,
                 d_ff: int = 2048, dropout: float = 0.1) -> None:
        super().__init__()
        self.self_attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.cross_attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.feed_forward = FeedForward(d_model, d_ff, dropout)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.norm3 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, encoder_output: torch.Tensor,
                src_mask: torch.Tensor | None = None,
                tgt_mask: torch.Tensor | None = None) -> torch.Tensor:
        # Masked self-attention
        attn_out = self.self_attn(x, x, x, tgt_mask)
        x = self.norm1(x + self.dropout(attn_out))

        # Cross-attention
        cross_out = self.cross_attn(x, encoder_output, encoder_output, src_mask)
        x = self.norm2(x + self.dropout(cross_out))

        # FFN
        ff_out = self.feed_forward(x)
        x = self.norm3(x + ff_out)
        return x


class Decoder(nn.Module):
    def __init__(self, vocab_size: int, d_model: int = 512,
                 num_heads: int = 8, num_layers: int = 6,
                 d_ff: int = 2048, max_len: int = 5000,
                 dropout: float = 0.1) -> None:
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoding = PositionalEncoding(d_model, max_len, dropout)
        self.layers = nn.ModuleList([
            DecoderLayer(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])
        self.norm = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, encoder_output: torch.Tensor,
                src_mask: torch.Tensor | None = None,
                tgt_mask: torch.Tensor | None = None) -> torch.Tensor:
        x = self.embedding(x) * math.sqrt(x.size(-1))
        x = self.pos_encoding(x)
        for layer in self.layers:
            x = layer(x, encoder_output, src_mask, tgt_mask)
        return self.norm(x)


# ============================================================
# §7  Full Transformer
# ============================================================

class Transformer(nn.Module):
    """完整的 Encoder-Decoder Transformer (如原始论文)。"""

    def __init__(self, src_vocab_size: int, tgt_vocab_size: int,
                 d_model: int = 512, num_heads: int = 8,
                 num_encoder_layers: int = 6, num_decoder_layers: int = 6,
                 d_ff: int = 2048, max_len: int = 5000,
                 dropout: float = 0.1) -> None:
        super().__init__()
        self.encoder = Encoder(src_vocab_size, d_model, num_heads,
                               num_encoder_layers, d_ff, max_len, dropout)
        self.decoder = Decoder(tgt_vocab_size, d_model, num_heads,
                               num_decoder_layers, d_ff, max_len, dropout)
        self.output_proj = nn.Linear(d_model, tgt_vocab_size)

        self._init_parameters()

    def _init_parameters(self) -> None:
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)

    @staticmethod
    def generate_square_subsequent_mask(sz: int) -> torch.Tensor:
        """创建因果掩码 (上三角为 0，下三角为 1)。"""
        return torch.triu(torch.ones(sz, sz) * float("-inf"), diagonal=1)

    @staticmethod
    def create_padding_mask(seq: torch.Tensor, pad_idx: int = 0) -> torch.Tensor:
        """创建 Padding 掩码 (padding=0, 正常=1)。"""
        return (seq != pad_idx).unsqueeze(1).unsqueeze(2)  # (batch, 1, 1, seq_len)

    def forward(self, src: torch.Tensor, tgt: torch.Tensor,
                src_pad_idx: int = 0, tgt_pad_idx: int = 0) -> torch.Tensor:
        src_mask = self.create_padding_mask(src, src_pad_idx)
        tgt_mask = self.create_padding_mask(tgt, tgt_pad_idx)
        causal_mask = self.generate_square_subsequent_mask(tgt.size(1)).to(tgt.device)
        tgt_mask = tgt_mask & (causal_mask == 0)   # type: ignore[operator]

        enc_out = self.encoder(src, src_mask)
        dec_out = self.decoder(tgt, enc_out, src_mask, tgt_mask)
        return self.output_proj(dec_out)


# ============================================================
# §8  GPT-style Decoder-Only Transformer
# ============================================================

class GPTBlock(nn.Module):
    """GPT 的基本构建块 — Decoder-only block。"""

    def __init__(self, d_model: int = 512, num_heads: int = 8,
                 d_ff: int = 2048, dropout: float = 0.1) -> None:
        super().__init__()
        self.attn = MultiHeadAttention(d_model, num_heads, dropout)
        self.ffn = FeedForward(d_model, d_ff, dropout, activation="gelu")
        self.ln1 = nn.LayerNorm(d_model)
        self.ln2 = nn.LayerNorm(d_model)

    def forward(self, x: torch.Tensor,
                mask: torch.Tensor | None = None) -> torch.Tensor:
        x = x + self.attn(self.ln1(x), self.ln1(x), self.ln1(x), mask)
        x = x + self.ffn(self.ln2(x))
        return x


class GPT(nn.Module):
    """GPT 风格的自回归语言模型。"""

    def __init__(self, vocab_size: int, d_model: int = 256,
                 num_heads: int = 8, num_layers: int = 4,
                 d_ff: int = 1024, max_len: int = 1024,
                 dropout: float = 0.1) -> None:
        super().__init__()
        self.token_embedding = nn.Embedding(vocab_size, d_model)
        self.pos_embedding = nn.Embedding(max_len, d_model)
        self.dropout = nn.Dropout(dropout)

        self.blocks = nn.ModuleList([
            GPTBlock(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])
        self.ln_final = nn.LayerNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size, bias=False)

        # 权重绑定
        self.lm_head.weight = self.token_embedding.weight

        self._init_weights()

    def _init_weights(self) -> None:
        for module in self.modules():
            if isinstance(module, nn.Linear):
                torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
                if module.bias is not None:
                    torch.nn.init.zeros_(module.bias)
            elif isinstance(module, nn.Embedding):
                torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, x: torch.Tensor,
                targets: torch.Tensor | None = None) -> tuple[torch.Tensor, torch.Tensor | None]:
        batch_size, seq_len = x.shape
        device = x.device

        # Token + Position embeddings
        positions = torch.arange(0, seq_len, device=device).unsqueeze(0)
        tok_emb = self.token_embedding(x)
        pos_emb = self.pos_embedding(positions)
        hidden = self.dropout(tok_emb + pos_emb)

        # Causal mask
        causal_mask = torch.triu(
            torch.ones(seq_len, seq_len, device=device) * float("-inf"), diagonal=1
        )

        # Transformer blocks
        for block in self.blocks:
            hidden = block(hidden, causal_mask)

        hidden = self.ln_final(hidden)
        logits = self.lm_head(hidden)

        loss = None
        if targets is not None:
            loss = F.cross_entropy(
                logits.view(-1, logits.size(-1)),
                targets.view(-1),
                ignore_index=-1,
            )

        return logits, loss

    @torch.no_grad()
    def generate(self, idx: torch.Tensor, max_new_tokens: int,
                 temperature: float = 1.0, top_k: int | None = None) -> torch.Tensor:
        """自回归生成。"""
        for _ in range(max_new_tokens):
            # 截断到最大上下文长度
            idx_cond = idx[:, -512:] if idx.size(1) > 512 else idx

            logits, _ = self(idx_cond)
            logits = logits[:, -1, :] / temperature

            if top_k is not None:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = float("-inf")

            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat((idx, idx_next), dim=1)

        return idx


# ============================================================
# §9  演示与测试
# ============================================================

def demo_transformer() -> None:
    print("=" * 60)
    print("Transformer (Encoder-Decoder) 演示")
    print("=" * 60)

    # 构建一个小型 Transformer
    model = Transformer(
        src_vocab_size=1000,
        tgt_vocab_size=1000,
        d_model=128,
        num_heads=4,
        num_encoder_layers=2,
        num_decoder_layers=2,
        d_ff=256,
        dropout=0.1,
    )
    n_params = sum(p.numel() for p in model.parameters())
    print(f"模型参数: {n_params:,}")

    # 虚拟数据
    src = torch.randint(1, 100, (2, 10))         # (batch=2, seq=10)
    tgt = torch.randint(1, 100, (2, 8))          # (batch=2, seq=8)

    # 前向传播
    output = model(src, tgt)
    print(f"src {src.shape}, tgt {tgt.shape} -> output {output.shape}")
    print(f"  (batch={output.shape[0]}, seq_len={output.shape[1]}, "
          f"vocab={output.shape[2]})")


def demo_gpt() -> None:
    print("\n" + "=" * 60)
    print("GPT (Decoder-Only) 演示")
    print("=" * 60)

    vocab_size = 256
    gpt = GPT(
        vocab_size=vocab_size,
        d_model=128,
        num_heads=4,
        num_layers=3,
        d_ff=256,
        max_len=256,
        dropout=0.1,
    )
    n_params = sum(p.numel() for p in gpt.parameters())
    print(f"模型参数: {n_params:,}")

    # 随机输入序列
    x = torch.randint(0, vocab_size, (2, 32))
    targets = torch.randint(0, vocab_size, (2, 32))

    # 训练前向
    logits, loss = gpt(x, targets)
    print(f"输入 {x.shape}, 目标 {targets.shape} -> logits {logits.shape}")
    print(f"训练损失: {loss.item():.4f}")

    # 推理 + 生成
    gpt.eval()
    start_ids = torch.tensor([[1, 2, 3]])         # 起始 token
    generated = gpt.generate(start_ids, max_new_tokens=15, temperature=0.8, top_k=10)
    print(f"生成序列: {generated.tolist()}")


def demo_attention_patterns() -> None:
    print("\n" + "=" * 60)
    print("Attention 模式可视化 (数值)")
    print("=" * 60)

    mha = MultiHeadAttention(d_model=8, num_heads=2, dropout=0.0)
    mha.eval()

    # 简单查询
    x = torch.tensor([[
        [1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0],   # token 0 (类似 "I")
        [0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0],   # token 1 (类似 "love")
        [0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0],   # token 2 (类似 "you")
    ]])                                                # (1, 3, 8)

    with torch.no_grad():
        Q = mha.split_heads(mha.W_q(x))
        K = mha.split_heads(mha.W_k(x))
        V = mha.split_heads(mha.W_v(x))

        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(4)
        attn_weights = F.softmax(scores, dim=-1)

    print(f"Q shape: {Q.shape}  (batch=1, heads=2, seq=3, d_k=4)")
    print(f"Attention weights (head 0):\n{attn_weights[0, 0]}")
    print(f"Attention weights (head 1):\n{attn_weights[0, 1]}")


def demo_training_step() -> None:
    """简单训练循环演示。"""
    print("\n" + "=" * 60)
    print("GPT 训练步骤演示")
    print("=" * 60)

    gpt_small = GPT(vocab_size=64, d_model=64, num_heads=4,
                    num_layers=2, d_ff=128, max_len=128)

    optimizer = torch.optim.AdamW(gpt_small.parameters(), lr=3e-4)

    # 模拟数据
    batch = torch.randint(0, 64, (4, 16))
    targets = torch.randint(0, 64, (4, 16))

    gpt_small.train()
    for step in range(5):
        optimizer.zero_grad()
        logits, loss = gpt_small(batch, targets)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(gpt_small.parameters(), max_norm=1.0)
        optimizer.step()
        print(f"  Step {step+1}: loss = {loss.item():.4f}")

    print("训练步骤完成")


if __name__ == "__main__":
    demo_attention_patterns()
    demo_transformer()
    demo_gpt()
    demo_training_step()
    print("\n✅ Transformer 篇全部执行完毕!")
