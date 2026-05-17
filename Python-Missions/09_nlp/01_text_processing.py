#!/usr/bin/env python3
"""
自然语言处理 —— 文本处理从零实现
涵盖：分词（正向/反向/双向最大匹配）、N-gram 语言模型、
      TF-IDF 计算与向量空间模型、朴素贝叶斯文本分类、
      HMM 中文分词与词性标注、TextRank 关键词提取、
      编辑距离与拼写纠错、BM25 检索、主题模型 (LDA 吉布斯采样)
"""

import numpy as np
import re
import math
from collections import defaultdict, Counter
from typing import Any
import heapq

rng = np.random.default_rng(42)


# ============================================================
# §1  分词算法
# ============================================================

def load_dictionary() -> set[str]:
    return {
        "研究", "生命", "起源", "研究生", "命", "的", "化学",
        "物质", "生物", "大分子", "细胞", "人类", "基因组",
        "蛋白质", "DNA", "RNA", "基因", "氨基酸", "核酸",
        "自然", "语言", "处理", "自然语言", "机器", "学习",
        "深度学习", "人工智能", "数据", "科学", "算法",
        "模型", "训练", "推理", "应用", "系统", "工程",
        "中国", "美国", "北京", "上海", "大学", "学院",
        "计算机", "软件", "硬件", "网络", "数据库",
    }


def forward_max_match(text: str, dictionary: set[str],
                      max_len: int = 5) -> list[str]:
    """正向最大匹配分词 (FMM)。"""
    words: list[str] = []
    i = 0
    while i < len(text):
        matched = text[i]
        for j in range(min(i + max_len, len(text)), i, -1):
            candidate = text[i:j]
            if candidate in dictionary:
                matched = candidate
                break
        words.append(matched)
        i += len(matched)
    return words


def backward_max_match(text: str, dictionary: set[str],
                       max_len: int = 5) -> list[str]:
    """逆向最大匹配分词 (BMM)。"""
    words: list[str] = []
    i = len(text)
    while i > 0:
        matched = text[i - 1]
        for j in range(max(0, i - max_len), i):
            candidate = text[j:i]
            if candidate in dictionary:
                matched = candidate
                break
        words.insert(0, matched)
        i -= len(matched)
    return words


def bidirectional_max_match(text: str, dictionary: set[str],
                            max_len: int = 5) -> list[str]:
    """双向最大匹配 —— 比较 FMM 和 BMM 结果，择优。"""
    fmm = forward_max_match(text, dictionary, max_len)
    bmm = backward_max_match(text, dictionary, max_len)

    if len(fmm) < len(bmm):
        return fmm
    if len(bmm) < len(fmm):
        return bmm
    # 同样多则选单字少的
    fmm_single = sum(1 for w in fmm if len(w) == 1)
    bmm_single = sum(1 for w in bmm if len(w) == 1)
    return fmm if fmm_single <= bmm_single else bmm


# ============================================================
# §2  N-gram 语言模型
# ============================================================

class NGramLM:
    """N-gram 语言模型 —— 带加一平滑 (Laplace Smoothing)。"""

    def __init__(self, n: int = 2) -> None:
        self.n = n
        self.counts: dict[tuple[str, ...], Counter[str]] = defaultdict(Counter)
        self.vocab: set[str] = set()
        self.total_tokens = 0

    def tokenize(self, text: str) -> list[str]:
        return re.findall(r'\w+|[，。！？、；：""''（）]', text)

    def train(self, corpus: list[str]) -> None:
        for doc in corpus:
            tokens = ["<s>"] * (self.n - 1) + self.tokenize(doc) + ["</s>"]
            self.total_tokens += len(tokens)
            self.vocab.update(tokens)
            for i in range(self.n - 1, len(tokens)):
                context = tuple(tokens[i - self.n + 1:i])
                self.counts[context][tokens[i]] += 1

    def probability(self, context: tuple[str, ...], word: str) -> float:
        cnt_context = sum(self.counts[context].values())
        cnt_word = self.counts[context].get(word, 0)
        V = len(self.vocab)
        return (cnt_word + 1) / (cnt_context + V) if cnt_context > 0 else 1.0 / V

    def perplexity(self, text: str) -> float:
        tokens = self.tokenize(text)
        padded = ["<s>"] * (self.n - 1) + tokens + ["</s>"]
        log_prob = 0.0
        N = len(tokens) + 1
        for i in range(self.n - 1, len(padded)):
            context = tuple(padded[i - self.n + 1:i])
            word = padded[i]
            p = self.probability(context, word)
            log_prob += math.log(max(p, 1e-12))
        return math.exp(-log_prob / N)

    def generate(self, max_len: int = 20) -> str:
        result = ["<s>"] * (self.n - 1)
        for _ in range(max_len):
            context = tuple(result[-(self.n - 1):])
            if context not in self.counts:
                break
            total = sum(self.counts[context].values())
            r = np.random.random() * total
            cumulative = 0.0
            for word, cnt in self.counts[context].items():
                cumulative += cnt
                if r <= cumulative:
                    result.append(word)
                    break
            if result[-1] == "</s>":
                break
        return "".join(w for w in result[self.n - 1:] if w not in ("<s>", "</s>"))


# ============================================================
# §3  TF-IDF 与向量空间模型
# ============================================================

class TFIDF:
    """TF-IDF 向量化器。"""

    def __init__(self, max_features: int = 5000) -> None:
        self.max_features = max_features
        self.vocabulary: dict[str, int] = {}
        self.idf: np.ndarray | None = None

    def tokenize(self, text: str) -> list[str]:
        return re.findall(r'[一-鿿\w]+', text.lower())

    def fit(self, documents: list[str]) -> "TFIDF":
        # 文档频率
        doc_freq: Counter[str] = Counter()
        tokenized_docs = [self.tokenize(doc) for doc in documents]

        for tokens in tokenized_docs:
            doc_freq.update(set(tokens))

        # 按文档频率排序选词
        n_docs = len(documents)
        sorted_terms = sorted(doc_freq.items(), key=lambda x: -x[1])[:self.max_features]
        self.vocabulary = {term: idx for idx, (term, _) in enumerate(sorted_terms)}

        # 计算 IDF
        self.idf = np.ones(len(self.vocabulary))
        for term, idx in self.vocabulary.items():
            df = doc_freq.get(term, 0)
            self.idf[idx] = math.log((n_docs + 1) / (df + 1)) + 1

        return self

    def transform(self, documents: list[str]) -> np.ndarray:
        result = np.zeros((len(documents), len(self.vocabulary)))
        for i, doc in enumerate(documents):
            tokens = self.tokenize(doc)
            tf = Counter(tokens)
            doc_len = max(len(tokens), 1)
            for term, freq in tf.items():
                if term in self.vocabulary:
                    j = self.vocabulary[term]
                    result[i, j] = (freq / doc_len) * self.idf[j]  # type: ignore[index]
        return result

    def fit_transform(self, documents: list[str]) -> np.ndarray:
        return self.fit(documents).transform(documents)

    def cosine_similarity(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))


# ============================================================
# §4  朴素贝叶斯文本分类
# ============================================================

class NaiveBayesClassifier:
    """多项式朴素贝叶斯 —— 文本分类。"""

    def __init__(self, alpha: float = 1.0) -> None:
        self.alpha = alpha                       # Laplace 平滑
        self.class_log_prior: dict[int, float] = {}
        self.feature_log_prob: dict[int, np.ndarray] = {}
        self.vocabulary: dict[str, int] = {}
        self.classes: list[int] = []

    def tokenize(self, text: str) -> list[str]:
        return re.findall(r'[一-鿿\w]+', text.lower())

    def fit(self, documents: list[str], labels: list[int]) -> "NaiveBayesClassifier":
        # 构建词表
        vocab_counter: Counter[str] = Counter()
        for doc in documents:
            vocab_counter.update(self.tokenize(doc))
        self.vocabulary = {word: i for i, word in enumerate(vocab_counter.keys())}
        n_features = len(self.vocabulary)

        # 按类别汇总
        self.classes = sorted(set(labels))
        class_counts: dict[int, int] = Counter(labels)
        n_docs = len(documents)

        for c in self.classes:
            self.class_log_prior[c] = math.log(class_counts[c] / n_docs)

            # 收集该类别所有文档的词
            class_docs = [doc for doc, lbl in zip(documents, labels) if lbl == c]
            class_word_counts = np.zeros(n_features) + self.alpha
            for doc in class_docs:
                for word in self.tokenize(doc):
                    if word in self.vocabulary:
                        class_word_counts[self.vocabulary[word]] += 1

            self.feature_log_prob[c] = (
                np.log(class_word_counts / class_word_counts.sum())
            )

        return self

    def predict(self, document: str) -> int:
        tokens = self.tokenize(document)
        best_class = self.classes[0]
        best_score = float("-inf")

        for c in self.classes:
            score = self.class_log_prior[c]
            for word in tokens:
                if word in self.vocabulary:
                    score += self.feature_log_prob[c][self.vocabulary[word]]
            if score > best_score:
                best_score = score
                best_class = c

        return best_class

    def predict_proba(self, document: str) -> dict[int, float]:
        tokens = self.tokenize(document)
        scores = {}
        for c in self.classes:
            score = self.class_log_prior[c]
            for word in tokens:
                if word in self.vocabulary:
                    score += self.feature_log_prob[c][self.vocabulary[word]]
            scores[c] = score

        max_score = max(scores.values())
        exp_scores = {c: math.exp(s - max_score) for c, s in scores.items()}
        total = sum(exp_scores.values())
        return {c: v / total for c, v in exp_scores.items()}


# ============================================================
# §5  HMM 中文分词
# ============================================================

class HMMSegmenter:
    """基于 HMM 的中文分词 —— BMES 标注体系。"""

    STATES = ["B", "M", "E", "S"]              # Begin, Middle, End, Single

    def __init__(self) -> None:
        self.start_prob: dict[str, float] = {s: 0.25 for s in self.STATES}
        self.trans_prob: dict[str, dict[str, float]] = {}
        self.emit_prob: dict[str, Counter[str]] = defaultdict(Counter)
        self.state_index: dict[str, int] = {s: i for i, s in enumerate(self.STATES)}

    def _label_to_bmes(self, words: list[str]) -> str:
        labels: list[str] = []
        for word in words:
            if len(word) == 1:
                labels.append("S")
            else:
                labels.extend(["B"] + ["M"] * (len(word) - 2) + ["E"])
        return "".join(labels)

    def train(self, segmented_sentences: list[list[str]]) -> None:
        # 统计转移和发射概率
        trans_counts: dict[str, Counter[str]] = defaultdict(Counter)
        total_start = 0

        for words in segmented_sentences:
            labels = self._label_to_bmes(words)
            total_start += 1
            first_state = labels[0]
            self.start_prob[first_state] = self.start_prob.get(first_state, 0) + 1  # type: ignore[operator]

            chars = "".join(words)
            for s, ch in zip(labels, chars):
                self.emit_prob[s][ch] += 1
            for s1, s2 in zip(labels, labels[1:]):
                trans_counts[s1][s2] += 1

        # 归一化
        for s in self.STATES:
            self.start_prob[s] /= total_start

        for s1 in self.STATES:
            total = sum(trans_counts[s1].values())
            self.trans_prob[s1] = {
                s2: cnt / total for s2, cnt in trans_counts[s1].items()
            }
            # 平滑
            if not self.trans_prob[s1]:
                self.trans_prob[s1] = {s2: 0.25 for s2 in self.STATES}

    def segment(self, text: str) -> list[str]:
        """维特比算法解码。"""
        if not text:
            return []

        n = len(text)
        dp = [{s: float("-inf") for s in self.STATES} for _ in range(n)]
        backtrack: list[dict[str, str]] = []

        # 初始化
        for s in self.STATES:
            emit_p = self.emit_prob[s].get(text[0], 1e-6) / sum(self.emit_prob[s].values())
            dp[0][s] = math.log(self.start_prob.get(s, 0.25)) + math.log(emit_p)

        # 递推
        for i in range(1, n):
            backtrack.append({})
            for curr_s in self.STATES:
                max_prob = float("-inf")
                best_prev = self.STATES[0]

                for prev_s in self.STATES:
                    trans_p = self.trans_prob.get(prev_s, {}).get(curr_s, 0.01)
                    prob = dp[i - 1][prev_s] + math.log(trans_p)
                    if prob > max_prob:
                        max_prob = prob
                        best_prev = prev_s

                emit_p = self.emit_prob[curr_s].get(text[i], 1e-6) / max(sum(self.emit_prob[curr_s].values()), 1)
                dp[i][curr_s] = max_prob + math.log(emit_p)
                backtrack[-1][curr_s] = best_prev

        # 回溯
        last_state = max(dp[-1], key=dp[-1].get)
        states = [last_state]
        for i in range(n - 2, -1, -1):
            states.append(backtrack[i][states[-1]])
        states.reverse()

        # BMES -> 词
        words: list[str] = []
        start = 0
        for i, s in enumerate(states):
            if s in ("E", "S"):
                words.append(text[start:i + 1])
                start = i + 1
        if start < len(text):
            words.append(text[start:])
        return words


# ============================================================
# §6  TextRank 关键词提取
# ============================================================

def textrank_keywords(text: str, top_n: int = 10,
                      window: int = 5, damping: float = 0.85,
                      max_iter: int = 100) -> list[tuple[str, float]]:
    """TextRank 关键词提取 —— 基于图的排序算法。"""
    # 分词 (简化: 使用正则)
    words = re.findall(r'[一-鿿\w]{2,}', text)
    if not words:
        return []

    word_set = list(set(words))
    word2idx = {w: i for i, w in enumerate(word_set)}
    n = len(word_set)

    # 构建共现图
    adjacency = np.zeros((n, n))
    cooccur = defaultdict(set)
    for i, w in enumerate(words):
        for j in range(i + 1, min(i + window, len(words))):
            if w != words[j]:
                cooccur[w].add(words[j])
                cooccur[words[j]].add(w)

    for w1, neighbors in cooccur.items():
        for w2 in neighbors:
            i, j = word2idx[w1], word2idx[w2]
            adjacency[i, j] = 1
            adjacency[j, i] = 1

    # 归一化
    for i in range(n):
        row_sum = adjacency[i].sum()
        if row_sum > 0:
            adjacency[i] /= row_sum

    # PageRank 迭代
    scores = np.ones(n) / n
    for _ in range(max_iter):
        prev_scores = scores.copy()
        scores = (1 - damping) / n + damping * adjacency.T @ scores
        if np.abs(scores - prev_scores).sum() < 1e-6:
            break

    ranked = [(word_set[i], scores[i]) for i in np.argsort(-scores)[:top_n]]
    return ranked


# ============================================================
# §7  BM25 检索
# ============================================================

class BM25:
    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self.documents: list[list[str]] = []
        self.doc_lengths: list[int] = []
        self.avgdl: float = 0.0
        self.idf: dict[str, float] = {}
        self.N: int = 0

    def fit(self, documents: list[str]) -> "BM25":
        self.documents = [re.findall(r'\w+', doc.lower()) for doc in documents]
        self.doc_lengths = [len(doc) for doc in self.documents]
        self.N = len(self.documents)
        self.avgdl = sum(self.doc_lengths) / max(self.N, 1)

        df: Counter[str] = Counter()
        for doc in self.documents:
            df.update(set(doc))

        for term, freq in df.items():
            self.idf[term] = math.log((self.N - freq + 0.5) / (freq + 0.5) + 1)

        return self

    def score(self, query: str, doc_idx: int) -> float:
        query_terms = re.findall(r'\w+', query.lower())
        doc = self.documents[doc_idx]
        doc_len = self.doc_lengths[doc_idx]
        tf = Counter(doc)

        score = 0.0
        for term in query_terms:
            if term not in self.idf:
                continue
            freq = tf.get(term, 0)
            if freq == 0:
                continue
            numerator = freq * (self.k1 + 1)
            denominator = freq + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl)
            score += self.idf[term] * numerator / denominator

        return score

    def search(self, query: str, top_k: int = 10) -> list[tuple[int, float]]:
        scores = [(i, self.score(query, i)) for i in range(self.N)]
        scores.sort(key=lambda x: -x[1])
        return scores[:top_k]


# ============================================================
# §8  拼写纠错
# ============================================================

class SpellCorrector:
    """基于编辑距离的简单拼写纠错。"""

    def __init__(self, word_list: list[str] | None = None) -> None:
        self.dictionary: set[str] = set(word_list or [])
        self.word_freq: Counter[str] = Counter(word_list or [])

    @staticmethod
    def edits1(word: str) -> set[str]:
        """生成编辑距离为 1 的所有候选词。"""
        letters = 'abcdefghijklmnopqrstuvwxyz'
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = {L + R[1:] for L, R in splits if R}
        transposes = {L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1}
        replaces = {L + c + R[1:] for L, R in splits if R for c in letters}
        inserts = {L + c + R for L, R in splits for c in letters}
        return deletes | transposes | replaces | inserts

    def edits2(self, word: str) -> set[str]:
        return {e2 for e1 in self.edits1(word) for e2 in self.edits1(e1)}

    def known(self, words: set[str]) -> set[str]:
        return words & self.dictionary

    def correct(self, word: str) -> str:
        candidates = (
            self.known({word}) or
            self.known(self.edits1(word)) or
            self.known(self.edits2(word)) or
            {word}
        )
        return max(candidates, key=lambda w: self.word_freq.get(w, 0))


# ============================================================
# §9  LDA 主题模型 (吉布斯采样)
# ============================================================

class LDA:
    """LDA 主题模型 —— 吉布斯采样。"""

    def __init__(self, n_topics: int = 5, alpha: float = 0.1,
                 beta: float = 0.01, n_iter: int = 500) -> None:
        self.n_topics = n_topics
        self.alpha = alpha
        self.beta = beta
        self.n_iter = n_iter

    def fit(self, documents: list[list[str]]) -> tuple[np.ndarray, np.ndarray]:
        # 构建词表
        vocab: dict[str, int] = {}
        for doc in documents:
            for word in doc:
                if word not in vocab:
                    vocab[word] = len(vocab)
        V = len(vocab)
        D = len(documents)

        # 初始化主题分配
        z: list[list[int]] = []
        n_doc_topic = np.zeros((D, self.n_topics))
        n_topic_word = np.zeros((self.n_topics, V))
        n_topic = np.zeros(self.n_topics)

        for d, doc in enumerate(documents):
            z_d = []
            for word in doc:
                topic = np.random.randint(0, self.n_topics)
                z_d.append(topic)
                w = vocab[word]
                n_doc_topic[d, topic] += 1
                n_topic_word[topic, w] += 1
                n_topic[topic] += 1
            z.append(z_d)

        # 吉布斯采样
        for _ in range(self.n_iter):
            for d, doc in enumerate(documents):
                for i, word in enumerate(doc):
                    w = vocab[word]
                    old_topic = z[d][i]

                    n_doc_topic[d, old_topic] -= 1
                    n_topic_word[old_topic, w] -= 1
                    n_topic[old_topic] -= 1

                    # 计算条件概率
                    p = np.zeros(self.n_topics)
                    for k in range(self.n_topics):
                        p[k] = ((n_doc_topic[d, k] + self.alpha) *
                                (n_topic_word[k, w] + self.beta) /
                                (n_topic[k] + self.beta * V))
                    p /= p.sum()

                    new_topic = np.random.choice(self.n_topics, p=p)
                    z[d][i] = new_topic
                    n_doc_topic[d, new_topic] += 1
                    n_topic_word[new_topic, w] += 1
                    n_topic[new_topic] += 1

        # 计算 doc-topic 和 topic-word 分布
        doc_topic = (n_doc_topic + self.alpha)
        doc_topic /= doc_topic.sum(axis=1, keepdims=True)

        topic_word = (n_topic_word + self.beta)
        topic_word /= topic_word.sum(axis=1, keepdims=True)

        self.doc_topic = doc_topic
        self.topic_word = topic_word
        self.vocab = vocab
        self.inv_vocab = {v: k for k, v in vocab.items()}

        return doc_topic, topic_word

    def get_topic_words(self, topic_id: int, top_n: int = 10) -> list[tuple[str, float]]:
        indices = np.argsort(-self.topic_word[topic_id])[:top_n]
        return [(self.inv_vocab[i], self.topic_word[topic_id, i])
                for i in indices]


# ============================================================
# §10  演示
# ============================================================

def demo_nlp() -> None:
    print("=" * 60)
    print("NLP 文本处理全集演示")
    print("=" * 60)

    # 分词
    dic = load_dictionary()
    text = "研究生命起源的化学物质"
    print(f"\n分词测试: '{text}'")
    print(f"  FMM:  {forward_max_match(text, dic)}")
    print(f"  BMM:  {backward_max_match(text, dic)}")
    print(f"  BiMM: {bidirectional_max_match(text, dic)}")

    text2 = "自然语言处理是人工智能的重要分支"
    print(f"\n分词测试: '{text2}'")
    print(f"  FMM:  {forward_max_match(text2, dic)}")
    print(f"  BMM:  {backward_max_match(text2, dic)}")
    print(f"  BiMM: {bidirectional_max_match(text2, dic)}")

    # N-gram
    print("\n--- N-gram 语言模型 ---")
    corpus = [
        "我喜欢自然语言处理",
        "自然语言处理很有趣",
        "机器学习和深度学习都是人工智能的分支",
        "我喜欢机器学习",
        "深度学习在自然语言处理中有广泛应用",
    ]
    lm = NGramLM(n=3)
    lm.train(corpus)
    print(f"词汇量: {len(lm.vocab)}")
    print(f"Perplexity: {lm.perplexity('我喜欢机器学习'):.2f}")
    print(f"生成: {lm.generate(15)}")

    # TF-IDF
    print("\n--- TF-IDF ---")
    docs = [
        "机器学习是人工智能的重要领域",
        "深度学习使用神经网络进行学习",
        "自然语言处理是人工智能的分支",
        "计算机视觉使用深度学习分析图像",
        "人工智能包括机器学习和深度学习",
    ]
    tfidf = TFIDF(max_features=50)
    X = tfidf.fit_transform(docs)
    sim = tfidf.cosine_similarity(X[0], X[1])
    print(f"Doc0 vs Doc1 相似度: {sim:.4f}")
    sim = tfidf.cosine_similarity(X[0], X[4])
    print(f"Doc0 vs Doc4 相似度: {sim:.4f}")

    # 朴素贝叶斯
    print("\n--- 朴素贝叶斯 ---")
    train_docs = [
        "I love this movie", "Great film", "Amazing acting",
        "Terrible movie", "Boring film", "I hate this",
    ]
    labels = [1, 1, 1, 0, 0, 0]
    nb = NaiveBayesClassifier()
    nb.fit(train_docs, labels)
    test = "I like this amazing film"
    print(f"'{test}' -> class {nb.predict(test)}")
    print(f"proba: {nb.predict_proba(test)}")

    # HMM 分词
    print("\n--- HMM 分词 ---")
    training_data = [
        ["我", "是", "学生"],
        ["他", "喜欢", "编程"],
        ["今天", "天气", "很好"],
        ["北京", "是", "中国", "的", "首都"],
        ["我", "在", "清华大学", "读书"],
    ]
    hmm = HMMSegmenter()
    hmm.train(training_data)
    print(f"分词 '我是清华大学的学生': {hmm.segment('我是清华大学的学生')}")

    # TextRank
    print("\n--- TextRank 关键词 ---")
    long_text = (
        "自然语言处理是人工智能和语言学领域的分支学科。"
        "此领域探讨如何处理及运用自然语言；自然语言处理包括多方面和步骤，"
        "基本有认知、理解、生成等部分。"
        "自然语言认知和理解是让电脑把输入的语言变成有意思的符号和关系，"
        "然后根据目的再处理。自然语言生成系统则是把计算机数据转化为自然语言。"
    )
    keywords = textrank_keywords(long_text)
    print(f"关键词: {keywords}")

    # BM25
    print("\n--- BM25 检索 ---")
    bm = BM25()
    bm.fit(docs)
    results = bm.search("深度学习 人工智能", top_k=3)
    for idx, score in results:
        print(f"  Doc{idx} (score={score:.4f}): {docs[idx]}")

    # 拼写纠错
    print("\n--- 拼写纠错 ---")
    word_list = ["spelling", "correct", "hello", "world", "python",
                 "learning", "machine", "language", "natural", "processing"]
    corrector = SpellCorrector(word_list)
    for wrong in ["speling", "helo", "machime", "procesing"]:
        print(f"  '{wrong}' -> '{corrector.correct(wrong)}'")

    # LDA
    print("\n--- LDA 主题模型 ---")
    lda_docs = [
        ["machine", "learning", "data", "algorithm", "model"],
        ["deep", "learning", "neural", "network", "training"],
        ["natural", "language", "processing", "text", "nlp"],
        ["computer", "vision", "image", "detection", "object"],
        ["algorithm", "data", "model", "training", "deep"],
        ["text", "nlp", "language", "natural", "speech"],
        ["image", "vision", "object", "computer", "recognition"],
        ["network", "neural", "deep", "learning", "model"],
    ]
    lda_model = LDA(n_topics=3, n_iter=300)
    lda_model.fit(lda_docs)
    for t in range(3):
        print(f"  Topic {t}: {lda_model.get_topic_words(t, 5)}")


if __name__ == "__main__":
    demo_nlp()
    print("\n✅ NLP 文本处理篇执行完毕!")
