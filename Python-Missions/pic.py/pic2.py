import cv2
import numpy as np
import os

def upsample_and_stretch_image(input_path, output_upscaled_path, output_stretched_path, target_width_4k=3840, target_height_4k=2160):
    """
    1. 将输入图片通过上采样调整到指定的 4K 分辨率。
    2. 然后将 4K 图片按 1280:800 (即 16:10) 的比例拉伸。

    Args:
        input_path (str): 输入图片的路径。
        output_upscaled_path (str): 中间步骤：输出上采样至 4K 的图片路径。
        output_stretched_path (str): 最终步骤：输出按 16:10 拉伸后的图片路径。
        target_width_4k (int): 目标 4K 宽度，默认为 3840。
        target_height_4k (int): 目标 4K 高度，默认为 2160。
    """
    # 1. 读取原始图片
    img = cv2.imread(input_path)
    if img is None:
        print(f"错误：无法读取图片 '{input_path}'，请检查路径是否正确。")
        return

    original_height, original_width = img.shape[:2]
    print(f"原始图片尺寸: {original_width} x {original_height}")

    # 2. 检查目标 4K 尺寸是否大于原始尺寸
    if target_width_4k <= original_width or target_height_4k <= original_height:
        print(f"警告：目标 4K 尺寸 ({target_width_4k}x{target_height_4k}) 小于或等于原始尺寸 ({original_width}x{original_height})。这将导致下采样或无变化。")

    # 3. 上采样到 4K
    upscaled_img = cv2.resize(img, (target_width_4k, target_height_4k), interpolation=cv2.INTER_CUBIC)
    print(f"已上采样到 4K ({target_width_4k}x{target_height_4k})")

    # 4. 保存上采样后的 4K 图片 (可选中间步骤)
    success_4k = cv2.imwrite(output_upscaled_path, upscaled_img)
    if success_4k:
        print(f"中间图片已保存到: {output_upscaled_path}")
    else:
        print(f"错误：无法保存中间图片到 '{output_upscaled_path}'")
        return # 如果中间步骤失败，停止后续处理

    # 5. 计算按 16:10 比例拉伸的目标尺寸
    # 例如，保持 3840 像素宽度，高度应为 3840 / 16 * 10 = 2400
    aspect_ratio_w = 16
    aspect_ratio_h = 10
    stretch_target_width = target_width_4k # 保持 4K 宽度作为拉伸后宽度
    stretch_target_height = int((stretch_target_width / aspect_ratio_w) * aspect_ratio_h)
    
    print(f"将按 16:10 比例拉伸至: {stretch_target_width} x {stretch_target_height}")

    # 6. 拉伸图片
    stretched_img = cv2.resize(upscaled_img, (stretch_target_width, stretch_target_height), interpolation=cv2.INTER_CUBIC)

    # 7. 保存最终拉伸后的图片
    success_stretch = cv2.imwrite(output_stretched_path, stretched_img)
    if success_stretch:
        print(f"成功完成上采样和拉伸，并保存最终图片到: {output_stretched_path}")
    else:
        print(f"错误：无法保存最终图片到 '{output_stretched_path}'")


# --- 主程序 ---
if __name__ == "__main__":
    # --- 请修改这里的路径 ---
    input_image_path = r"D:\trash\1765206788.png"      # 替换为你的 1280x800 图片路径
    output_4k_path = "upscaled_to_4k2.jpg"          # 中间步骤：保存 4K 图片的路径
    output_final_path = "stretched_to_16_10_aspect.jpg" # 最终步骤：保存拉伸后图片的路径

    # --- 执行上采样和拉伸 ---
    upsample_and_stretch_image(input_image_path, output_4k_path, output_final_path)
