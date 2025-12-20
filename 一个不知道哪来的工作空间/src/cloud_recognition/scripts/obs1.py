#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw
import os
import yaml

# ==================== 矩形参数设置（硬编码）====================
# 矩形参数（单位：米）
RECT_WIDTH_OUT = 1.42       # 外矩形宽度(米)
RECT_HEIGHT_OUT = 1.14      # 外矩形高度
RECT_WIDTH_IN = 1.04        # 内矩形宽度
RECT_HEIGHT_IN = 0.76       # 内矩形高度

# 颜色设置 (RGB格式)
BLACK = (0, 0, 0)      # 黑色
WHITE = (255, 255, 255)  # 白色

# 保存设置
OUTPUT_FOLDER = "../template"        # 输出文件夹名称
OUTPUT_FILENAME = "obs1.png"         # 输出文件名
# =====================================================

# 读取 YAML 配置文件获取分辨率
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
    """创建观测目标图片（外白内黑）"""
    # 根据分辨率计算图片尺寸
    image_width = meters_to_pixels(RECT_WIDTH_OUT, resolution)
    image_height = meters_to_pixels(RECT_HEIGHT_OUT, resolution)
    
    # 计算中心位置
    center_x = image_width // 2
    center_y = image_height // 2
    
    # 计算内外矩形在像素坐标系中的尺寸
    inner_rect_width_px = meters_to_pixels(RECT_WIDTH_IN, resolution)
    inner_rect_height_px = meters_to_pixels(RECT_HEIGHT_IN, resolution)
    
    # 计算内矩形左上角坐标（使矩形居中）
    inner_x = center_x - inner_rect_width_px // 2
    inner_y = center_y - inner_rect_height_px // 2
    inner_right = inner_x + inner_rect_width_px
    inner_bottom = inner_y + inner_rect_height_px
    
    # 创建新图片，模式为RGB，背景为白色
    image = Image.new('RGB', (image_width, image_height), WHITE)
    
    # 创建绘图对象
    draw = ImageDraw.Draw(image)
    
    # 绘制内矩形（黑色）- 这是观测目标的中心
    draw.rectangle([inner_x, inner_y, inner_right, inner_bottom], fill=BLACK)
    
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
        # 从配置文件读取分辨率
        RESOLUTION = load_config()
        print(f"从配置文件加载分辨率: {RESOLUTION} m/px")

        # 创建图片
        img, img_width, img_height = create_target_image(RESOLUTION)
        
        # 获取完整保存路径
        full_path = get_full_path()
        
        # 保存为PNG格式
        img.save(full_path, 'PNG')
        print(f"图片已保存为: {full_path}")
        print(f"图片尺寸: {img_width} x {img_height} 像素")
        print(f"分辨率: {RESOLUTION} m/px")
        print(f"外矩形: {RECT_WIDTH_OUT}m x {RECT_HEIGHT_OUT}m "
              f"({meters_to_pixels(RECT_WIDTH_OUT, RESOLUTION)} x "
              f"{meters_to_pixels(RECT_HEIGHT_OUT, RESOLUTION)} px)")
        print(f"内矩形: {RECT_WIDTH_IN}m x {RECT_HEIGHT_IN}m "
              f"({meters_to_pixels(RECT_WIDTH_IN, RESOLUTION)} x "
              f"{meters_to_pixels(RECT_HEIGHT_IN, RESOLUTION)} px)")
        print("图案: 外白内黑的观测目标")
        
        # 显示文件信息
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            print(f"文件大小: {file_size} 字节")
        
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()