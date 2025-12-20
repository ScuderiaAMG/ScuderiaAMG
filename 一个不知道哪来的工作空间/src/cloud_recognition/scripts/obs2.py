#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw
import os
import yaml

# ==================== 圆形参数设置（除分辨率外，其余硬编码）====================
# 圆形参数（单位：米）
RADIUS_OUT = 1.2       # 外圆直径（米）
RADIUS_IN = 0.9        # 内圆直径（米）

# 颜色设置 (RGB格式)
BLACK = (0, 0, 0)      # 黑色
WHITE = (255, 255, 255)  # 白色

# 保存设置
OUTPUT_FOLDER = "../template"        # 输出文件夹
OUTPUT_FILENAME = "obs2.png"         # 输出文件名
# =====================================================

def load_config():
    """从 YAML 文件加载分辨率参数"""
    config_path = "../config/resolution.yaml"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            resolution = config.get('resolution')
            if resolution is None:
                raise ValueError("配置文件中缺少 'resolution' 字段")
            if not isinstance(resolution, (int, float)):
                raise ValueError("resolution 必须是数字")
            return float(resolution)
    except FileNotFoundError:
        raise FileNotFoundError(f"配置文件未找到: {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"YAML 文件解析错误: {e}")

def meters_to_pixels(meters, resolution):
    """将米转换为像素"""
    return int(meters / resolution)

def create_target_image(resolution):
    """创建同心圆观测目标图片（外白内黑）"""
    # 图像尺寸：基于外圆直径 + 边距，确保圆完整显示
    padding_m = 0.2  # 米
    image_size = meters_to_pixels(RADIUS_OUT + padding_m, resolution)
    
    # 图像中心
    center = image_size // 2
    
    # 将直径（米）转为像素，并计算半径
    outer_diameter_px = meters_to_pixels(RADIUS_OUT, resolution)
    inner_diameter_px = meters_to_pixels(RADIUS_IN, RESOLUTION)
    
    outer_radius_px = outer_diameter_px // 2
    inner_radius_px = inner_diameter_px // 2

    # 创建黑色背景图像
    image = Image.new('RGB', (image_size, image_size), BLACK)
    draw = ImageDraw.Draw(image)

    # 外圆边界框（白色）
    outer_left = center - outer_radius_px
    outer_top = center - outer_radius_px
    outer_right = center + outer_radius_px
    outer_bottom = center + outer_radius_px
    draw.ellipse([outer_left, outer_top, outer_right, outer_bottom], fill=WHITE)

    # 内圆边界框（黑色，覆盖中心）
    inner_left = center - inner_radius_px
    inner_top = center - inner_radius_px
    inner_right = center + inner_radius_px
    inner_bottom = center + inner_radius_px
    draw.ellipse([inner_left, inner_top, inner_right, inner_bottom], fill=BLACK)

    return image, image_size, image_size

def ensure_folder_exists(folder_path):
    """确保文件夹存在，如果不存在则创建"""
    if folder_path and not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"已创建文件夹: {folder_path}")

def get_full_path():
    """获取完整的文件保存路径"""
    if OUTPUT_FOLDER:
        ensure_folder_exists(OUTPUT_FOLDER)
        full_path = os.path.join(OUTPUT_FOLDER, OUTPUT_FILENAME)
    else:
        full_path = OUTPUT_FILENAME
    return full_path

def main():
    """主函数"""
    try:
        # 从配置文件加载分辨率
        global RESOLUTION
        RESOLUTION = load_config()
        print(f"从配置文件加载分辨率: {RESOLUTION} m/px")

        # 生成图像
        img, img_width, img_height = create_target_image(RESOLUTION)

        # 获取保存路径
        full_path = get_full_path()

        # 保存图像
        img.save(full_path, 'PNG')
        print(f"图片已保存为: {full_path}")
        print(f"图片尺寸: {img_width} x {img_height} 像素")
        print(f"分辨率: {RESOLUTION} m/px")
        print(f"外圆直径: {RADIUS_OUT}m ({meters_to_pixels(RADIUS_OUT, RESOLUTION)} px)")
        print(f"内圆直径: {RADIUS_IN}m ({meters_to_pixels(RADIUS_IN, RESOLUTION)} px)")
        print("图案: 外白内黑的同心圆观测目标")

        # 显示文件信息
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            print(f"文件大小: {file_size} 字节")

    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()