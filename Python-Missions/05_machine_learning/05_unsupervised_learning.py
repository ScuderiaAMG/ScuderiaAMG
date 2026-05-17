#!/usr/bin/env python3
"""
无监督学习算法从零实现
涵盖：K-Means (含 K-Means++ 初始化)、DBSCAN、层次聚类 (AGNES)、
      高斯混合模型 (GMM/EM)、PCA (特征值分解/SVD/随机化)、
      t-SNE (简化版)、自编码器 (AutoEncoder)
"""

import numpy as np
from typing import Any, Callable
from collections import defaultdict
import math

rng = np.random.default_rng(42)


# ============================================================
# §1  K-Means
# ============================================================

class KMeans:
    """K-Means 聚类 —— O(n·k·d·iter)。"""

    def __init__(self, n_clusters: int = 3, max_iter: int = 300,
                 tol: float = 1e-4, init: str = "kmeans++",
                 random_state: int = 42) -> None:
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.tol = tol
        self.init = init
        self.rng = np.random.default_rng(random_state)
        self.cluster_centers_: np.ndarray | None = None
        self.labels_: np.ndarray | None = None
        self.inertia_: float = 0.0

    def _init_centroids(self, X: np.ndarray) -> np.ndarray:
        if self.init == "random":
            indices = self.rng.choice(len(X), self.n_clusters, replace=False)
            return X[indices].copy()

        if self.init == "kmeans++":
            centroids = [X[self.rng.integers(len(X))]]
            for _ in range(1, self.n_clusters):
                dist_sq = np.min([
                    np.sum((X - c) ** 2, axis=1) for c in centroids
                ], axis=0)
                probs = dist_sq / dist_sq.sum()
                cumsum = np.cumsum(probs)
                r = self.rng.random()
                idx = np.searchsorted(cumsum, r)
                centroids.append(X[idx])
            return np.array(centroids)

        raise ValueError(f"未知初始化方法: {self.init}")

    def fit(self, X: np.ndarray) -> "KMeans":
        centroids = self._init_centroids(X)
        n_samples = X.shape[0]

        for _ in range(self.max_iter):
            # E-step: 分配
            distances = np.zeros((n_samples, self.n_clusters))
            for k in range(self.n_clusters):
                distances[:, k] = np.sum((X - centroids[k]) ** 2, axis=1)
            labels = np.argmin(distances, axis=1)

            # M-step: 更新
            new_centroids = np.zeros_like(centroids)
            for k in range(self.n_clusters):
                mask = labels == k
                if mask.sum() > 0:
                    new_centroids[k] = X[mask].mean(axis=0)
                else:
                    new_centroids[k] = X[self.rng.integers(n_samples)]

            shift = np.sum((new_centroids - centroids) ** 2)
            centroids = new_centroids

            if shift < self.tol:
                break

        self.cluster_centers_ = centroids
        self.labels_ = labels

        # 惯性 (inertia)
        self.inertia_ = 0.0
        for k in range(self.n_clusters):
            mask = labels == k
            self.inertia_ += np.sum((X[mask] - centroids[k]) ** 2)

        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        distances = np.zeros((X.shape[0], self.n_clusters))
        for k in range(self.n_clusters):
            distances[:, k] = np.sum((X - self.cluster_centers_[k]) ** 2, axis=1)  # type: ignore[index]
        return np.argmin(distances, axis=1)


# ============================================================
# §2  DBSCAN
# ============================================================

class DBSCAN:
    """DBSCAN —— 基于密度的聚类，可发现任意形状簇。"""

    def __init__(self, eps: float = 0.5, min_samples: int = 5) -> None:
        self.eps = eps
        self.min_samples = min_samples
        self.labels_: np.ndarray | None = None

    def fit(self, X: np.ndarray) -> "DBSCAN":
        n = len(X)
        labels = np.full(n, -1, dtype=int)    # -1 = 噪声
        cluster_id = 0

        # 预计算邻域
        neighbors_cache: dict[int, list[int]] = {}
        for i in range(n):
            dist = np.sqrt(np.sum((X - X[i]) ** 2, axis=1))
            neighbors_cache[i] = list(np.where(dist <= self.eps)[0])

        for i in range(n):
            if labels[i] != -1:
                continue

            neighbors = neighbors_cache[i]
            if len(neighbors) < self.min_samples:
                labels[i] = -1                   # 噪声
                continue

            cluster_id += 1
            labels[i] = cluster_id
            seeds = neighbors.copy()

            idx = 0
            while idx < len(seeds):
                j = seeds[idx]
                if labels[j] == -1:
                    labels[j] = cluster_id

                if labels[j] <= 0:
                    labels[j] = cluster_id
                    j_neighbors = neighbors_cache[j]
                    if len(j_neighbors) >= self.min_samples:
                        for nb in j_neighbors:
                            if labels[nb] <= 0:
                                seeds.append(nb)
                idx += 1

        self.labels_ = labels
        return self


# ============================================================
# §3  层次聚类 (AGNES)
# ============================================================

class AgglomerativeClustering:
    """自底向上层次聚类 (AGNES)。"""

    def __init__(self, n_clusters: int = 3,
                 linkage: str = "ward") -> None:
        self.n_clusters = n_clusters
        self.linkage = linkage
        self.labels_: np.ndarray | None = None
        self.children_: list[tuple[int, int, float, int]] | None = None

    def fit(self, X: np.ndarray) -> "AgglomerativeClustering":
        n = len(X)

        # 初始化: 每个点一个簇
        clusters: list[set[int]] = [{i} for i in range(n)]

        # 成对距离矩阵
        dist_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(i + 1, n):
                d = np.sqrt(np.sum((X[i] - X[j]) ** 2))
                dist_matrix[i, j] = d
                dist_matrix[j, i] = d

        cluster_dists: dict[tuple[int, int], float] = {}
        for i in range(n):
            for j in range(i + 1, n):
                cluster_dists[(i, j)] = dist_matrix[i, j]

        self.children_ = []

        for iteration in range(n - self.n_clusters):
            # 找最近的两个簇
            if not cluster_dists:
                break
            (a, b), min_dist = min(cluster_dists.items(), key=lambda x: x[1])

            # 合并簇 a 和 b
            new_idx = n + iteration
            size_a = len(clusters[a])
            size_b = len(clusters[b])
            self.children_.append((a, b, min_dist, size_a + size_b))

            new_cluster = clusters[a] | clusters[b]
            clusters[a] = set()
            clusters[b] = set()
            clusters.append(new_cluster)

            # 删除旧距离
            keys_to_remove = [k for k in cluster_dists if a in k or b in k]
            for k in keys_to_remove:
                del cluster_dists[k]

            # 计算新簇与其他簇的距离
            for other in range(len(clusters) - 1):
                if not clusters[other]:
                    continue
                if other in (a, b):
                    continue
                d = self._linkage_distance(
                    X, list(clusters[other]),
                    list(new_cluster), dist_matrix
                )
                cluster_dists[(other, new_idx)] = d

        # 分配标签
        self.labels_ = np.zeros(n, dtype=int)
        label = 0
        for i, cluster in enumerate(clusters):
            if cluster:
                for idx in cluster:
                    self.labels_[idx] = label
                label += 1

        return self

    def _linkage_distance(self, X: np.ndarray,
                          indices_a: list[int], indices_b: list[int],
                          dist_matrix: np.ndarray) -> float:
        if self.linkage == "single":
            return min(dist_matrix[i, j] for i in indices_a for j in indices_b)
        if self.linkage == "complete":
            return max(dist_matrix[i, j] for i in indices_a for j in indices_b)
        if self.linkage == "average":
            return np.mean([dist_matrix[i, j] for i in indices_a for j in indices_b])
        if self.linkage == "ward":
            centroid_a = X[indices_a].mean(axis=0)
            centroid_b = X[indices_b].mean(axis=0)
            na, nb = len(indices_a), len(indices_b)
            return na * nb / (na + nb) * np.sum((centroid_a - centroid_b) ** 2)
        raise ValueError(f"未知链接方法: {self.linkage}")


# ============================================================
# §4  高斯混合模型 (GMM)
# ============================================================

class GaussianMixture:
    """GMM —— EM 算法估计参数。"""

    def __init__(self, n_components: int = 3, max_iter: int = 100,
                 tol: float = 1e-3, reg_covar: float = 1e-6,
                 random_state: int = 42) -> None:
        self.n_components = n_components
        self.max_iter = max_iter
        self.tol = tol
        self.reg_covar = reg_covar
        self.rng = np.random.default_rng(random_state)

        self.weights_: np.ndarray | None = None
        self.means_: np.ndarray | None = None
        self.covariances_: np.ndarray | None = None

    def _multivariate_normal_pdf(self, X: np.ndarray, mean: np.ndarray,
                                  cov: np.ndarray) -> np.ndarray:
        """多元高斯 PDF。"""
        d = X.shape[1]
        cov_reg = cov + self.reg_covar * np.eye(d)
        try:
            L = np.linalg.cholesky(cov_reg)
            log_det = 2 * np.sum(np.log(np.diag(L)))
            diff = X - mean
            # solve triangular
            z = np.linalg.solve(L, diff.T).T
            quad = np.sum(z ** 2, axis=1)
            log_pdf = -0.5 * (d * np.log(2 * np.pi) + log_det + quad)
            return np.exp(log_pdf)
        except np.linalg.LinAlgError:
            return np.zeros(len(X))

    def fit(self, X: np.ndarray) -> "GaussianMixture":
        n, d = X.shape

        # 初始化
        idx = self.rng.choice(n, self.n_components, replace=False)
        self.means_ = X[idx].copy()
        self.covariances_ = np.array([np.eye(d) for _ in range(self.n_components)])
        self.weights_ = np.ones(self.n_components) / self.n_components

        log_likelihood_old = -np.inf

        for _ in range(self.max_iter):
            # E-step: 计算后验概率 (responsibilities)
            resp = np.zeros((n, self.n_components))
            for k in range(self.n_components):
                pdf = self._multivariate_normal_pdf(
                    X, self.means_[k], self.covariances_[k]
                )
                resp[:, k] = self.weights_[k] * pdf

            resp_sum = resp.sum(axis=1, keepdims=True)
            resp_sum = np.clip(resp_sum, 1e-300, None)
            resp /= resp_sum

            # M-step: 更新参数
            nk = resp.sum(axis=0) + 1e-10
            self.weights_ = nk / n
            self.means_ = (resp.T @ X) / nk[:, np.newaxis]

            for k in range(self.n_components):
                diff = X - self.means_[k]
                self.covariances_[k] = (resp[:, k][:, np.newaxis] * diff).T @ diff / nk[k]

            # 检查收敛
            log_likelihood = np.sum(np.log(resp_sum))
            if abs(log_likelihood - log_likelihood_old) < self.tol:
                break
            log_likelihood_old = log_likelihood

        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        resp = np.zeros((X.shape[0], self.n_components))
        for k in range(self.n_components):
            pdf = self._multivariate_normal_pdf(
                X, self.means_[k], self.covariances_[k]  # type: ignore[index]
            )
            resp[:, k] = self.weights_[k] * pdf  # type: ignore[index]
        return np.argmax(resp, axis=1)


# ============================================================
# §5  PCA
# ============================================================

class PCA:
    """主成分分析 —— 三种实现方式。"""

    def __init__(self, n_components: int = 2,
                 method: str = "svd") -> None:
        self.n_components = n_components
        self.method = method
        self.components_: np.ndarray | None = None
        self.explained_variance_: np.ndarray | None = None
        self.mean_: np.ndarray | None = None

    def fit(self, X: np.ndarray) -> "PCA":
        self.mean_ = X.mean(axis=0)
        X_centered = X - self.mean_

        if self.method == "svd":
            U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
            self.components_ = Vt[:self.n_components]
            self.explained_variance_ = (S ** 2) / (X.shape[0] - 1)

        elif self.method == "eigen":
            cov = (X_centered.T @ X_centered) / (X.shape[0] - 1)
            eigenvalues, eigenvectors = np.linalg.eigh(cov)
            idx = np.argsort(eigenvalues)[::-1]
            self.components_ = eigenvectors[:, idx[:self.n_components]].T
            self.explained_variance_ = eigenvalues[idx]

        elif self.method == "randomized":
            n, d = X_centered.shape
            n_oversamples = min(10, d)
            n_random = self.n_components + n_oversamples
            Q = rng.standard_normal((d, n_random))
            Q, _ = np.linalg.qr(X_centered @ Q)
            B = Q.T @ X_centered
            U, S, Vt = np.linalg.svd(B, full_matrices=False)
            self.components_ = Vt[:self.n_components]
            self.explained_variance_ = (S ** 2) / (n - 1)

        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        return (X - self.mean_) @ self.components_.T  # type: ignore[union-attr]

    def inverse_transform(self, X_transformed: np.ndarray) -> np.ndarray:
        return X_transformed @ self.components_ + self.mean_  # type: ignore[union-attr]


# ============================================================
# §6  t-SNE (简化版)
# ============================================================

class TSNE:
    """t-SNE —— 高维数据可视化到 2D/3D。"""

    def __init__(self, n_components: int = 2, perplexity: float = 30.0,
                 max_iter: int = 1000, lr: float = 200.0,
                 random_state: int = 42) -> None:
        self.n_components = n_components
        self.perplexity = perplexity
        self.max_iter = max_iter
        self.lr = lr
        self.rng = np.random.default_rng(random_state)
        self.embedding_: np.ndarray | None = None

    def _compute_pairwise_affinities(self, X: np.ndarray) -> np.ndarray:
        """计算高维空间的条件概率 P。"""
        n = X.shape[0]
        dist_sq = np.zeros((n, n))
        for i in range(n):
            dist_sq[i] = np.sum((X - X[i]) ** 2, axis=1)

        P = np.zeros((n, n))
        target_entropy = math.log(self.perplexity)

        for i in range(n):
            # 二分搜索找到合适的 sigma
            sigma_min, sigma_max = 1e-10, 1e10
            sigma = 1.0

            for _ in range(50):
                p_i = np.exp(-dist_sq[i] / (2 * sigma ** 2))
                p_i[i] = 0
                sum_pi = p_i.sum()
                if sum_pi == 0:
                    break

                H = np.log(sum_pi) + sigma ** (-2) * (dist_sq[i] * p_i).sum() / sum_pi

                if abs(H - target_entropy) < 1e-5:
                    break
                if H > target_entropy:
                    sigma_min = sigma
                else:
                    sigma_max = sigma
                sigma = (sigma_min + sigma_max) / 2

            P[i] = p_i / max(p_i.sum(), 1e-10)

        return (P + P.T) / (2 * n)

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        n, d = X.shape
        P = self._compute_pairwise_affinities(X)
        P = np.maximum(P, 1e-12)

        # 初始化低维嵌入
        Y = self.rng.normal(0, 1e-4, (n, self.n_components))

        # 动量
        velocity = np.zeros_like(Y)
        momentum = 0.5
        final_momentum = 0.8
        momentum_switch = 250

        for iteration in range(self.max_iter):
            # 低维空间距离
            dist_sq_y = np.sum((Y[:, np.newaxis, :] - Y[np.newaxis, :, :]) ** 2, axis=-1)

            # t-分布核
            Q_num = 1 / (1 + dist_sq_y)
            np.fill_diagonal(Q_num, 0)
            Q = Q_num / Q_num.sum()

            # 梯度
            PQ_diff = P - Q
            grad = np.zeros_like(Y)
            for i in range(n):
                grad[i] = 4 * np.sum(
                    (PQ_diff[i] * Q_num[i])[:, np.newaxis] * (Y[i] - Y),
                    axis=0
                )

            if iteration >= momentum_switch:
                momentum = final_momentum

            velocity = momentum * velocity - self.lr * grad
            Y += velocity

            # 中心化
            Y -= Y.mean(axis=0)

            # 早停
            if iteration > 50 and iteration % 100 == 0:
                if np.linalg.norm(grad) < 1e-5:
                    break

        self.embedding_ = Y
        return Y


# ============================================================
# §7  自编码器 (NumPy)
# ============================================================

class AutoEncoder:
    """单隐藏层自编码器 —— 仅用 NumPy。"""

    def __init__(self, input_dim: int, hidden_dim: int,
                 lr: float = 0.01) -> None:
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim

        std = np.sqrt(1.0 / input_dim)
        self.W1 = rng.normal(0, std, (input_dim, hidden_dim))
        self.b1 = np.zeros((1, hidden_dim))
        self.W2 = rng.normal(0, std, (hidden_dim, input_dim))
        self.b2 = np.zeros((1, input_dim))
        self.lr = lr

    def sigmoid(self, x: np.ndarray) -> np.ndarray:
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

    def forward(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        self.z1 = X @ self.W1 + self.b1
        self.h = self.sigmoid(self.z1)
        self.z2 = self.h @ self.W2 + self.b2
        self.reconstructed = self.sigmoid(self.z2)
        return self.h, self.reconstructed

    def backward(self, X: np.ndarray) -> float:
        n = X.shape[0]
        d_recon = (self.reconstructed - X) * self.reconstructed * (1 - self.reconstructed) / n

        self.dW2 = self.h.T @ d_recon
        self.db2 = np.sum(d_recon, axis=0, keepdims=True)

        d_hidden = (d_recon @ self.W2.T) * self.h * (1 - self.h)
        self.dW1 = X.T @ d_hidden
        self.db1 = np.sum(d_hidden, axis=0, keepdims=True)

        self.W2 -= self.lr * self.dW2
        self.b2 -= self.lr * self.db2
        self.W1 -= self.lr * self.dW1
        self.b1 -= self.lr * self.db1

        return float(np.mean((X - self.reconstructed) ** 2))

    def fit(self, X: np.ndarray, epochs: int = 100) -> list[float]:
        losses = []
        for _ in range(epochs):
            self.forward(X)
            loss = self.backward(X)
            losses.append(loss)
        return losses

    def encode(self, X: np.ndarray) -> np.ndarray:
        z1 = X @ self.W1 + self.b1
        return self.sigmoid(z1)


# ============================================================
# §8  演示
# ============================================================

def demo_unsupervised() -> None:
    print("=" * 60)
    print("无监督学习算法演示")
    print("=" * 60)

    # 生成测试数据
    n_samples = 300
    X1 = rng.normal([0, 0], 0.8, (n_samples // 3, 2))
    X2 = rng.normal([4, 4], 0.7, (n_samples // 3, 2))
    X3 = rng.normal([8, 0], 0.9, (n_samples // 3, 2))
    X = np.vstack([X1, X2, X3])

    # K-Means
    print("\n--- K-Means ---")
    km = KMeans(n_clusters=3)
    km.fit(X)
    print(f"中心:\n{km.cluster_centers_}")
    print(f"惯性 (inertia): {km.inertia_:.2f}")
    print(f"各类数量: {np.bincount(km.labels_)}")

    # DBSCAN
    print("\n--- DBSCAN ---")
    db = DBSCAN(eps=1.2, min_samples=5)
    db.fit(X)
    n_clusters = len(set(db.labels_)) - (1 if -1 in db.labels_ else 0)
    n_noise = np.sum(db.labels_ == -1)
    print(f"簇数: {n_clusters}, 噪声点: {n_noise}")

    # 层次聚类
    print("\n--- 层次聚类 (AGNES) ---")
    ac = AgglomerativeClustering(n_clusters=3, linkage="ward")
    ac.fit(X)
    from collections import Counter
    label_counts = Counter(ac.labels_)
    print(f"各类数量: {dict(sorted(label_counts.items()))}")

    # GMM
    print("\n--- 高斯混合模型 ---")
    gmm = GaussianMixture(n_components=3, max_iter=50)
    gmm.fit(X)
    labels = gmm.predict(X)
    print(f"权重: {gmm.weights_}")
    print(f"均值:\n{gmm.means_}")
    print(f"各类数量: {np.bincount(labels)}")

    # PCA
    print("\n--- PCA ---")
    pca = PCA(n_components=1, method="svd")
    pca.fit(X)
    X_transformed = pca.transform(X)
    variance_ratio = pca.explained_variance_[0] / sum(pca.explained_variance_)  # type: ignore[union-attr]
    print(f"主成分 1 方差比: {variance_ratio:.3%}")
    print(f"变换后形状: {X_transformed.shape}")

    # 各方法比较
    print("\n--- PCA 方法比较 (随机数据) ---")
    X_rand = rng.normal(0, 1, (100, 20))
    for method in ["svd", "eigen", "randomized"]:
        p = PCA(n_components=3, method=method)
        p.fit(X_rand)
        print(f"  {method:12}: 方差比={p.explained_variance_[:3].sum() / p.explained_variance_.sum():.3%}")  # type: ignore[union-attr]

    # t-SNE
    print("\n--- t-SNE (小样本) ---")
    X_small = np.vstack([X1[:50], X2[:50], X3[:50]])
    tsne = TSNE(n_components=2, perplexity=15, max_iter=300)
    Y_tsne = tsne.fit_transform(X_small)
    print(f"t-SNE 嵌入: {Y_tsne.shape}, 范围: x∈[{Y_tsne[:,0].min():.1f},{Y_tsne[:,0].max():.1f}], "
          f"y∈[{Y_tsne[:,1].min():.1f},{Y_tsne[:,1].max():.1f}]")

    # AutoEncoder
    print("\n--- AutoEncoder ---")
    data_ae = rng.random((200, 20))
    ae = AutoEncoder(input_dim=20, hidden_dim=8, lr=0.1)
    losses = ae.fit(data_ae, epochs=100)
    encoded = ae.encode(data_ae)
    print(f"编码维度: {encoded.shape}")
    print(f"初始损失: {losses[0]:.4f}")
    print(f"最终损失: {losses[-1]:.4f}")


if __name__ == "__main__":
    demo_unsupervised()
    print("\n✅ 无监督学习篇执行完毕!")
