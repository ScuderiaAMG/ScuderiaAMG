#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw
import os
import yaml

# ==================== 矩形参数设置（除分辨率外，其余硬编码）====================
# 外框参数（单位：米）
OUTER_WIDTH = 2.24       # 外框宽度(米)
OUTER_HEIGHT = 1.18      # 外框高度(米)

# 内框参数（单位：米）
INNER_WIDTH = 0.9        # 内框宽度(米)
INNER_HEIGHT = 0.9       # 内框高度(米)

# 中间柱子宽度（单位：米）
COLUMN_WIDTH = 0.1       # 中间竖直隔断的宽度(米)

# 颜色设置 (RGB格式)
BLACK = (0, 0, 0)        # 黑色
WHITE = (255, 255, 255)  # 白色

# 保存设置
OUTPUT_FOLDER = "../template"        # 输出文件夹
OUTPUT_FILENAME = "obs3.png"         # 输出文件名
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
    """创建带有中间隔断的矩形观测目标图片（外白背景，左右两个黑块，中间白柱）"""
    # 根据外框尺寸计算图像尺寸（像素）
    image_width = meters_to_pixels(OUTER_WIDTH, resolution)
    image_height = meters_to_pixels(OUTER_HEIGHT, resolution)

    # 创建白色背景图像
    image = Image.new('RGB', (image_width, image_height), WHITE)
    draw = ImageDraw.Draw(image)

    # 计算内框尺寸（像素）
    inner_width_px = meters_to_pixels(INNER_WIDTH, resolution)
    inner_height_px = meters_to_pixels(INNER_HEIGHT, resolution)

    # 计算中间柱子宽度（像素）
    column_width_px = meters_to_pixels(COLUMN_WIDTH, resolution)

    # 总占用宽度：左黑块 + 柱子 + 右黑块
    total_inner_width = 2 * inner_width_px + column_width_px

    # 计算起始X坐标（水平居中）
    start_x = (image_width - total_inner_width) // 2
    center_y = image_height // 2

    # 左上角和右下角坐标
    top_y = center_y - inner_height_px // 2
    bottom_y = center_y + inner_height_px // 2

    # 左侧黑色矩形
    left_inner_left = start_x
    left_inner_right = start_x + inner_width_px

    # 右侧黑色矩形（跳过中间柱子）
    right_inner_left = start_x + inner_width_px + column_width_px
    right_inner_right = right_inner_left + inner_width_px

    # 绘制左侧黑色矩形
    draw.rectangle([left_inner_left, top_y, left_inner_right, bottom_y], fill=BLACK)

    # 绘制右侧黑色矩形
    draw.rectangle([right_inner_left, top_y, right_inner_right, bottom_y], fill=BLACK)

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

        # 保存为 PNG
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
        print("图案: 外框白色，左右两个黑色内框，中间白色柱子分隔")

        # 显示文件信息
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            print(f"文件大小: {file_size} 字节")

    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()