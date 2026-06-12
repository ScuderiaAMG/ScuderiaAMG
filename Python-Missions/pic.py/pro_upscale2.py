import subprocess
import cv2
import os
import sys

def pro_ai_upscale_any_ratio(input_path, output_path, realesrgan_exe_path, target_width=3840):
    if not os.path.exists(input_path):
        print(f"错误: 找不到输入图片 '{input_path}'")
        return
    if not os.path.exists(realesrgan_exe_path):
        print(f"错误: 找不到 AI 引擎 '{realesrgan_exe_path}'")
        return

    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    temp_upscaled_path = os.path.join(os.path.dirname(realesrgan_exe_path), "temp_ai_upscaled.png")

    print("正在启动 Real-ESRGAN 引擎进行超清重构 (通用真实照片模型)...")
    
    command = [
        realesrgan_exe_path,
        "-i", input_path,
        "-o", temp_upscaled_path,
        "-s", "4",               # 放大 4 倍
        "-n", "realesrgan-x4plus", # 使用通用真实照片模型
        "-f", "png"              # 强制输出 png 格式
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        print("AI 超分完成！正在处理画面比例...")
    except subprocess.CalledProcessError as e:
        print(f"Real-ESRGAN 引擎运行失败。错误代码: {e.returncode}")
        print("请检查显卡驱动是否正常，或路径中是否包含特殊字符。")
        return
    except FileNotFoundError:
        print("找不到可执行文件，请检查路径是否正确。")
        return

    img = cv2.imread(temp_upscaled_path)
    if img is None:
        print("无法读取 AI 放大后的临时文件。")
        return

    current_h, current_w = img.shape[:2]
    
    scale_ratio = target_width / current_w
    target_h = int(current_h * scale_ratio)

    print(f"原始放大尺寸: {current_w}x{current_h}")
    print(f"正在等比例缩放至 {target_width}x{target_h}")

    final_img = cv2.resize(img, (target_width, target_h), interpolation=cv2.INTER_LANCZOS4)

    success = cv2.imwrite(output_path, final_img)
    if success:
        print(f"无拉伸的高清图片已生成: {output_path}")
        if os.path.exists(temp_upscaled_path):
            os.remove(temp_upscaled_path)
    else:
        print("最终图片保存失败，请检查输出路径权限。")

if __name__ == "__main__":

    
    INPUT_IMAGE = rf"./input/8.png"
    OUTPUT_IMAGE = rf"./output/Pro_4K_Result_8.png"
    REALESRGAN_EXE = r"./realesrgan-ncnn-vulkan-20220424-windows/realesrgan-ncnn-vulkan.exe"
    pro_ai_upscale_any_ratio(INPUT_IMAGE, OUTPUT_IMAGE, REALESRGAN_EXE, target_width=3840)
    print(f"已处理 8.png\n")