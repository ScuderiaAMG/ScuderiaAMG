import cv2
from cv2 import dnn_superres
import os

def ai_super_resolution_to_4k(input_path, output_path, model_path="EDSR_x4.pb"):
    """
    使用 AI 模型对图片进行超分辨率处理，并输出为 4K (16:10) 比例。
    """
    # --- 1. 路径与环境检查 ---
    if not os.path.exists(input_path):
        print(f"❌ 错误: 找不到输入图片 '{input_path}'")
        return
    if not os.path.exists(model_path):
        print(f"❌ 错误: 找不到模型文件 '{model_path}'。请确保已下载并放置在同级目录！")
        return

    # --- 2. 初始化 AI 超分辨率模型 ---
    print("⏳ 正在加载 EDSR AI 模型 (只需几秒钟)...")
    sr = dnn_superres.DnnSuperResImpl_create()
    sr.readModel(model_path)
    # 设置模型名称和放大倍数 (EDSR_x4 就是 4 倍)
    sr.setModel("edsr", 4) 

    # --- 3. 读取原始图片 ---
    img = cv2.imread(input_path)
    if img is None:
        print("❌ 错误: 图片读取失败。")
        return
    
    original_h, original_w = img.shape[:2]
    print(f"✅ 成功读取图片。原始尺寸: {original_w} x {original_h}")

    # --- 4. 执行 AI 放大运算 ---
    print("🧠 正在进行 AI 超分辨率重构 (计算量较大，根据电脑性能可能需要数十秒到几分钟，请耐心等待)...")
    # 这步会生成极为清晰的放大后图像
    upscaled_img = sr.upsample(img)
    print(f"✅ AI 放大完成！当前尺寸: {upscaled_img.shape[1]} x {upscaled_img.shape[0]}")

    # --- 5. 尺寸校准至 4K 16:10 (3840 x 2400) ---
    target_width = 3840
    target_height = 2400
    print(f"📐 正在校准至目标尺寸: {target_width} x {target_height} (16:10 比例)...")
    
    # 使用 INTER_LANCZOS4 算法调整最终尺寸。
    # Lanczos 算法在缩小或微调高分辨率图像时，能最大程度保留边缘锐度，抗锯齿效果极佳。
    final_img = cv2.resize(upscaled_img, (target_width, target_height), interpolation=cv2.INTER_LANCZOS4)

    # --- 6. 保存最终结果 ---
    # 推荐保存为 .png 以保留最高画质，避免 jpg 二次压缩产生噪点
    success = cv2.imwrite(output_path, final_img)
    if success:
        print(f"🎉 搞定！超高画质图片已保存至: {output_path}")
    else:
        print("❌ 错误: 最终图片保存失败。")

# ==========================================
#                  执行区
# ==========================================
if __name__ == "__main__":
    # 替换为你实际的图片路径
    INPUT_IMAGE = "D:\\Repositories\\ScuderiaAMG\\Python-Missions\\pic.py\\00000.jpg"  
    
    # 输出图片路径 (建议使用 png 格式无损保存)
    OUTPUT_IMAGE = "D:\\Repositories\\ScuderiaAMG\\Python-Missions\\pic.py\\GreatWall_4K_AI_Upscaled.png" 
    
    # 模型文件路径 (如果和脚本在同一目录，保持默认即可)
    MODEL_FILE = "EDSR_x4.pb"

    ai_super_resolution_to_4k(INPUT_IMAGE, OUTPUT_IMAGE, MODEL_FILE)