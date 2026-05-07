import subprocess
import cv2
import os

def pro_ai_upscale_extreme_sharp(input_path, output_path, realesrgan_exe_path):
    """
    针对水墨/艺术风格优化的极清超分辨率版本
    """
    if not os.path.exists(input_path):
        print(f"❌ 找不到输入图片: {input_path}")
        return
    if not os.path.exists(realesrgan_exe_path):
        print(f"❌ 找不到 AI 引擎: {realesrgan_exe_path}")
        return

    temp_upscaled_path = "temp_ai_upscaled.png"

    # --- 1. 调用 Real-ESRGAN 引擎 (核心修改：使用 anime 模型) ---
    print("🚀 正在启动动漫/插画级 AI 模型进行极端锐化重构...")
    command = [
        realesrgan_exe_path,
        "-i", input_path,
        "-o", temp_upscaled_path,
        "-s", "4",
        # 【关键修改 1】换用 anime 模型，它对水墨和建筑线条的锐化极强，拒绝涂抹模糊
        "-n", "realesrgan-x4plus-anime" 
    ]
    
    try:
        subprocess.run(command, check=True)
        print("✅ AI 锐化重构完成！")
    except subprocess.CalledProcessError:
        print("❌ Real-ESRGAN 引擎运行失败。")
        return

    # --- 2. 动态读取尺寸，等比例缩小至 4K ---
    img = cv2.imread(temp_upscaled_path)
    if img is None:
        print("❌ 无法读取临时文件。")
        return

    current_h, current_w = img.shape[:2]
    target_w = 3840
    target_h = int(current_h * (target_w / current_w))
    
    print(f"📐 正在使用像素区域重采样技术缩放至 {target_w}x{target_h}...")
    
    # 【关键修改 2】从超大图“缩小”到 4K，必须用 INTER_AREA 算法，它能保留最完美的清晰边缘
    final_img = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_AREA)

    # --- 3. 保存并清理 ---
    success = cv2.imwrite(output_path, final_img)
    if success:
        print(f"🎉 完美！最高锐度的 4K 图片已生成: {output_path}")
        if os.path.exists(temp_upscaled_path):
            os.remove(temp_upscaled_path)
    else:
        print("❌ 最终图片保存失败。")

# ==========================================
if __name__ == "__main__":
    # 路径保持不变
    INPUT = r"D:\Repositories\ScuderiaAMG\Python-Missions\pic.py\00000.jpg"  
    OUTPUT = r"D:\Repositories\ScuderiaAMG\Python-Missions\pic.py\Pro_4K_Sharp.png" 
    REALESRGAN_EXE = r"D:\Repositories\ScuderiaAMG\Python-Missions\pic.py\realesrgan-ncnn-vulkan-20220424-windows\realesrgan-ncnn-vulkan.exe"

    pro_ai_upscale_extreme_sharp(INPUT, OUTPUT, REALESRGAN_EXE)