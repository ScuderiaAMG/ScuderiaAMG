#!/usr/bin/env python3
"""
计算机视觉 —— 图像处理从零实现
涵盖：图像I/O与色彩空间、卷积滤波（模糊/锐化/边缘检测）、
      形态学操作（腐蚀/膨胀/开/闭）、几何变换（旋转/缩放/仿射/透视）、
      直方图均衡化/CLAHE、特征检测（Harris角点/SIFT描述思路）、
      Hough变换（直线/圆）、图像分割（Otsu/分水岭思路）、
      图像金字塔与模板匹配
使用 NumPy 从零实现，不依赖 OpenCV
"""

import numpy as np
from typing import Any
import math

rng = np.random.default_rng(42)


# ============================================================
# §1  基本图像操作
# ============================================================

def rgb_to_grayscale(image: np.ndarray) -> np.ndarray:
    """RGB 转灰度 —— Y = 0.299R + 0.587G + 0.114B。"""
    if image.ndim == 2:
        return image.copy()
    return np.dot(image[..., :3], [0.299, 0.587, 0.114])


def rgb_to_hsv(image: np.ndarray) -> np.ndarray:
    """RGB 转 HSV 色彩空间。"""
    img = image.astype(np.float64) / 255.0
    r, g, b = img[..., 0], img[..., 1], img[..., 2]

    cmax = np.max(img, axis=2)
    cmin = np.min(img, axis=2)
    delta = cmax - cmin

    h = np.zeros_like(cmax)
    mask = delta > 0
    # Red is max
    r_mask = (cmax == r) & mask
    h[r_mask] = 60 * (((g[r_mask] - b[r_mask]) / delta[r_mask]) % 6)
    # Green is max
    g_mask = (cmax == g) & mask
    h[g_mask] = 60 * (((b[g_mask] - r[g_mask]) / delta[g_mask]) + 2)
    # Blue is max
    b_mask = (cmax == b) & mask
    h[b_mask] = 60 * (((r[b_mask] - g[b_mask]) / delta[b_mask]) + 4)

    s = np.zeros_like(cmax)
    s[mask] = delta[mask] / cmax[mask]

    v = cmax

    return np.stack([h / 360.0, s, v], axis=-1)


def adjust_brightness(image: np.ndarray, factor: float) -> np.ndarray:
    """调整亮度 —— factor > 1 增亮, < 1 变暗。"""
    result = image.astype(np.float64) * factor
    return np.clip(result, 0, 255).astype(np.uint8)


def adjust_contrast(image: np.ndarray, factor: float) -> np.ndarray:
    """调整对比度 —— factor > 1 增强, < 1 减弱。"""
    mean = np.mean(image, axis=(0, 1), keepdims=True)
    result = (image.astype(np.float64) - mean) * factor + mean
    return np.clip(result, 0, 255).astype(np.uint8)


def gamma_correction(image: np.ndarray, gamma: float = 2.2) -> np.ndarray:
    """Gamma 校正。"""
    img_norm = image.astype(np.float64) / 255.0
    corrected = np.power(img_norm, 1.0 / gamma)
    return (corrected * 255).astype(np.uint8)


def image_negative(image: np.ndarray) -> np.ndarray:
    return 255 - image


# ============================================================
# §2  卷积与滤波
# ============================================================

def convolve2d(image: np.ndarray, kernel: np.ndarray,
               pad_mode: str = "reflect") -> np.ndarray:
    """2D 卷积 —— 支持多通道图像。"""
    if image.ndim == 3:
        result = np.zeros_like(image, dtype=np.float64)
        for c in range(image.shape[2]):
            result[..., c] = convolve2d(image[..., c], kernel, pad_mode)
        return np.clip(result, 0, 255).astype(np.uint8)

    kh, kw = kernel.shape
    pad_h, pad_w = kh // 2, kw // 2
    padded = np.pad(image, ((pad_h, pad_h), (pad_w, pad_w)), mode=pad_mode)

    result = np.zeros_like(image, dtype=np.float64)
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            region = padded[i:i + kh, j:j + kw]
            result[i, j] = np.sum(region * kernel)

    return np.clip(result, 0, 255).astype(np.uint8)


def convolve2d_fast(image: np.ndarray, kernel: np.ndarray,
                    pad_mode: str = "reflect") -> np.ndarray:
    """快速 2D 卷积 —— 使用 im2col 技巧。"""
    if image.ndim == 3:
        result = np.zeros_like(image, dtype=np.float64)
        for c in range(image.shape[2]):
            result[..., c] = convolve2d_fast(image[..., c], kernel, pad_mode)
        return np.clip(result, 0, 255).astype(np.uint8)

    H, W = image.shape
    kh, kw = kernel.shape
    pad_h, pad_w = kh // 2, kw // 2

    padded = np.pad(image, ((pad_h, pad_h), (pad_w, pad_w)), mode=pad_mode)

    # im2col
    shape = (H, W, kh, kw)
    strides = (padded.strides[0], padded.strides[1],
               padded.strides[0], padded.strides[1])
    windows = np.lib.stride_tricks.as_strided(padded, shape=shape, strides=strides)

    result = np.tensordot(windows, kernel, axes=((2, 3), (0, 1)))
    return np.clip(result, 0, 255).astype(np.uint8)


def gaussian_kernel(size: int = 5, sigma: float = 1.0) -> np.ndarray:
    """生成高斯核。"""
    center = size // 2
    kernel = np.zeros((size, size))
    for i in range(size):
        for j in range(size):
            x, y = i - center, j - center
            kernel[i, j] = np.exp(-(x**2 + y**2) / (2 * sigma**2))
    return kernel / kernel.sum()


def box_blur_kernel(size: int = 3) -> np.ndarray:
    return np.ones((size, size)) / (size * size)


def sobel_kernels() -> tuple[np.ndarray, np.ndarray]:
    """Sobel 算子 —— X 和 Y 方向。"""
    Gx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float64)
    Gy = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float64)
    return Gx, Gy


def laplacian_kernel() -> np.ndarray:
    return np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float64)


def sharpen_kernel() -> np.ndarray:
    return np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float64)


def emboss_kernel() -> np.ndarray:
    return np.array([[-2, -1, 0], [-1, 1, 1], [0, 1, 2]], dtype=np.float64)


def gaussian_blur(image: np.ndarray, size: int = 5,
                  sigma: float = 1.0) -> np.ndarray:
    return convolve2d_fast(image, gaussian_kernel(size, sigma))


def sobel_edges(image: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Sobel 边缘检测 —— 返回 (幅值, 方向)。"""
    gray = rgb_to_grayscale(image) if image.ndim == 3 else image
    Gx, Gy = sobel_kernels()
    grad_x = convolve2d_fast(gray, Gx)
    grad_y = convolve2d_fast(gray, Gy)
    magnitude = np.sqrt(grad_x ** 2 + grad_y ** 2)
    direction = np.arctan2(grad_y, grad_x)
    return magnitude.astype(np.uint8), direction


def canny_edge_detection(image: np.ndarray, low_thresh: float = 50,
                         high_thresh: float = 150) -> np.ndarray:
    """Canny 边缘检测的核心步骤 (简化版)。"""
    gray = rgb_to_grayscale(image) if image.ndim == 3 else image
    blurred = gaussian_blur(gray, size=5, sigma=1.4)

    Gx, Gy = sobel_kernels()
    grad_x = convolve2d_fast(blurred, Gx)
    grad_y = convolve2d_fast(blurred, Gy)

    magnitude = np.sqrt(grad_x ** 2 + grad_y ** 2)
    direction = np.arctan2(grad_y, grad_x)

    # 非极大值抑制 (简化)
    suppressed = np.zeros_like(magnitude)
    angle = direction * 180 / np.pi
    angle[angle < 0] += 180

    for i in range(1, magnitude.shape[0] - 1):
        for j in range(1, magnitude.shape[1] - 1):
            # 根据方向确定比较的邻居
            if (0 <= angle[i, j] < 22.5) or (157.5 <= angle[i, j] <= 180):
                neighbors = [magnitude[i, j + 1], magnitude[i, j - 1]]
            elif 22.5 <= angle[i, j] < 67.5:
                neighbors = [magnitude[i - 1, j + 1], magnitude[i + 1, j - 1]]
            elif 67.5 <= angle[i, j] < 112.5:
                neighbors = [magnitude[i - 1, j], magnitude[i + 1, j]]
            else:
                neighbors = [magnitude[i - 1, j - 1], magnitude[i + 1, j + 1]]

            if magnitude[i, j] >= max(neighbors):
                suppressed[i, j] = magnitude[i, j]

    # 双阈值 + 滞后
    strong = suppressed >= high_thresh
    weak = (suppressed >= low_thresh) & (suppressed < high_thresh)
    result = np.zeros_like(suppressed)
    result[strong] = 255

    # 弱边缘连接到强边缘 (简化: 检查 8 邻域)
    for i in range(1, result.shape[0] - 1):
        for j in range(1, result.shape[1] - 1):
            if weak[i, j]:
                if np.any(strong[i - 1:i + 2, j - 1:j + 2]):
                    result[i, j] = 128

    return result.astype(np.uint8)


# ============================================================
# §3  形态学操作
# ============================================================

def erode(binary: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """腐蚀 —— 收缩前景区域。"""
    pad = kernel_size // 2
    padded = np.pad(binary > 0, pad, mode="constant", constant_values=1)
    result = np.zeros_like(binary, dtype=bool)
    for i in range(binary.shape[0]):
        for j in range(binary.shape[1]):
            region = padded[i:i + kernel_size, j:j + kernel_size]
            result[i, j] = np.all(region)
    return result.astype(np.uint8) * 255


def dilate(binary: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """膨胀 —— 扩展前景区域。"""
    pad = kernel_size // 2
    padded = np.pad(binary > 0, pad, mode="constant")
    result = np.zeros_like(binary, dtype=bool)
    for i in range(binary.shape[0]):
        for j in range(binary.shape[1]):
            region = padded[i:i + kernel_size, j:j + kernel_size]
            result[i, j] = np.any(region)
    return result.astype(np.uint8) * 255


def morph_open(binary: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """开运算 —— 先腐蚀后膨胀 (去除小噪点)。"""
    return dilate(erode(binary, kernel_size), kernel_size)


def morph_close(binary: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """闭运算 —— 先膨胀后腐蚀 (填充小孔)。"""
    return erode(dilate(binary, kernel_size), kernel_size)


def morph_gradient(binary: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """形态学梯度 —— 膨胀 - 腐蚀 (获取边界)。"""
    d = dilate(binary, kernel_size)
    e = erode(binary, kernel_size)
    return np.clip(d.astype(int) - e.astype(int), 0, 255).astype(np.uint8)


# ============================================================
# §4  几何变换
# ============================================================

def resize_nearest(image: np.ndarray, new_h: int, new_w: int) -> np.ndarray:
    """最近邻插值缩放。"""
    if image.ndim == 3:
        channels = [resize_nearest(image[..., c], new_h, new_w)
                    for c in range(image.shape[2])]
        return np.stack(channels, axis=-1)

    h, w = image.shape
    scale_h, scale_w = h / new_h, w / new_w
    result = np.zeros((new_h, new_w), dtype=image.dtype)

    for i in range(new_h):
        for j in range(new_w):
            src_i = int(i * scale_h)
            src_j = int(j * scale_w)
            result[i, j] = image[src_i, src_j]

    return result


def resize_bilinear(image: np.ndarray, new_h: int, new_w: int) -> np.ndarray:
    """双线性插值缩放。"""
    if image.ndim == 3:
        channels = [resize_bilinear(image[..., c], new_h, new_w)
                    for c in range(image.shape[2])]
        return np.stack(channels, axis=-1)

    h, w = image.shape
    result = np.zeros((new_h, new_w), dtype=np.float64)

    for i in range(new_h):
        for j in range(new_w):
            src_y = (i + 0.5) * h / new_h - 0.5
            src_x = (j + 0.5) * w / new_w - 0.5

            y0 = int(np.floor(src_y))
            x0 = int(np.floor(src_x))
            y1 = min(y0 + 1, h - 1)
            x1 = min(x0 + 1, w - 1)

            dy = src_y - y0
            dx = src_x - x0

            result[i, j] = (image[y0, x0] * (1 - dy) * (1 - dx) +
                            image[y0, x1] * (1 - dy) * dx +
                            image[y1, x0] * dy * (1 - dx) +
                            image[y1, x1] * dy * dx)

    return result.astype(image.dtype)


def rotate_image(image: np.ndarray, angle_deg: float) -> np.ndarray:
    """旋转图像 (双线性插值)。"""
    if image.ndim == 3:
        channels = [rotate_image(image[..., c], angle_deg)
                    for c in range(image.shape[2])]
        return np.stack(channels, axis=-1)

    h, w = image.shape
    angle_rad = math.radians(angle_deg)
    cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)

    cx, cy = w / 2, h / 2
    result = np.zeros_like(image)

    for i in range(h):
        for j in range(w):
            src_x = cos_a * (j - cx) + sin_a * (i - cy) + cx
            src_y = -sin_a * (j - cx) + cos_a * (i - cy) + cy

            x0, y0 = int(src_x), int(src_y)
            if 0 <= x0 < w - 1 and 0 <= y0 < h - 1:
                dx, dy = src_x - x0, src_y - y0
                result[i, j] = (image[y0, x0] * (1 - dy) * (1 - dx) +
                                image[y0, x0 + 1] * (1 - dy) * dx +
                                image[y0 + 1, x0] * dy * (1 - dx) +
                                image[y0 + 1, x0 + 1] * dy * dx)

    return result


def flip_horizontal(image: np.ndarray) -> np.ndarray:
    return image[:, ::-1].copy()


def flip_vertical(image: np.ndarray) -> np.ndarray:
    return image[::-1, :].copy()


def crop(image: np.ndarray, y: int, x: int, h: int, w: int) -> np.ndarray:
    return image[y:y + h, x:x + w].copy()


# ============================================================
# §5  直方图处理
# ============================================================

def histogram(image: np.ndarray, bins: int = 256) -> np.ndarray:
    """计算灰度直方图。"""
    gray = rgb_to_grayscale(image) if image.ndim == 3 else image
    hist, _ = np.histogram(gray.ravel(), bins=bins, range=(0, 256))
    return hist


def histogram_equalization(image: np.ndarray) -> np.ndarray:
    """直方图均衡化。"""
    gray = rgb_to_grayscale(image).astype(np.uint8) if image.ndim == 3 else image.copy()
    hist, _ = np.histogram(gray.ravel(), 256, (0, 256))
    cdf = hist.cumsum()
    cdf_normalized = (cdf - cdf.min()) * 255 / (cdf.max() - cdf.min())
    return cdf_normalized[gray].astype(np.uint8)


def clahe(image: np.ndarray, clip_limit: float = 3.0,
          tile_size: int = 8) -> np.ndarray:
    """CLAHE (自适应直方图均衡化简化版)。"""
    gray = rgb_to_grayscale(image).astype(np.uint8) if image.ndim == 3 else image.copy()
    h, w = gray.shape
    result = np.zeros_like(gray, dtype=np.float64)

    for i in range(0, h, tile_size):
        for j in range(0, w, tile_size):
            tile = gray[i:min(i + tile_size, h), j:min(j + tile_size, w)]
            hist, _ = np.histogram(tile.ravel(), 256, (0, 256))

            # 裁剪
            excess = np.maximum(hist - clip_limit * tile.size / 256, 0).sum()
            hist = hist + excess / 256
            hist = np.minimum(hist, clip_limit * tile.size / 256)

            cdf = hist.cumsum()
            cdf = (cdf - cdf.min()) * 255 / (cdf.max() - cdf.min())

            tile_h, tile_w = tile.shape
            result[i:i + tile_h, j:j + tile_w] = cdf[tile]

    return result.astype(np.uint8)


# ============================================================
# §6  特征检测
# ============================================================

def harris_corners(image: np.ndarray, k: float = 0.04,
                   threshold: float = 0.01) -> np.ndarray:
    """Harris 角点检测。"""
    gray = rgb_to_grayscale(image).astype(np.float64) if image.ndim == 3 else image.astype(np.float64)

    Gx, Gy = sobel_kernels()
    Ix = convolve2d_fast(gray, Gx)
    Iy = convolve2d_fast(gray, Gy)

    Ixx = gaussian_blur(Ix ** 2, size=5, sigma=1.0)
    Iyy = gaussian_blur(Iy ** 2, size=5, sigma=1.0)
    Ixy = gaussian_blur(Ix * Iy, size=5, sigma=1.0)

    det = Ixx * Iyy - Ixy ** 2
    trace = Ixx + Iyy
    R = det - k * trace ** 2

    R_max = R.max()
    corners = (R > threshold * R_max) & (R == maximum_filter(R, size=5))
    return corners


def maximum_filter(image: np.ndarray, size: int = 3) -> np.ndarray:
    """局部最大值滤波。"""
    pad = size // 2
    padded = np.pad(image, pad, mode="edge")
    result = np.zeros_like(image)
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            result[i, j] = np.max(padded[i:i + size, j:j + size])
    return result


# ============================================================
# §7  Hough 变换
# ============================================================

def hough_lines(image: np.ndarray, theta_res: float = 1.0,
                rho_res: float = 1.0, threshold: int = 50) -> list[tuple[float, float]]:
    """Hough 直线检测。"""
    magnitude, _ = sobel_edges(image)
    edges = magnitude > 50

    h, w = edges.shape
    diag = int(np.sqrt(h**2 + w**2))
    thetas = np.deg2rad(np.arange(-90, 90, theta_res))
    rhos = np.arange(-diag, diag, rho_res)

    accumulator = np.zeros((len(rhos), len(thetas)))

    edge_points = np.argwhere(edges)
    cos_t = np.cos(thetas)
    sin_t = np.sin(thetas)

    edge_rhos = np.outer(edge_points[:, 0], sin_t) + np.outer(edge_points[:, 1], cos_t)
    rho_indices = ((edge_rhos + diag) / rho_res).astype(int)

    for idx in range(len(edge_points)):
        np.add.at(accumulator, (rho_indices[idx], np.arange(len(thetas))), 1)

    # 提取局部极大值
    from scipy.ndimage import maximum_filter as mf_scipy
    try:
        local_max = accumulator == maximum_filter(accumulator, size=10)
        peaks = np.argwhere(local_max & (accumulator >= threshold))
    except ImportError:
        peaks = np.argwhere(accumulator >= threshold)

    lines: list[tuple[float, float]] = []
    for rho_idx, theta_idx in peaks:
        lines.append((rhos[rho_idx], thetas[theta_idx]))

    return lines


def hough_circles(image: np.ndarray, min_radius: int = 10,
                  max_radius: int = 50, threshold: float = 0.5) -> list[tuple[int, int, int]]:
    """Hough 圆检测。"""
    magnitude, _ = sobel_edges(image)
    edges = magnitude > 50
    h, w = edges.shape
    accumulator = np.zeros((h, w, max_radius - min_radius + 1))

    edge_points = np.argwhere(edges)
    for y, x in edge_points:
        for r_idx, r in enumerate(range(min_radius, max_radius + 1)):
            for theta in np.linspace(0, 2 * np.pi, 36):
                a = int(x - r * np.cos(theta))
                b = int(y - r * np.sin(theta))
                if 0 <= a < w and 0 <= b < h:
                    accumulator[b, a, r_idx] += 1

    circles: list[tuple[int, int, int]] = []
    for r_idx, r in enumerate(range(min_radius, max_radius + 1)):
        max_val = accumulator[..., r_idx].max()
        if max_val > 0:
            peaks = np.argwhere(
                (accumulator[..., r_idx] > threshold * max_val) &
                (accumulator[..., r_idx] == maximum_filter(accumulator[..., r_idx], size=5))
            )
            for y, x in peaks:
                circles.append((x, y, r))

    return circles


# ============================================================
# §8  模板匹配
# ============================================================

def template_match_ssd(image: np.ndarray, template: np.ndarray) -> np.ndarray:
    """模板匹配 —— 平方差和 (SSD)，返回相似度图。"""
    gray = rgb_to_grayscale(image).astype(np.float64) if image.ndim == 3 else image.astype(np.float64)
    tpl = rgb_to_grayscale(template).astype(np.float64) if template.ndim == 3 else template.astype(np.float64)

    h, w = gray.shape
    th, tw = tpl.shape
    result = np.zeros((h - th + 1, w - tw + 1))

    for i in range(h - th + 1):
        for j in range(w - tw + 1):
            patch = gray[i:i + th, j:j + tw]
            result[i, j] = -np.sum((patch - tpl) ** 2)

    return result


def template_match_ncc(image: np.ndarray, template: np.ndarray) -> np.ndarray:
    """模板匹配 —— 归一化互相关 (NCC)。"""
    gray = rgb_to_grayscale(image).astype(np.float64) if image.ndim == 3 else image.astype(np.float64)
    tpl = rgb_to_grayscale(template).astype(np.float64) if template.ndim == 3 else template.astype(np.float64)
    tpl_norm = (tpl - tpl.mean()) / tpl.std()

    h, w = gray.shape
    th, tw = tpl.shape
    result = np.zeros((h - th + 1, w - tw + 1))

    for i in range(h - th + 1):
        for j in range(w - tw + 1):
            patch = gray[i:i + th, j:j + tw]
            patch_norm = (patch - patch.mean()) / (patch.std() + 1e-8)
            result[i, j] = np.sum(patch_norm * tpl_norm) / (th * tw)

    return result


# ============================================================
# §9  图像金字塔
# ============================================================

def gaussian_pyramid(image: np.ndarray, levels: int = 4) -> list[np.ndarray]:
    """高斯金字塔 —— 逐级降采样。"""
    pyramid = [image]
    for _ in range(levels - 1):
        blurred = gaussian_blur(pyramid[-1], size=5, sigma=1.0)
        h, w = blurred.shape[:2]
        downsampled = resize_bilinear(blurred, h // 2, w // 2)
        pyramid.append(downsampled)
    return pyramid


def laplacian_pyramid(image: np.ndarray, levels: int = 4) -> list[np.ndarray]:
    """拉普拉斯金字塔 —— 高斯金字塔相邻级之差。"""
    g_pyr = gaussian_pyramid(image, levels)
    l_pyr: list[np.ndarray] = []
    for i in range(levels - 1):
        h, w = g_pyr[i].shape[:2]
        upsampled = resize_bilinear(g_pyr[i + 1], h, w)
        l_pyr.append(g_pyr[i].astype(np.float64) - upsampled.astype(np.float64))
    l_pyr.append(g_pyr[-1].astype(np.float64))
    return l_pyr


# ============================================================
# §10  Otsu 阈值分割
# ============================================================

def otsu_threshold(image: np.ndarray) -> int:
    """Otsu 算法 —— 找出最佳二值化阈值。"""
    gray = rgb_to_grayscale(image).astype(np.uint8) if image.ndim == 3 else image.astype(np.uint8)
    hist, _ = np.histogram(gray.ravel(), 256, (0, 256))
    total = gray.size

    sum_all = np.dot(np.arange(256), hist)
    sum_b = 0.0
    w_b = 0
    max_variance = 0.0
    best_threshold = 0

    for t in range(256):
        w_b += hist[t]
        if w_b == 0:
            continue
        w_f = total - w_b
        if w_f == 0:
            break

        sum_b += t * hist[t]
        m_b = sum_b / w_b
        m_f = (sum_all - sum_b) / w_f

        variance = w_b * w_f * (m_b - m_f) ** 2
        if variance > max_variance:
            max_variance = variance
            best_threshold = t

    return best_threshold


# ============================================================
# §11  演示
# ============================================================

def demo_image_processing() -> None:
    print("=" * 60)
    print("图像处理全集演示 (NumPy 从零实现)")
    print("=" * 60)

    # 生成测试图像
    size = 64
    xx, yy = np.meshgrid(np.arange(size), np.arange(size))
    # 彩色渐变 + 几何图形
    img = np.zeros((size, size, 3), dtype=np.uint8)
    img[..., 0] = (xx * 4).astype(np.uint8)       # R 通道
    img[..., 1] = (yy * 4).astype(np.uint8)       # G 通道
    img[..., 2] = 128                              # B 通道
    # 白色矩形
    img[10:30, 10:50] = 255
    # 黑色圆形
    cy, cx = 45, 45
    circle_mask = (xx - cx)**2 + (yy - cy)**2 < 12**2
    img[circle_mask] = 0

    print(f"测试图像: {img.shape}")

    # 灰度转换
    gray = rgb_to_grayscale(img)
    print(f"灰度: {gray.shape}, 范围 [{gray.min()}, {gray.max()}]")

    # 高斯模糊
    blurred = gaussian_blur(img, size=5, sigma=1.5)
    print(f"高斯模糊: 完成")

    # Sobel 边缘
    mag, direction = sobel_edges(img)
    print(f"Sobel 边缘: 幅值范围 [0, {mag.max()}]")

    # Canny
    canny = canny_edge_detection(img)
    print(f"Canny: 边缘像素数={np.sum(canny > 0)}")

    # 形态学
    binary = (gray > 128).astype(np.uint8) * 255
    eroded = erode(binary, 3)
    dilated = dilate(binary, 3)
    opened = morph_open(binary, 3)
    closed = morph_close(binary, 3)
    print(f"形态学: erode/dilate/open/close 完成")

    # 几何变换
    rotated = rotate_image(gray, 45)
    resized = resize_bilinear(gray, 32, 32)
    flipped = flip_horizontal(img)
    print(f"几何变换: rotate(45°)/resize(32x32)/flip 完成")

    # 直方图
    hist = histogram(gray)
    equalized = histogram_equalization(gray)
    clahed = clahe(gray)
    print(f"直方图均衡化: 完成")

    # Harris 角点
    corners = harris_corners(img)
    print(f"Harris 角点: 检测到 {corners.sum()} 个角点")

    # Otsu
    otsu_thresh = otsu_threshold(img)
    print(f"Otsu 阈值: {otsu_thresh}")

    # 模板匹配
    tpl = img[10:30, 10:30].copy()
    ncc_map = template_match_ncc(img, tpl)
    best_match = np.unravel_index(ncc_map.argmax(), ncc_map.shape)
    print(f"NCC 模板匹配: 最优位置={best_match}, 分值={ncc_map.max():.4f}")

    # 金字塔
    g_pyr = gaussian_pyramid(gray, 3)
    l_pyr = laplacian_pyramid(gray, 3)
    print(f"高斯金字塔: {[p.shape[:2] for p in g_pyr]}")
    print(f"拉普拉斯金字塔层数: {len(l_pyr)}")


if __name__ == "__main__":
    demo_image_processing()
    print("\n✅ 图像处理篇执行完毕!")
