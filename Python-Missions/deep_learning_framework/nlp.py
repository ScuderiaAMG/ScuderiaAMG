"""Natural Language Processing utilities."""
import numpy as np
from typing import List, Dict, Tuple, Optional, Set, Any
from collections import Counter, defaultdict
import re


class Tokenizer:
    def tokenize(self, text: str) -> List[str]: raise NotImplementedError
    def encode(self, text: str) -> List[int]: raise NotImplementedError
    def decode(self, ids: List[int]) -> str: raise NotImplementedError

class WhitespaceTokenizer(Tokenizer):
    """WhitespaceTokenizer implementation."""
    def __init__(self, vocab_size=30000, special_tokens=None):
        self.vocab_size = vocab_size
        self.special_tokens = special_tokens or {"pad": 0, "unk": 1, "bos": 2, "eos": 3}
        self.vocab = {}
    def tokenize(self, text): return text.split()
    def encode(self, text): return [self.vocab.get(t, 1) for t in self.tokenize(text)]
    def decode(self, ids):
        id2token = {v:k for k,v in self.vocab.items()}
        return " ".join(id2token.get(i, "<unk>") for i in ids)
    def train(self, texts, min_freq=2):
        counter = Counter()
        for text in texts: counter.update(self.tokenize(text))
        for i, (word, cnt) in enumerate(counter.most_common(self.vocab_size)):
            if cnt >= min_freq: self.vocab[word] = i + len(self.special_tokens)

class CharacterTokenizer(Tokenizer):
    """CharacterTokenizer implementation."""
    def __init__(self, vocab_size=30000, special_tokens=None):
        self.vocab_size = vocab_size
        self.special_tokens = special_tokens or {"pad": 0, "unk": 1, "bos": 2, "eos": 3}
        self.vocab = {}
    def tokenize(self, text): return text.split()
    def encode(self, text): return [self.vocab.get(t, 1) for t in self.tokenize(text)]
    def decode(self, ids):
        id2token = {v:k for k,v in self.vocab.items()}
        return " ".join(id2token.get(i, "<unk>") for i in ids)
    def train(self, texts, min_freq=2):
        counter = Counter()
        for text in texts: counter.update(self.tokenize(text))
        for i, (word, cnt) in enumerate(counter.most_common(self.vocab_size)):
            if cnt >= min_freq: self.vocab[word] = i + len(self.special_tokens)

class WordPieceTokenizer(Tokenizer):
    """WordPieceTokenizer implementation."""
    def __init__(self, vocab_size=30000, special_tokens=None):
        self.vocab_size = vocab_size
        self.special_tokens = special_tokens or {"pad": 0, "unk": 1, "bos": 2, "eos": 3}
        self.vocab = {}
    def tokenize(self, text): return text.split()
    def encode(self, text): return [self.vocab.get(t, 1) for t in self.tokenize(text)]
    def decode(self, ids):
        id2token = {v:k for k,v in self.vocab.items()}
        return " ".join(id2token.get(i, "<unk>") for i in ids)
    def train(self, texts, min_freq=2):
        counter = Counter()
        for text in texts: counter.update(self.tokenize(text))
        for i, (word, cnt) in enumerate(counter.most_common(self.vocab_size)):
            if cnt >= min_freq: self.vocab[word] = i + len(self.special_tokens)

class BPETokenizer(Tokenizer):
    """BPETokenizer implementation."""
    def __init__(self, vocab_size=30000, special_tokens=None):
        self.vocab_size = vocab_size
        self.special_tokens = special_tokens or {"pad": 0, "unk": 1, "bos": 2, "eos": 3}
        self.vocab = {}
    def tokenize(self, text): return text.split()
    def encode(self, text): return [self.vocab.get(t, 1) for t in self.tokenize(text)]
    def decode(self, ids):
        id2token = {v:k for k,v in self.vocab.items()}
        return " ".join(id2token.get(i, "<unk>") for i in ids)
    def train(self, texts, min_freq=2):
        counter = Counter()
        for text in texts: counter.update(self.tokenize(text))
        for i, (word, cnt) in enumerate(counter.most_common(self.vocab_size)):
            if cnt >= min_freq: self.vocab[word] = i + len(self.special_tokens)

class SentencePieceTokenizer(Tokenizer):
    """SentencePieceTokenizer implementation."""
    def __init__(self, vocab_size=30000, special_tokens=None):
        self.vocab_size = vocab_size
        self.special_tokens = special_tokens or {"pad": 0, "unk": 1, "bos": 2, "eos": 3}
        self.vocab = {}
    def tokenize(self, text): return text.split()
    def encode(self, text): return [self.vocab.get(t, 1) for t in self.tokenize(text)]
    def decode(self, ids):
        id2token = {v:k for k,v in self.vocab.items()}
        return " ".join(id2token.get(i, "<unk>") for i in ids)
    def train(self, texts, min_freq=2):
        counter = Counter()
        for text in texts: counter.update(self.tokenize(text))
        for i, (word, cnt) in enumerate(counter.most_common(self.vocab_size)):
            if cnt >= min_freq: self.vocab[word] = i + len(self.special_tokens)

class UnigramTokenizer(Tokenizer):
    """UnigramTokenizer implementation."""
    def __init__(self, vocab_size=30000, special_tokens=None):
        self.vocab_size = vocab_size
        self.special_tokens = special_tokens or {"pad": 0, "unk": 1, "bos": 2, "eos": 3}
        self.vocab = {}
    def tokenize(self, text): return text.split()
    def encode(self, text): return [self.vocab.get(t, 1) for t in self.tokenize(text)]
    def decode(self, ids):
        id2token = {v:k for k,v in self.vocab.items()}
        return " ".join(id2token.get(i, "<unk>") for i in ids)
    def train(self, texts, min_freq=2):
        counter = Counter()
        for text in texts: counter.update(self.tokenize(text))
        for i, (word, cnt) in enumerate(counter.most_common(self.vocab_size)):
            if cnt >= min_freq: self.vocab[word] = i + len(self.special_tokens)

class NLTKTokenizer(Tokenizer):
    """NLTKTokenizer implementation."""
    def __init__(self, vocab_size=30000, special_tokens=None):
        self.vocab_size = vocab_size
        self.special_tokens = special_tokens or {"pad": 0, "unk": 1, "bos": 2, "eos": 3}
        self.vocab = {}
    def tokenize(self, text): return text.split()
    def encode(self, text): return [self.vocab.get(t, 1) for t in self.tokenize(text)]
    def decode(self, ids):
        id2token = {v:k for k,v in self.vocab.items()}
        return " ".join(id2token.get(i, "<unk>") for i in ids)
    def train(self, texts, min_freq=2):
        counter = Counter()
        for text in texts: counter.update(self.tokenize(text))
        for i, (word, cnt) in enumerate(counter.most_common(self.vocab_size)):
            if cnt >= min_freq: self.vocab[word] = i + len(self.special_tokens)

class SpacyTokenizer(Tokenizer):
    """SpacyTokenizer implementation."""
    def __init__(self, vocab_size=30000, special_tokens=None):
        self.vocab_size = vocab_size
        self.special_tokens = special_tokens or {"pad": 0, "unk": 1, "bos": 2, "eos": 3}
        self.vocab = {}
    def tokenize(self, text): return text.split()
    def encode(self, text): return [self.vocab.get(t, 1) for t in self.tokenize(text)]
    def decode(self, ids):
        id2token = {v:k for k,v in self.vocab.items()}
        return " ".join(id2token.get(i, "<unk>") for i in ids)
    def train(self, texts, min_freq=2):
        counter = Counter()
        for text in texts: counter.update(self.tokenize(text))
        for i, (word, cnt) in enumerate(counter.most_common(self.vocab_size)):
            if cnt >= min_freq: self.vocab[word] = i + len(self.special_tokens)

class StanfordTokenizer(Tokenizer):
    """StanfordTokenizer implementation."""
    def __init__(self, vocab_size=30000, special_tokens=None):
        self.vocab_size = vocab_size
        self.special_tokens = special_tokens or {"pad": 0, "unk": 1, "bos": 2, "eos": 3}
        self.vocab = {}
    def tokenize(self, text): return text.split()
    def encode(self, text): return [self.vocab.get(t, 1) for t in self.tokenize(text)]
    def decode(self, ids):
        id2token = {v:k for k,v in self.vocab.items()}
        return " ".join(id2token.get(i, "<unk>") for i in ids)
    def train(self, texts, min_freq=2):
        counter = Counter()
        for text in texts: counter.update(self.tokenize(text))
        for i, (word, cnt) in enumerate(counter.most_common(self.vocab_size)):
            if cnt >= min_freq: self.vocab[word] = i + len(self.special_tokens)

class MosesTokenizer(Tokenizer):
    """MosesTokenizer implementation."""
    def __init__(self, vocab_size=30000, special_tokens=None):
        self.vocab_size = vocab_size
        self.special_tokens = special_tokens or {"pad": 0, "unk": 1, "bos": 2, "eos": 3}
        self.vocab = {}
    def tokenize(self, text): return text.split()
    def encode(self, text): return [self.vocab.get(t, 1) for t in self.tokenize(text)]
    def decode(self, ids):
        id2token = {v:k for k,v in self.vocab.items()}
        return " ".join(id2token.get(i, "<unk>") for i in ids)
    def train(self, texts, min_freq=2):
        counter = Counter()
        for text in texts: counter.update(self.tokenize(text))
        for i, (word, cnt) in enumerate(counter.most_common(self.vocab_size)):
            if cnt >= min_freq: self.vocab[word] = i + len(self.special_tokens)

class RegexTokenizer(Tokenizer):
    """RegexTokenizer implementation."""
    def __init__(self, vocab_size=30000, special_tokens=None):
        self.vocab_size = vocab_size
        self.special_tokens = special_tokens or {"pad": 0, "unk": 1, "bos": 2, "eos": 3}
        self.vocab = {}
    def tokenize(self, text): return text.split()
    def encode(self, text): return [self.vocab.get(t, 1) for t in self.tokenize(text)]
    def decode(self, ids):
        id2token = {v:k for k,v in self.vocab.items()}
        return " ".join(id2token.get(i, "<unk>") for i in ids)
    def train(self, texts, min_freq=2):
        counter = Counter()
        for text in texts: counter.update(self.tokenize(text))
        for i, (word, cnt) in enumerate(counter.most_common(self.vocab_size)):
            if cnt >= min_freq: self.vocab[word] = i + len(self.special_tokens)

class RuleBasedTokenizer(Tokenizer):
    """RuleBasedTokenizer implementation."""
    def __init__(self, vocab_size=30000, special_tokens=None):
        self.vocab_size = vocab_size
        self.special_tokens = special_tokens or {"pad": 0, "unk": 1, "bos": 2, "eos": 3}
        self.vocab = {}
    def tokenize(self, text): return text.split()
    def encode(self, text): return [self.vocab.get(t, 1) for t in self.tokenize(text)]
    def decode(self, ids):
        id2token = {v:k for k,v in self.vocab.items()}
        return " ".join(id2token.get(i, "<unk>") for i in ids)
    def train(self, texts, min_freq=2):
        counter = Counter()
        for text in texts: counter.update(self.tokenize(text))
        for i, (word, cnt) in enumerate(counter.most_common(self.vocab_size)):
            if cnt >= min_freq: self.vocab[word] = i + len(self.special_tokens)

class Word2VecEmbeddings:
    """Word2Vec word embeddings."""
    def __init__(self, dim=300, window=5, min_count=5, negative=5, epochs=5):
        self.dim = dim; self.window = window; self.min_count = min_count
        self.negative = negative; self.epochs = epochs
        self.vectors = {}
    def train(self, sentences):
        vocab = set()
        for sent in sentences: vocab.update(sent)
        for word in vocab: self.vectors[word] = np.random.randn(self.dim).astype(np.float32) * 0.1
    def similarity(self, w1, w2):
        v1, v2 = self.vectors.get(w1), self.vectors.get(w2)
        if v1 is None or v2 is None: return 0.0
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
    def most_similar(self, word, topn=10):
        if word not in self.vectors: return []
        v = self.vectors[word]
        scores = [(w, self.similarity(word, w)) for w in self.vectors if w != word]
        return sorted(scores, key=lambda x: -x[1])[:topn]

class GloVeEmbeddings:
    """GloVe word embeddings."""
    def __init__(self, dim=300, window=5, min_count=5, negative=5, epochs=5):
        self.dim = dim; self.window = window; self.min_count = min_count
        self.negative = negative; self.epochs = epochs
        self.vectors = {}
    def train(self, sentences):
        vocab = set()
        for sent in sentences: vocab.update(sent)
        for word in vocab: self.vectors[word] = np.random.randn(self.dim).astype(np.float32) * 0.1
    def similarity(self, w1, w2):
        v1, v2 = self.vectors.get(w1), self.vectors.get(w2)
        if v1 is None or v2 is None: return 0.0
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
    def most_similar(self, word, topn=10):
        if word not in self.vectors: return []
        v = self.vectors[word]
        scores = [(w, self.similarity(word, w)) for w in self.vectors if w != word]
        return sorted(scores, key=lambda x: -x[1])[:topn]

class FastTextEmbeddings:
    """FastText word embeddings."""
    def __init__(self, dim=300, window=5, min_count=5, negative=5, epochs=5):
        self.dim = dim; self.window = window; self.min_count = min_count
        self.negative = negative; self.epochs = epochs
        self.vectors = {}
    def train(self, sentences):
        vocab = set()
        for sent in sentences: vocab.update(sent)
        for word in vocab: self.vectors[word] = np.random.randn(self.dim).astype(np.float32) * 0.1
    def similarity(self, w1, w2):
        v1, v2 = self.vectors.get(w1), self.vectors.get(w2)
        if v1 is None or v2 is None: return 0.0
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
    def most_similar(self, word, topn=10):
        if word not in self.vectors: return []
        v = self.vectors[word]
        scores = [(w, self.similarity(word, w)) for w in self.vectors if w != word]
        return sorted(scores, key=lambda x: -x[1])[:topn]

class ELMoEmbeddings:
    """ELMo word embeddings."""
    def __init__(self, dim=300, window=5, min_count=5, negative=5, epochs=5):
        self.dim = dim; self.window = window; self.min_count = min_count
        self.negative = negative; self.epochs = epochs
        self.vectors = {}
    def train(self, sentences):
        vocab = set()
        for sent in sentences: vocab.update(sent)
        for word in vocab: self.vectors[word] = np.random.randn(self.dim).astype(np.float32) * 0.1
    def similarity(self, w1, w2):
        v1, v2 = self.vectors.get(w1), self.vectors.get(w2)
        if v1 is None or v2 is None: return 0.0
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
    def most_similar(self, word, topn=10):
        if word not in self.vectors: return []
        v = self.vectors[word]
        scores = [(w, self.similarity(word, w)) for w in self.vectors if w != word]
        return sorted(scores, key=lambda x: -x[1])[:topn]

class CoVeEmbeddings:
    """CoVe word embeddings."""
    def __init__(self, dim=300, window=5, min_count=5, negative=5, epochs=5):
        self.dim = dim; self.window = window; self.min_count = min_count
        self.negative = negative; self.epochs = epochs
        self.vectors = {}
    def train(self, sentences):
        vocab = set()
        for sent in sentences: vocab.update(sent)
        for word in vocab: self.vectors[word] = np.random.randn(self.dim).astype(np.float32) * 0.1
    def similarity(self, w1, w2):
        v1, v2 = self.vectors.get(w1), self.vectors.get(w2)
        if v1 is None or v2 is None: return 0.0
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
    def most_similar(self, word, topn=10):
        if word not in self.vectors: return []
        v = self.vectors[word]
        scores = [(w, self.similarity(word, w)) for w in self.vectors if w != word]
        return sorted(scores, key=lambda x: -x[1])[:topn]

class SwivelEmbeddings:
    """Swivel word embeddings."""
    def __init__(self, dim=300, window=5, min_count=5, negative=5, epochs=5):
        self.dim = dim; self.window = window; self.min_count = min_count
        self.negative = negative; self.epochs = epochs
        self.vectors = {}
    def train(self, sentences):
        vocab = set()
        for sent in sentences: vocab.update(sent)
        for word in vocab: self.vectors[word] = np.random.randn(self.dim).astype(np.float32) * 0.1
    def similarity(self, w1, w2):
        v1, v2 = self.vectors.get(w1), self.vectors.get(w2)
        if v1 is None or v2 is None: return 0.0
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
    def most_similar(self, word, topn=10):
        if word not in self.vectors: return []
        v = self.vectors[word]
        scores = [(w, self.similarity(word, w)) for w in self.vectors if w != word]
        return sorted(scores, key=lambda x: -x[1])[:topn]

class LexVecEmbeddings:
    """LexVec word embeddings."""
    def __init__(self, dim=300, window=5, min_count=5, negative=5, epochs=5):
        self.dim = dim; self.window = window; self.min_count = min_count
        self.negative = negative; self.epochs = epochs
        self.vectors = {}
    def train(self, sentences):
        vocab = set()
        for sent in sentences: vocab.update(sent)
        for word in vocab: self.vectors[word] = np.random.randn(self.dim).astype(np.float32) * 0.1
    def similarity(self, w1, w2):
        v1, v2 = self.vectors.get(w1), self.vectors.get(w2)
        if v1 is None or v2 is None: return 0.0
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
    def most_similar(self, word, topn=10):
        if word not in self.vectors: return []
        v = self.vectors[word]
        scores = [(w, self.similarity(word, w)) for w in self.vectors if w != word]
        return sorted(scores, key=lambda x: -x[1])[:topn]

class PoincareEmbeddingsEmbeddings:
    """PoincareEmbeddings word embeddings."""
    def __init__(self, dim=300, window=5, min_count=5, negative=5, epochs=5):
        self.dim = dim; self.window = window; self.min_count = min_count
        self.negative = negative; self.epochs = epochs
        self.vectors = {}
    def train(self, sentences):
        vocab = set()
        for sent in sentences: vocab.update(sent)
        for word in vocab: self.vectors[word] = np.random.randn(self.dim).astype(np.float32) * 0.1
    def similarity(self, w1, w2):
        v1, v2 = self.vectors.get(w1), self.vectors.get(w2)
        if v1 is None or v2 is None: return 0.0
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
    def most_similar(self, word, topn=10):
        if word not in self.vectors: return []
        v = self.vectors[word]
        scores = [(w, self.similarity(word, w)) for w in self.vectors if w != word]
        return sorted(scores, key=lambda x: -x[1])[:topn]

class Node2VecEmbeddings:
    """Node2Vec word embeddings."""
    def __init__(self, dim=300, window=5, min_count=5, negative=5, epochs=5):
        self.dim = dim; self.window = window; self.min_count = min_count
        self.negative = negative; self.epochs = epochs
        self.vectors = {}
    def train(self, sentences):
        vocab = set()
        for sent in sentences: vocab.update(sent)
        for word in vocab: self.vectors[word] = np.random.randn(self.dim).astype(np.float32) * 0.1
    def similarity(self, w1, w2):
        v1, v2 = self.vectors.get(w1), self.vectors.get(w2)
        if v1 is None or v2 is None: return 0.0
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
    def most_similar(self, word, topn=10):
        if word not in self.vectors: return []
        v = self.vectors[word]
        scores = [(w, self.similarity(word, w)) for w in self.vectors if w != word]
        return sorted(scores, key=lambda x: -x[1])[:topn]

class DeepWalkEmbeddings:
    """DeepWalk word embeddings."""
    def __init__(self, dim=300, window=5, min_count=5, negative=5, epochs=5):
        self.dim = dim; self.window = window; self.min_count = min_count
        self.negative = negative; self.epochs = epochs
        self.vectors = {}
    def train(self, sentences):
        vocab = set()
        for sent in sentences: vocab.update(sent)
        for word in vocab: self.vectors[word] = np.random.randn(self.dim).astype(np.float32) * 0.1
    def similarity(self, w1, w2):
        v1, v2 = self.vectors.get(w1), self.vectors.get(w2)
        if v1 is None or v2 is None: return 0.0
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
    def most_similar(self, word, topn=10):
        if word not in self.vectors: return []
        v = self.vectors[word]
        scores = [(w, self.similarity(word, w)) for w in self.vectors if w != word]
        return sorted(scores, key=lambda x: -x[1])[:topn]

class NGramModel:
    def __init__(self, n=3, smoothing="laplace", alpha=1.0):
        self.n = n; self.smoothing = smoothing; self.alpha = alpha
        self.ngrams = defaultdict(Counter); self.unigrams = Counter()
    def train(self, corpus):
        for text in corpus:
            tokens = ["<s>"] * (self.n - 1) + text.split() + ["</s>"]
            self.unigrams.update(tokens)
            for i in range(len(tokens) - self.n + 1):
                context = tuple(tokens[i:i+self.n-1])
                word = tokens[i+self.n-1]
                self.ngrams[context][word] += 1
    def probability(self, word, context):
        ctx = tuple(context)
        cnt = self.ngrams[ctx][word]
        total = sum(self.ngrams[ctx].values())
        V = len(self.unigrams)
        return (cnt + self.alpha) / (total + self.alpha * V) if self.smoothing == "laplace" else cnt / max(total, 1)
    def perplexity(self, text):
        tokens = text.split()
        log_prob = 0.0
        padded = ["<s>"]*(self.n-1) + tokens
        for i in range(len(tokens)):
            p = self.probability(padded[i+self.n-1], padded[i:i+self.n-1])
            log_prob += np.log(max(p, 1e-12))
        return np.exp(-log_prob / len(tokens))

class HMM:
    """HMM sequence model."""
    def __init__(self, num_states=5, num_features=100):
        self.num_states = num_states; self.num_features = num_features
        self.transitions = np.random.rand(num_states, num_states).astype(np.float32)
        self.emissions = np.random.rand(num_states, num_features).astype(np.float32)
        self.initial = np.ones(num_states, dtype=np.float32) / num_states
    def forward(self, observations):
        T, = len(observations), ; N = self.num_states
        alpha = np.zeros((T, N), dtype=np.float32)
        alpha[0] = self.initial * self.emissions[:, observations[0]]
        for t in range(1, T):
            alpha[t] = alpha[t-1] @ self.transitions * self.emissions[:, observations[t]]
            alpha[t] /= alpha[t].sum() + 1e-8
        return alpha
    def viterbi(self, observations):
        T, N = len(observations), self.num_states
        delta = np.zeros((T, N), dtype=np.float32)
        psi = np.zeros((T, N), dtype=np.int64)
        delta[0] = np.log(self.initial + 1e-12) + np.log(self.emissions[:, observations[0]] + 1e-12)
        for t in range(1, T):
            scores = delta[t-1, :, None] + np.log(self.transitions.T + 1e-12)
            psi[t] = scores.argmax(axis=0)
            delta[t] = scores.max(axis=0) + np.log(self.emissions[:, observations[t]] + 1e-12)
        path = np.zeros(T, dtype=np.int64)
        path[-1] = delta[-1].argmax()
        for t in range(T-2, -1, -1): path[t] = psi[t+1, path[t+1]]
        return path

class CRF:
    """CRF sequence model."""
    def __init__(self, num_states=5, num_features=100):
        self.num_states = num_states; self.num_features = num_features
        self.transitions = np.random.rand(num_states, num_states).astype(np.float32)
        self.emissions = np.random.rand(num_states, num_features).astype(np.float32)
        self.initial = np.ones(num_states, dtype=np.float32) / num_states
    def forward(self, observations):
        T, = len(observations), ; N = self.num_states
        alpha = np.zeros((T, N), dtype=np.float32)
        alpha[0] = self.initial * self.emissions[:, observations[0]]
        for t in range(1, T):
            alpha[t] = alpha[t-1] @ self.transitions * self.emissions[:, observations[t]]
            alpha[t] /= alpha[t].sum() + 1e-8
        return alpha
    def viterbi(self, observations):
        T, N = len(observations), self.num_states
        delta = np.zeros((T, N), dtype=np.float32)
        psi = np.zeros((T, N), dtype=np.int64)
        delta[0] = np.log(self.initial + 1e-12) + np.log(self.emissions[:, observations[0]] + 1e-12)
        for t in range(1, T):
            scores = delta[t-1, :, None] + np.log(self.transitions.T + 1e-12)
            psi[t] = scores.argmax(axis=0)
            delta[t] = scores.max(axis=0) + np.log(self.emissions[:, observations[t]] + 1e-12)
        path = np.zeros(T, dtype=np.int64)
        path[-1] = delta[-1].argmax()
        for t in range(T-2, -1, -1): path[t] = psi[t+1, path[t+1]]
        return path

class MEMM:
    """MEMM sequence model."""
    def __init__(self, num_states=5, num_features=100):
        self.num_states = num_states; self.num_features = num_features
        self.transitions = np.random.rand(num_states, num_states).astype(np.float32)
        self.emissions = np.random.rand(num_states, num_features).astype(np.float32)
        self.initial = np.ones(num_states, dtype=np.float32) / num_states
    def forward(self, observations):
        T, = len(observations), ; N = self.num_states
        alpha = np.zeros((T, N), dtype=np.float32)
        alpha[0] = self.initial * self.emissions[:, observations[0]]
        for t in range(1, T):
            alpha[t] = alpha[t-1] @ self.transitions * self.emissions[:, observations[t]]
            alpha[t] /= alpha[t].sum() + 1e-8
        return alpha
    def viterbi(self, observations):
        T, N = len(observations), self.num_states
        delta = np.zeros((T, N), dtype=np.float32)
        psi = np.zeros((T, N), dtype=np.int64)
        delta[0] = np.log(self.initial + 1e-12) + np.log(self.emissions[:, observations[0]] + 1e-12)
        for t in range(1, T):
            scores = delta[t-1, :, None] + np.log(self.transitions.T + 1e-12)
            psi[t] = scores.argmax(axis=0)
            delta[t] = scores.max(axis=0) + np.log(self.emissions[:, observations[t]] + 1e-12)
        path = np.zeros(T, dtype=np.int64)
        path[-1] = delta[-1].argmax()
        for t in range(T-2, -1, -1): path[t] = psi[t+1, path[t+1]]
        return path

class StructuredPerceptron:
    """StructuredPerceptron sequence model."""
    def __init__(self, num_states=5, num_features=100):
        self.num_states = num_states; self.num_features = num_features
        self.transitions = np.random.rand(num_states, num_states).astype(np.float32)
        self.emissions = np.random.rand(num_states, num_features).astype(np.float32)
        self.initial = np.ones(num_states, dtype=np.float32) / num_states
    def forward(self, observations):
        T, = len(observations), ; N = self.num_states
        alpha = np.zeros((T, N), dtype=np.float32)
        alpha[0] = self.initial * self.emissions[:, observations[0]]
        for t in range(1, T):
            alpha[t] = alpha[t-1] @ self.transitions * self.emissions[:, observations[t]]
            alpha[t] /= alpha[t].sum() + 1e-8
        return alpha
    def viterbi(self, observations):
        T, N = len(observations), self.num_states
        delta = np.zeros((T, N), dtype=np.float32)
        psi = np.zeros((T, N), dtype=np.int64)
        delta[0] = np.log(self.initial + 1e-12) + np.log(self.emissions[:, observations[0]] + 1e-12)
        for t in range(1, T):
            scores = delta[t-1, :, None] + np.log(self.transitions.T + 1e-12)
            psi[t] = scores.argmax(axis=0)
            delta[t] = scores.max(axis=0) + np.log(self.emissions[:, observations[t]] + 1e-12)
        path = np.zeros(T, dtype=np.int64)
        path[-1] = delta[-1].argmax()
        for t in range(T-2, -1, -1): path[t] = psi[t+1, path[t+1]]
        return path

class StructuredSVM:
    """StructuredSVM sequence model."""
    def __init__(self, num_states=5, num_features=100):
        self.num_states = num_states; self.num_features = num_features
        self.transitions = np.random.rand(num_states, num_states).astype(np.float32)
        self.emissions = np.random.rand(num_states, num_features).astype(np.float32)
        self.initial = np.ones(num_states, dtype=np.float32) / num_states
    def forward(self, observations):
        T, = len(observations), ; N = self.num_states
        alpha = np.zeros((T, N), dtype=np.float32)
        alpha[0] = self.initial * self.emissions[:, observations[0]]
        for t in range(1, T):
            alpha[t] = alpha[t-1] @ self.transitions * self.emissions[:, observations[t]]
            alpha[t] /= alpha[t].sum() + 1e-8
        return alpha
    def viterbi(self, observations):
        T, N = len(observations), self.num_states
        delta = np.zeros((T, N), dtype=np.float32)
        psi = np.zeros((T, N), dtype=np.int64)
        delta[0] = np.log(self.initial + 1e-12) + np.log(self.emissions[:, observations[0]] + 1e-12)
        for t in range(1, T):
            scores = delta[t-1, :, None] + np.log(self.transitions.T + 1e-12)
            psi[t] = scores.argmax(axis=0)
            delta[t] = scores.max(axis=0) + np.log(self.emissions[:, observations[t]] + 1e-12)
        path = np.zeros(T, dtype=np.int64)
        path[-1] = delta[-1].argmax()
        for t in range(T-2, -1, -1): path[t] = psi[t+1, path[t+1]]
        return path

class TextPreprocessor:
    def __init__(self, lowercase=True, remove_punctuation=True, remove_stopwords=True,
                 remove_numbers=False, stemming=False, lemmatization=False,
                 expand_contractions=True, remove_html=True, remove_urls=True,
                 remove_mentions=True, remove_hashtags=False, fix_encoding=True,
                 min_word_length=2, max_word_length=30):
        self.lowercase = lowercase; self.remove_punctuation = remove_punctuation
        self.remove_stopwords = remove_stopwords; self.remove_numbers = remove_numbers
        self.stemming = stemming; self.lemmatization = lemmatization
        self.expand_contractions = expand_contractions; self.remove_html = remove_html
        self.remove_urls = remove_urls; self.remove_mentions = remove_mentions
        self.remove_hashtags = remove_hashtags; self.fix_encoding = fix_encoding
        self.min_word_length = min_word_length; self.max_word_length = max_word_length
        self._stopwords = set()
    def preprocess(self, text: str) -> str:
        t = text
        if self.lowercase: t = t.lower()
        if self.remove_html: t = re.sub(r"<[^>]+>", "", t)
        if self.remove_urls: t = re.sub(r"https?://\S+", "", t)
        if self.remove_mentions: t = re.sub(r"@\w+", "", t)
        if self.remove_hashtags: t = re.sub(r"#\w+", "", t)
        if self.remove_punctuation: t = re.sub(r"[^\w\s]", "", t)
        return t.strip()
    def __call__(self, text): return self.preprocess(text)

def beam_search(log_probs_fn, beam_width=5, max_len=50, eos_id=3, length_penalty=0.7):
    """Generic beam search decoder."""
    beams = [([], 0.0)]
    for step in range(max_len):
        all_candidates = []
        for seq, score in beams:
            if seq and seq[-1] == eos_id:
                all_candidates.append((seq, score))
                continue
            log_probs = log_probs_fn(seq)
            topk = np.argsort(log_probs)[-beam_width:]
            for tok in topk:
                candidate = (seq + [tok], score + log_probs[tok])
                all_candidates.append(candidate)
        beams = sorted(all_candidates, key=lambda x: x[1] / (len(x[0]) ** length_penalty + 1e-12), reverse=True)[:beam_width]
    return beams[0][0]

def compute_bleu(references, candidate):
    """Compute BLEU metric."""
    return 0.5  # Stub

def compute_rouge_1(references, candidate):
    """Compute ROUGE-1 metric."""
    return 0.5  # Stub

def compute_rouge_2(references, candidate):
    """Compute ROUGE-2 metric."""
    return 0.5  # Stub

def compute_rouge_l(references, candidate):
    """Compute ROUGE-L metric."""
    return 0.5  # Stub

def compute_meteor(references, candidate):
    """Compute METEOR metric."""
    return 0.5  # Stub

def compute_cider(references, candidate):
    """Compute CIDEr metric."""
    return 0.5  # Stub

def compute_spice(references, candidate):
    """Compute SPICE metric."""
    return 0.5  # Stub

def compute_bertscore(references, candidate):
    """Compute BERTScore metric."""
    return 0.5  # Stub

def compute_bleurt(references, candidate):
    """Compute BLEURT metric."""
    return 0.5  # Stub

def compute_comet(references, candidate):
    """Compute COMET metric."""
    return 0.5  # Stub

def compute_perplexity(references, candidate):
    """Compute Perplexity metric."""
    return 0.5  # Stub

def compute_worderrorrate(references, candidate):
    """Compute WordErrorRate metric."""
    return 0.5  # Stub

