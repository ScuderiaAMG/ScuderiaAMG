#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw
import os
import yaml

# ==================== 矩形参数设置（除分辨率外，其余硬编码）====================
# 外框参数（单位：米）
OUTER_WIDTH = 1.36        # 外框宽度(米)
OUTER_HEIGHT = 2.28       # 外框高度(米)

# 内框参数（单位：米）
INNER_WIDTH = 1.18        # 内框宽度(米)
INNER_HEIGHT = 1.0       # 内框高度(米)

# 中间柱子宽度（单位：米）
COLUMN_WIDTH = 0.09       # 中间水平隔断的宽度(米) —— 注意：这里是上下分隔，所以是“横条”

# 颜色设置 (RGB格式)
BLACK = (0, 0, 0)        # 黑色
WHITE = (255, 255, 255)  # 白色

# 保存设置
OUTPUT_FOLDER = "../template"        # 输出文件夹
OUTPUT_FILENAME = "obs4.png"         # 输出文件名
# =====================================================

def load_config():
    """从 YAML 文件加载分辨率参数"""
    config_path = "../config/obs.yaml"
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
    """创建上下双黑块观测目标图片（中间白色横条分隔）"""
    # 计算图像尺寸（像素）
    image_width = meters_to_pixels(OUTER_WIDTH, resolution)
    image_height = meters_to_pixels(OUTER_HEIGHT, resolution)

    # 创建白色背景图像
    image = Image.new('RGB', (image_width, image_height), WHITE)
    draw = ImageDraw.Draw(image)

    # 内框尺寸（像素）
    inner_width_px = meters_to_pixels(INNER_WIDTH, resolution)
    inner_height_px = meters_to_pixels(INNER_HEIGHT, resolution)

    # 中间横条高度（像素）
    column_height_px = meters_to_pixels(COLUMN_WIDTH, resolution)

    # 上下两个黑块总高度（含中间横条）
    total_height_with_column = 2 * inner_height_px + column_height_px

    # 垂直居中计算起始Y坐标
    start_y = (image_height - total_height_with_column) // 2

    # 水平居中计算X坐标
    center_x = image_width // 2
    left_x = center_x - inner_width_px // 2
    right_x = left_x + inner_width_px

    # 上方黑色矩形
    top_top = start_y
    top_bottom = start_y + inner_height_px

    # 下方黑色矩形（跳过中间横条）
    bottom_top = top_bottom + column_height_px
    bottom_bottom = bottom_top + inner_height_px

    # 绘制上方黑色矩形
    draw.rectangle([left_x, top_top, right_x, top_bottom], fill=BLACK)

    # 绘制下方黑色矩形
    draw.rectangle([left_x, bottom_top, right_x, bottom_bottom], fill=BLACK)

    return image, image_width, image_height

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
        print(f"外框尺寸: {OUTER_WIDTH}m x {OUTER_HEIGHT}m "
              f"({meters_to_pixels(OUTER_WIDTH, RESOLUTION)} x {meters_to_pixels(OUTER_HEIGHT, RESOLUTION)} px)")
        print(f"内框尺寸: {INNER_WIDTH}m x {INNER_HEIGHT}m "
              f"({meters_to_pixels(INNER_WIDTH, RESOLUTION)} x {meters_to_pixels(INNER_HEIGHT, RESOLUTION)} px)")
        print(f"中间柱子宽度: {COLUMN_WIDTH}m "
              f"({meters_to_pixels(COLUMN_WIDTH, RESOLUTION)} px)")
        print("图案: 外框白色，上下两个黑色内框，中间白色柱子分隔")

        # 显示文件信息
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            print(f"文件大小: {file_size} 字节")

    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()
