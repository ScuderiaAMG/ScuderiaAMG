import subprocess
import cv2
import os
import numpy as np  # 【新增】引入 numpy 用于创建纯黑背景画布

def pro_ai_upscale_extreme_sharp(input_path, output_path, realesrgan_exe_path):
    """
    针对水墨/艺术风格优化的极清超分辨率版本，并自动适配 16:10 4K 居中无损填充
    """
    if not os.path.exists(input_path):
        print(f"❌ 找不到输入图片: {input_path}")
        return
    if not os.path.exists(realesrgan_exe_path):
        print(f"❌ 找不到 AI 引擎: {realesrgan_exe_path}")
        return

    temp_upscaled_path = "temp_ai_upscaled.png"

    # --- 1. 调用 Real-ESRGAN 引擎 ---
    print("🚀 正在启动动漫/插画级 AI 模型进行极端锐化重构...")
    command = [
        realesrgan_exe_path,
        "-i", input_path,
        "-o", temp_upscaled_path,
        "-s", "4",
        "-n", "realesrgan-x4plus-anime" 
    ]
    
    try:
        subprocess.run(command, check=True)
        print("✅ AI 锐化重构完成！")
    except subprocess.CalledProcessError:
        print("❌ Real-ESRGAN 引擎运行失败。")
        return

    # --- 2. 动态读取尺寸，等比例缩小并放入 16:10 黑色画布 ---
    img = cv2.imread(temp_upscaled_path)
    if img is None:
        print("❌ 无法读取临时文件。")
        return

    current_h, current_w = img.shape[:2]
    
    # 【核心修改】设定 16:10 4K 的目标分辨率
    target_w = 3840
    target_h = 2400 
    
    print(f"📐 正在将图片无损居中填充至 {target_w}x{target_h} (16:10)...")
    
    # 1. 计算缩放比例 (以刚好能塞进目标尺寸为准，不拉伸)
    scale = min(target_w / current_w, target_h / current_h)
    new_w = int(current_w * scale)
    new_h = int(current_h * scale)

    # 2. 对超大图进行缩小重采样
    resized_img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # 3. 创建一张 3840x2400 的纯黑底图 (数据类型为uint8，颜色为BGR的0,0,0)
    final_img = np.zeros((target_h, target_w, 3), dtype=np.uint8)

    # 4. 计算将图片贴到正中心的偏移量
    y_offset = (target_h - new_h) // 2
    x_offset = (target_w - new_w) // 2

    # 5. 将缩放后的图片覆盖到黑底的中心位置
    final_img[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized_img

    # --- 3. 保存并清理 ---
    success = cv2.imwrite(output_path, final_img)
    if success:
        print(f"🎉 完美！最高锐度的 16:10 4K 图片已生成: {output_path}")
        if os.path.exists(temp_upscaled_path):
            os.remove(temp_upscaled_path)
    else:
        print("❌ 最终图片保存失败。")

# ==========================================
if __name__ == "__main__":
    # 路径保持不变
    INPUT = r"D:\Repositories\ScuderiaAMG\Python-Missions\pic.py\11111.png"  
    OUTPUT = r"D:\Repositories\ScuderiaAMG\Python-Missions\pic.py\intel.png" 
    REALESRGAN_EXE = r"D:\Repositories\ScuderiaAMG\Python-Missions\pic.py\realesrgan-ncnn-vulkan-20220424-windows\realesrgan-ncnn-vulkan.exe"

    pro_ai_upscale_extreme_sharp(INPUT, OUTPUT, REALESRGAN_EXE)