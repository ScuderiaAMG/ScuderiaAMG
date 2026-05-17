#!/usr/bin/env python3
"""
词嵌入从零实现 —— Word2Vec / GloVe / FastText
涵盖：Skip-gram (负采样) / CBOW、GloVe (共现矩阵+加权最小二乘)、
      FastText (子词模型)、词向量评估 (类比推理/相似度)、
      完整训练循环与可视化
"""

import numpy as np
from typing import Any
from collections import Counter, defaultdict
import math
import random

rng = np.random.default_rng(42)


# ============================================================
# §1  Skip-gram with Negative Sampling
# ============================================================

class SkipGram:
    """Skip-gram 模型 —— 用负采样训练。

    P(pos | w, c) = σ(v_w · v_c)
    P(neg | w, c) = σ(-v_w · v_n)
    """

    def __init__(self, vocab_size: int, embedding_dim: int = 100,
                 n_negatives: int = 5, lr: float = 0.025,
                 subsample_threshold: float = 1e-3) -> None:
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.n_negatives = n_negatives
        self.lr = lr
        self.subsample_threshold = subsample_threshold

        # 初始化嵌入矩阵
        std = 1.0 / np.sqrt(embedding_dim)
        self.W_in = rng.normal(0, std, (vocab_size, embedding_dim))   # 输入词向量
        self.W_out = rng.normal(0, std, (vocab_size, embedding_dim))  # 输出词向量

        # 负采样分布 (unigram ^ 0.75)
        self._noise_dist: np.ndarray | None = None
        self._word_counts: Counter[int] = Counter()

    def build_noise_distribution(self, token_ids: list[int]) -> None:
        self._word_counts = Counter(token_ids)
        freq = np.array([self._word_counts.get(i, 0)
                         for i in range(self.vocab_size)], dtype=np.float64)
        freq = freq ** 0.75
        self._noise_dist = freq / freq.sum()

    def _subsample_prob(self, word_id: int):  # type: ignore[return]
        freq = self._word_counts.get(word_id, 0) / sum(self._word_counts.values())
        return 1 - np.sqrt(self.subsample_threshold / max(freq, 1e-12))

    def train_pair(self, center_id: int, context_id: int) -> float:
        """训练一对 (center, context) —— 一个正样本 + n 个负样本。"""
        v_c = self.W_in[center_id]               # 中心词向量

        # ---- 正样本 ----
        u_pos = self.W_out[context_id]
        sigmoid_pos = 1 / (1 + np.exp(-np.dot(v_c, u_pos)))
        grad_pos = (1 - sigmoid_pos) * self.lr

        self.W_in[center_id] += grad_pos * u_pos
        self.W_out[context_id] += grad_pos * v_c

        total_loss = -np.log(max(sigmoid_pos, 1e-12))

        # ---- 负样本 ----
        neg_ids = rng.choice(self.vocab_size, self.n_negatives,
                             p=self._noise_dist)
        for neg_id in neg_ids:
            u_neg = self.W_out[neg_id]
            sigmoid_neg = 1 / (1 + np.exp(-np.dot(v_c, u_neg)))
            grad_neg = sigmoid_neg * self.lr

            self.W_in[center_id] -= grad_neg * u_neg
            self.W_out[neg_id] -= grad_neg * v_c

            total_loss -= np.log(max(1 - sigmoid_neg, 1e-12))

        return float(total_loss)

    def train(self, tokenized_sentences: list[list[int]],
              window: int = 5, epochs: int = 5) -> list[float]:
        """在语料上训练。"""
        all_tokens = [t for sent in tokenized_sentences for t in sent]
        self.build_noise_distribution(all_tokens)

        losses: list[float] = []
        for epoch in range(epochs):
            total_loss = 0.0
            count = 0
            for sentence in tokenized_sentences:
                n = len(sentence)
                for i, center in enumerate(sentence):
                    # 子采样
                    if random.random() < self._subsample_prob(center):
                        continue

                    context_start = max(0, i - window)
                    context_end = min(n, i + window + 1)
                    for j in range(context_start, context_end):
                        if j == i:
                            continue
                        total_loss += self.train_pair(center, sentence[j])
                        count += 1

            avg_loss = total_loss / max(count, 1)
            losses.append(avg_loss)
            self.lr *= 0.95

        return losses

    def get_vector(self, word_id: int) -> np.ndarray:
        """返回输入嵌入 (通常用作词向量)。"""
        return self.W_in[word_id].copy()

    def similarity(self, id1: int, id2: int) -> float:
        v1 = self.W_in[id1]
        v2 = self.W_in[id2]
        n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
        if n1 == 0 or n2 == 0:
            return 0.0
        return float(np.dot(v1, v2) / (n1 * n2))


# ============================================================
# §2  CBOW
# ============================================================

class CBOW:
    """CBOW —— 用上下文词预测中心词。"""

    def __init__(self, vocab_size: int, embedding_dim: int = 100,
                 lr: float = 0.025) -> None:
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.lr = lr
        std = 1.0 / np.sqrt(embedding_dim)
        self.W_in = rng.normal(0, std, (vocab_size, embedding_dim))
        self.W_out = rng.normal(0, std, (vocab_size, embedding_dim))

    def train_example(self, context_ids: list[int],
                      center_id: int) -> float:
        # 上下文向量取平均
        context_vecs = self.W_in[context_ids]
        h = context_vecs.mean(axis=0)

        # 前向
        scores = self.W_out @ h
        # 使用 negative sampling 或 hierarchical softmax
        # 这里简化：使用负采样
        probs = self._negative_sampling_loss(h, center_id)
        loss = -np.log(max(probs, 1e-12))

        return float(loss)

    def _negative_sampling_loss(self, h: np.ndarray,
                                pos_id: int, n_negs: int = 5) -> float:
        score = np.dot(self.W_out[pos_id], h)
        sig_pos = 1 / (1 + np.exp(-score))

        grad_h = self.W_out[pos_id] * (sig_pos - 1) * self.lr
        self.W_out[pos_id] += self.lr * (1 - sig_pos) * h

        # 负样本
        neg_ids = rng.integers(0, self.vocab_size, n_negs)
        for neg_id in neg_ids:
            score_neg = np.dot(self.W_out[neg_id], h)
            sig_neg = 1 / (1 + np.exp(-score_neg))
            grad_h += self.W_out[neg_id] * sig_neg * self.lr
            self.W_out[neg_id] -= self.lr * sig_neg * h

        # 更新上下文向量
        # (需要反向传播到各个输入词向量，此处省略细节)
        return sig_pos


# ============================================================
# §3  GloVe
# ============================================================

class GloVe:
    """GloVe —— 基于全局词共现矩阵的词嵌入。

    J = Σ f(X_ij) (w_i·w̃_j + b_i + b̃_j - log X_ij)²
    """

    def __init__(self, vocab_size: int, embedding_dim: int = 100,
                 x_max: float = 100.0, alpha: float = 0.75,
                 lr: float = 0.05) -> None:
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.x_max = x_max
        self.alpha = alpha
        self.lr = lr

        std = 1.0 / np.sqrt(embedding_dim)
        self.W = rng.normal(0, std, (vocab_size, embedding_dim))
        self.W_tilde = rng.normal(0, std, (vocab_size, embedding_dim))
        self.b = np.zeros(vocab_size)
        self.b_tilde = np.zeros(vocab_size)

    def _weight_func(self, x: float) -> float:
        if x < self.x_max:
            return (x / self.x_max) ** self.alpha
        return 1.0

    def build_cooccurrence(self, tokenized_sentences: list[list[int]],
                           window: int = 10) -> dict[tuple[int, int], float]:
        """构建共现矩阵 X。"""
        cooccur: dict[tuple[int, int], float] = defaultdict(float)
        for sentence in tokenized_sentences:
            n = len(sentence)
            for i, w in enumerate(sentence):
                for j in range(max(0, i - window), min(n, i + window + 1)):
                    if i == j:
                        continue
                    c = sentence[j]
                    cooccur[(w, c)] += 1.0 / abs(i - j)  # 距离加权
        return dict(cooccur)

    def fit(self, cooccur: dict[tuple[int, int], float],
            epochs: int = 20) -> list[float]:
        pairs = list(cooccur.keys())
        losses: list[float] = []

        for epoch in range(epochs):
            random.shuffle(pairs)
            total_loss = 0.0
            count = 0

            for i, j in pairs:
                X_ij = cooccur[(i, j)]
                if X_ij == 0:
                    continue

                weight = self._weight_func(X_ij)
                diff = (np.dot(self.W[i], self.W_tilde[j])
                        + self.b[i] + self.b_tilde[j]
                        - math.log(X_ij))
                loss = weight * diff ** 2
                total_loss += loss
                count += 1

                grad = weight * diff * self.lr
                self.W[i] -= grad * self.W_tilde[j]
                self.W_tilde[j] -= grad * self.W[i]
                self.b[i] -= grad
                self.b_tilde[j] -= grad

            avg_loss = total_loss / max(count, 1)
            losses.append(float(avg_loss))

        return losses

    def get_vector(self, word_id: int) -> np.ndarray:
        """GloVe 通常返回 W + W_tilde 的平均。"""
        return (self.W[word_id] + self.W_tilde[word_id]) / 2


# ============================================================
# §4  FastText 子词模型
# ============================================================

class FastText:
    """FastText —— 词向量 = 主词向量 + Σ 子词 (n-gram) 向量。"""

    def __init__(self, vocab_size: int, embedding_dim: int = 100,
                 min_n: int = 3, max_n: int = 6,
                 lr: float = 0.025) -> None:
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.min_n = min_n
        self.max_n = max_n
        self.lr = lr

        # 子词哈希桶
        self.n_buckets = 2000000
        std = 1.0 / np.sqrt(embedding_dim)
        self.W_word = rng.normal(0, std, (vocab_size, embedding_dim))
        self.W_ngram = rng.normal(0, std, (self.n_buckets, embedding_dim))
        self.W_out = rng.normal(0, std, (vocab_size, embedding_dim))

    def _word_to_ngrams(self, word: str) -> list[int]:
        """返回子词的哈希桶索引。"""
        word = "<" + word + ">"
        ngrams: list[int] = []
        for n in range(self.min_n, min(self.max_n + 1, len(word) + 1)):
            for i in range(len(word) - n + 1):
                ngram = word[i:i + n]
                bucket = hash(ngram) % self.n_buckets
                ngrams.append(bucket)
        return ngrams

    def get_word_vector(self, word_id: int, word: str) -> np.ndarray:
        """主词向量 + 子词向量平均。"""
        vec = self.W_word[word_id].copy()
        ngrams = self._word_to_ngrams(word)
        if ngrams:
            vec += self.W_ngram[ngrams].mean(axis=0)
        return vec

    def train_pair(self, word_id: int, word: str,
                   context_id: int) -> float:
        v_w = self.get_word_vector(word_id, word)
        u_c = self.W_out[context_id]

        sig_pos = 1 / (1 + np.exp(-np.dot(v_w, u_c)))
        grad = self.lr * (1 - sig_pos)

        self.W_word[word_id] += grad * u_c
        ngrams = self._word_to_ngrams(word)
        for ng in ngrams:
            self.W_ngram[ng] += grad * u_c / len(ngrams)
        self.W_out[context_id] += grad * v_w

        n_negs = 5
        loss = -np.log(max(sig_pos, 1e-12))
        for _ in range(n_negs):
            neg_id = rng.integers(0, self.vocab_size)
            u_n = self.W_out[neg_id]
            sig_neg = 1 / (1 + np.exp(-np.dot(v_w, u_n)))
            loss -= np.log(max(1 - sig_neg, 1e-12))

            grad_neg = self.lr * (-sig_neg)
            self.W_word[word_id] += grad_neg * u_n
            for ng in ngrams:
                self.W_ngram[ng] += grad_neg * u_n / len(ngrams)
            self.W_out[neg_id] += grad_neg * v_w

        return float(loss)


# ============================================================
# §5  词向量评估
# ============================================================

class WordVectorEvaluator:
    """评估词向量质量 —— 类比推理 + 词相似度。"""

    @staticmethod
    def analogy(vectors: dict[str, np.ndarray],
                a: str, b: str, c: str,
                exclude: set[str] | None = None) -> str | None:
        """a : b :: c : ?  例如 king - man + woman = queen。"""
        if a not in vectors or b not in vectors or c not in vectors:
            return None

        target = vectors[b] - vectors[a] + vectors[c]
        best_word = None
        best_sim = -float("inf")
        exclude = exclude or {a, b, c}

        for word, vec in vectors.items():
            if word in exclude:
                continue
            n_target = np.linalg.norm(target)
            n_vec = np.linalg.norm(vec)
            if n_target == 0 or n_vec == 0:
                continue
            sim = np.dot(target, vec) / (n_target * n_vec)
            if sim > best_sim:
                best_sim = sim
                best_word = word

        return best_word

    @staticmethod
    def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
        n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
        return float(np.dot(v1, v2) / (n1 * n2)) if n1 > 0 and n2 > 0 else 0.0

    @staticmethod
    def most_similar(vectors: dict[str, np.ndarray],
                     word: str, top_n: int = 10) -> list[tuple[str, float]]:
        if word not in vectors:
            return []
        query = vectors[word]
        sims = []
        for w, vec in vectors.items():
            if w == word:
                continue
            sim = WordVectorEvaluator.cosine_similarity(query, vec)
            sims.append((w, sim))
        sims.sort(key=lambda x: -x[1])
        return sims[:top_n]


# ============================================================
# §6  完整训练流程演示
# ============================================================

def demo_word_embeddings() -> None:
    print("=" * 60)
    print("词嵌入 (Word Embeddings) 从零实现")
    print("=" * 60)

    # 构建小语料词表
    sentences = [
        ["the", "king", "rules", "the", "kingdom"],
        ["the", "queen", "leads", "the", "palace"],
        ["man", "and", "woman", "are", "human"],
        ["the", "boy", "plays", "in", "the", "park"],
        ["the", "girl", "reads", "a", "book"],
        ["king", "and", "queen", "are", "royal"],
        ["man", "eats", "food", "and", "drinks", "water"],
        ["woman", "cooks", "dinner", "for", "the", "family"],
        ["the", "prince", "is", "the", "son", "of", "the", "king"],
        ["the", "princess", "is", "the", "daughter", "of", "the", "queen"],
    ]

    # 构建词表
    vocab: dict[str, int] = {"<PAD>": 0, "<UNK>": 1}
    for sent in sentences:
        for word in sent:
            if word not in vocab:
                vocab[word] = len(vocab)
    inv_vocab = {v: k for k, v in vocab.items()}

    tokenized = [[vocab[w] for w in s] for s in sentences]
    print(f"词表大小: {len(vocab)}")

    # ---- Skip-gram ----
    print("\n--- Skip-gram (Negative Sampling) ---")
    sg = SkipGram(vocab_size=len(vocab), embedding_dim=50,
                  n_negatives=3, lr=0.05)
    losses = sg.train(tokenized, window=3, epochs=30)
    print(f"初始损失: {losses[0]:.4f}")
    print(f"最终损失: {losses[-1]:.4f}")

    # 词向量相似度
    print("相似度:")
    for w1, w2 in [("king", "queen"), ("man", "woman"), ("boy", "girl"),
                    ("king", "food"), ("prince", "princess")]:
        if w1 in vocab and w2 in vocab:
            sim = sg.similarity(vocab[w1], vocab[w2])
            print(f"  sim({w1}, {w2}) = {sim:.4f}")

    # ---- GloVe ----
    print("\n--- GloVe ---")
    glove = GloVe(vocab_size=len(vocab), embedding_dim=50)
    cooccur = glove.build_cooccurrence(tokenized, window=3)
    print(f"共现对数量: {len(cooccur)}")
    glove_losses = glove.fit(cooccur, epochs=20)
    print(f"初始损失: {glove_losses[0]:.4f}")
    print(f"最终损失: {glove_losses[-1]:.4f}")

    # ---- 评估 ----
    print("\n--- 词向量评估 ---")
    # 构建 vectors dict (使用最终的 W + W_tilde)
    vectors = {inv_vocab[i]: (glove.W[i] + glove.W_tilde[i]) / 2
               for i in range(len(vocab))}

    evaluator = WordVectorEvaluator()

    # 类比
    analogies = [
        ("king", "man", "queen"),      # 期望 woman
        ("prince", "boy", "princess"), # 期望 girl
    ]
    for a, b, c in analogies:
        if all(x in vectors for x in [a, b, c]):
            result = evaluator.analogy(vectors, a, b, c)
            print(f"  {a} - {b} + {c} ≈ '{result}'")

    # 最相似词
    for query in ["king", "food", "book"]:
        if query in vectors:
            similar = evaluator.most_similar(vectors, query, top_n=5)
            print(f"  most_similar({query}): {[(w, f'{s:.3f}') for w, s in similar]}")


if __name__ == "__main__":
    demo_word_embeddings()
    print("\n✅ 词嵌入篇执行完毕!")
