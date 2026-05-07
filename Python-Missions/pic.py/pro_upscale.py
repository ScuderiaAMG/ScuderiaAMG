import subprocess
import cv2
import os

def pro_ai_upscale_keep_ratio(input_path, output_path, realesrgan_exe_path):
    """
    使用 Real-ESRGAN 引擎进行极清超分辨率，并【等比例】调整为 4K 宽度，拒绝拉伸变形！
    """
    if not os.path.exists(input_path):
        print(f"❌ 找不到输入图片: {input_path}")
        return
    if not os.path.exists(realesrgan_exe_path):
        print(f"❌ 找不到 AI 引擎: {realesrgan_exe_path}，请确认路径！")
        return

    # 中间文件路径 (与脚本同目录)
    temp_upscaled_path = "temp_ai_upscaled.png"

    # --- 1. 调用 Real-ESRGAN 引擎进行 4倍 放大 ---
    print("🚀 正在启动 Real-ESRGAN 引擎进行超清重构...")
    command = [
        realesrgan_exe_path,
        "-i", input_path,
        "-o", temp_upscaled_path,
        "-s", "4",
        "-n", "realesrgan-x4plus"
    ]
    
    try:
        # 执行命令行调用
        subprocess.run(command, check=True)
        print("✅ AI 超分完成！正在处理画面比例...")
    except subprocess.CalledProcessError:
        print("❌ Real-ESRGAN 引擎运行失败，请检查路径或图片格式。")
        return

    # --- 2. 动态读取尺寸，等比例缩放至 4K ---
    img = cv2.imread(temp_upscaled_path)
    if img is None:
        print("❌ 无法读取 AI 放大后的临时文件。")
        return

    # 获取 AI 放大后的当前长宽
    current_h, current_w = img.shape[:2]
    
    # 设定我们想要的 4K 宽度
    target_w = 3840
    
    # 核心修改：根据原始比例动态计算高度！这样绝对不会拉伸。
    target_h = int(current_h * (target_w / current_w))
    
    print(f"📐 正在等比例缩放至 {target_w}x{target_h} (完美保持原图比例)...")
    
    # 使用 Lanczos4 算法缩小至目标尺寸，保留最大锐度
    final_img = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)

    # --- 3. 保存并清理 ---
    success = cv2.imwrite(output_path, final_img)
    if success:
        print(f"🎉 完美！无拉伸的高清图片已生成: {output_path}")
        # 清理临时文件
        if os.path.exists(temp_upscaled_path):
            os.remove(temp_upscaled_path)
    else:
        print("❌ 最终图片保存失败。")

# ==========================================
#                  执行区
# ==========================================
if __name__ == "__main__":
    # 1. 原始图片路径
    INPUT = r"D:\Repositories\ScuderiaAMG\Python-Missions\pic.py\00000.jpg"  
    
    # 2. 最终输出的高清图片路径
    OUTPUT = r"D:\Repositories\ScuderiaAMG\Python-Missions\pic.py\Pro_4K.png" 
    
    # 3. Real-ESRGAN exe 程序的绝对路径
    REALESRGAN_EXE = r"D:\Repositories\ScuderiaAMG\Python-Missions\pic.py\realesrgan-ncnn-vulkan-20220424-windows\realesrgan-ncnn-vulkan.exe"

    # 执行防拉伸版的函数
    pro_ai_upscale_keep_ratio(INPUT, OUTPUT, REALESRGAN_EXE)