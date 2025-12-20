#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw
import os
import yaml

# ==================== 全局设置 ====================
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
OUTPUT_FOLDER = "../template"
OUTPUT_NAMES = {
    'obs1': 'obs1.png',
    'obs2': 'obs2.png',
    'obs3': 'obs3.png',
    'obs4': 'obs4.png'
}
CONFIG_PATH = "../config/obs.yaml"
# =================================================

def load_config():
    """加载 YAML 配置文件"""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"配置文件未找到: {CONFIG_PATH}")
    except yaml.YAMLError as e:
        raise ValueError(f"YAML 解析错误: {e}")

def meters_to_pixels(meters, resolution):
    """米转像素"""
    return int(meters / resolution)

def ensure_folder_exists(folder_path):
    """创建输出文件夹"""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"已创建文件夹: {folder_path}")

def save_image(image, name):
    """保存图像"""
    full_path = os.path.join(OUTPUT_FOLDER, name)
    image.save(full_path, 'PNG')
    print(f"✅ 保存: {full_path} | 尺寸: {image.size[0]}x{image.size[1]} px")
    if os.path.exists(full_path):
        print(f"   文件大小: {os.path.getsize(full_path)} 字节")

# === 图案生成函数 ===

def create_obs1(config, resolution):
    """外白内黑矩形"""
    p = config
    w = meters_to_pixels(p['outer_width'], resolution)
    h = meters_to_pixels(p['outer_height'], resolution)
    iw = meters_to_pixels(p['inner_width'], resolution)
    ih = meters_to_pixels(p['inner_height'], resolution)

    img = Image.new('RGB', (w, h), COLOR_WHITE)
    draw = ImageDraw.Draw(img)

    cx, cy = w // 2, h // 2
    left = cx - iw // 2
    top = cy - ih // 2
    right = left + iw
    bottom = top + ih

    draw.rectangle([left, top, right, bottom], fill=COLOR_BLACK)
    return img

def create_obs2(config, resolution):
    """同心圆：外白内黑"""
    p = config
    padding_px = meters_to_pixels(p['padding'], resolution)
    diameter_px = meters_to_pixels(p['outer_diameter'], resolution)
    size = diameter_px + 2 * padding_px

    img = Image.new('RGB', (size, size), COLOR_BLACK)
    draw = ImageDraw.Draw(img)

    center = size // 2
    r_outer = meters_to_pixels(p['outer_diameter'], resolution) // 2
    r_inner = meters_to_pixels(p['inner_diameter'], resolution) // 2

    # 外圆（白）
    draw.ellipse([
        center - r_outer, center - r_outer,
        center + r_outer, center + r_outer
    ], fill=COLOR_WHITE)

    # 内圆（黑）
    draw.ellipse([
        center - r_inner, center - r_inner,
        center + r_inner, center + r_inner
    ], fill=COLOR_BLACK)

    return img

def create_obs3(config, resolution):
    """左右双黑块 + 中间白柱"""
    p = config
    w = meters_to_pixels(p['outer_width'], resolution)
    h = meters_to_pixels(p['outer_height'], resolution)
    iw = meters_to_pixels(p['inner_width'], resolution)
    ih = meters_to_pixels(p['inner_height'], resolution)
    cw = meters_to_pixels(p['column_width'], resolution)

    total_inner_width = 2 * iw + cw
    start_x = (w - total_inner_width) // 2
    center_y = h // 2
    top_y = center_y - ih // 2
    bottom_y = center_y + ih // 2

    img = Image.new('RGB', (w, h), COLOR_WHITE)
    draw = ImageDraw.Draw(img)

    # 左黑块
    draw.rectangle([start_x, top_y, start_x + iw, bottom_y], fill=COLOR_BLACK)
    # 右黑块
    draw.rectangle([start_x + iw + cw, top_y, start_x + 2*iw + cw, bottom_y], fill=COLOR_BLACK)

    return img

def create_obs4(config, resolution):
    """上下双黑块 + 中间白条"""
    p = config
    w = meters_to_pixels(p['outer_width'], resolution)
    h = meters_to_pixels(p['outer_height'], resolution)
    iw = meters_to_pixels(p['inner_width'], resolution)
    ih = meters_to_pixels(p['inner_height'], resolution)
    ch = meters_to_pixels(p['column_width'], resolution)

    total_inner_height = 2 * ih + ch
    start_y = (h - total_inner_height) // 2
    center_x = w // 2
    left_x = center_x - iw // 2
    right_x = left_x + iw

    img = Image.new('RGB', (w, h), COLOR_WHITE)
    draw = ImageDraw.Draw(img)

    # 上黑块
    draw.rectangle([left_x, start_y, right_x, start_y + ih], fill=COLOR_BLACK)
    # 下黑块
    draw.rectangle([left_x, start_y + ih + ch, right_x, start_y + 2*ih + ch], fill=COLOR_BLACK)

    return img

# === 主函数 ===
def main():
    try:
        # 加载配置
        config = load_config()
        resolution = config['resolution']
        print(f"📊 使用分辨率: {resolution} m/px\n")

        # 创建输出目录
        ensure_folder_exists(OUTPUT_FOLDER)

        # 生成每张图
        generators = {
            'obs1': create_obs1,
            'obs2': create_obs2,
            'obs3': create_obs3,
            'obs4': create_obs4
        }

        for key, func in generators.items():
            if key not in config:
                print(f"⚠️ 跳过 {key}: 配置缺失")
                continue

            print(f"🎨 生成 {key}: {config[key]['type']}")
            img = func(config[key], resolution)
            save_image(img, OUTPUT_NAMES[key])
            print()

    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    main()