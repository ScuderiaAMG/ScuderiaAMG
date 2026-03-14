import torchvision.transforms.functional as TF
import sys
sys.modules['torchvision.transforms.functional_tensor'] = TF
import os
import cv2
import torch
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
from basicsr.utils.download_util import load_file_from_url

def enhance_image(input_path, output_path, outscale=2, tile_size=512):
    """
    使用 Real-ESRGAN 对图片进行超分辨率处理
    
    参数:
        input_path (str): 原图路径
        output_path (str): 输出图片路径
        outscale (float): 最终输出的放大倍数 (默认2倍)
        tile_size (int): 切块大小，防爆显存的关键。8GB显存推荐512或256
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"找不到输入图片: {input_path}")

    # 1. 配置核心网络架构 (RealESRGAN_x4plus 针对真实照片优化)
    # 这里的 scale=4 是模型本身的架构设定，不要改动
    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
    netscale = 4 

    # 2. 自动下载或加载模型权重
    model_url = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth'
    model_path = load_file_from_url(url=model_url, model_dir='weights', progress=True, file_name=None)

    # 3. 初始化推理器
    upsampler = RealESRGANer(
        scale=netscale,
        model_path=model_path,
        model=model,
        tile=tile_size,
        tile_pad=10,
        pre_pad=0,
        half=True,  # 开启半精度(FP16)，RTX 4060 强烈推荐，省显存且提速
        gpu_id=0    # 使用主 GPU
    )

    # 4. 读取图片
    # cv2 默认读取为 BGR 格式，RealESRGANer 内部会自动处理
    img = cv2.imread(input_path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"无法读取图片，请检查文件是否损坏或路径是否包含不支持的字符: {input_path}")

    print(f"正在处理: {input_path} (原图尺寸: {img.shape[1]}x{img.shape[0]})")

    try:
        # 5. 执行超分辨率增强
        # outscale 参数控制最终输出的尺寸比例
        output, _ = upsampler.enhance(img, outscale=outscale)

        # 6. 保存结果
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        cv2.imwrite(output_path, output)
        print(f"处理完成！已保存至: {output_path} (输出尺寸: {output.shape[1]}x{output.shape[0]})")

    except RuntimeError as e:
        print(f"处理失败: {e}")
        if 'CUDA out of memory' in str(e):
            print("【警告】显存溢出！请尝试在调用时减小 tile_size 参数（例如设为 256 或 128）。")
    finally:
        # 7. 清理显存垃圾
        # 这在批量处理数据流水线中非常重要，防止显存碎片化导致 OOM
        torch.cuda.empty_cache()

# ==========================================
# 调用示例
# ==========================================
if __name__ == "__main__":
    # 假设你的樱花图片放在当前目录
    input_file = "3A0AC779DA9407B350C7C4B54F493F4D.jpg"
    output_file = "sakura_enhanced.jpg"

    # 执行函数：原图 3060*4080，outscale=2 输出为 6120*8160
    # tile_size=512 配合 FP16，在 8GB VRAM 上应该能流畅运行
    enhance_image(
        input_path=input_file, 
        output_path=output_file, 
        outscale=2, 
        tile_size=256
    )