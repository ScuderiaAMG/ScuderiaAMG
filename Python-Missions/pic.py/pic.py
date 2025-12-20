from PIL import Image
import numpy as np

def is_grayscale_pixel(r, g, b, tolerance=30):
    """
    判断一个RGB像素是否为灰色。
    通过检查RGB三个值是否非常接近（在容差范围内）来判断。
    容差的存在是为了处理一些接近灰色但不完全相等的像素。
    """
    return abs(r - g) <= tolerance and abs(r - b) <= tolerance and abs(g - b) <= tolerance

def process_image(input_path, output_path, tolerance=30):
    """
    处理图片：反转黑白灰色域的像素，保持其他颜色不变。

    Args:
        input_path (str): 输入图片的路径。
        output_path (str): 输出图片的路径。
        tolerance (int): 判断灰色的容差，默认为30。
    """
    try:
        # 打开图片
        img = Image.open(input_path)
        print(f"原始图片尺寸: {img.size}, 模式: {img.mode}")

        # 检查分辨率是否不低于2K (2048)
        width, height = img.size
        if width < 2048 and height < 2048:
            raise ValueError(f"图片分辨率 {width}x{height} 低于2K (2048) 标准。")

        # 确保图片模式为RGB，以便处理
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # 将图片转换为NumPy数组以提高处理速度
        img_array = np.array(img, dtype=np.int16) # 使用int16防止减法运算溢出

        # 分离RGB通道
        r_channel = img_array[:, :, 0]
        g_channel = img_array[:, :, 1]
        b_channel = img_array[:, :, 2]

        # 创建一个掩码，标记哪些像素是灰色的
        # 使用绝对差值判断
        diff_rg = np.abs(r_channel - g_channel)
        diff_rb = np.abs(r_channel - b_channel)
        diff_gb = np.abs(g_channel - b_channel)

        grayscale_mask = (diff_rg <= tolerance) & (diff_rb <= tolerance) & (diff_gb <= tolerance)

        # 对灰色像素进行反转
        # 创建一个全为255的矩阵，用于反转计算
        inverted_channels = 255 - img_array
        # 仅对灰色区域应用反转
        img_array[grayscale_mask] = inverted_channels[grayscale_mask]

        # 将数组转换回uint8
        img_array = np.clip(img_array, 0, 255).astype(np.uint8)

        # 将NumPy数组转换回PIL Image对象
        processed_img = Image.fromarray(img_array, mode='RGB')

        # 保存处理后的图片
        processed_img.save(output_path, format='PNG') # 使用PNG格式以保留高质量
        print(f"处理完成！图片已保存至: {output_path}")

    except FileNotFoundError:
        print(f"错误：找不到文件 {input_path}")
    except ValueError as e:
        print(f"错误：{e}")
    except Exception as e:
        print(f"处理过程中发生错误: {e}")

# --- 主程序 ---
# --- 主程序 ---
if __name__ == "__main__":
    # 修改输入路径为你的图片实际路径
    # 使用原始字符串 (r"") 来避免转义序列警告
    input_image_path = r"D:\wallpapers\Retro Desktop Wallpaper 2.png"
    
    # 修改输出路径到一个你有权限的目录
    # 例如，保存到当前脚本所在的文件夹
    output_image_path = r"d:\Repositories\Python-Missions\pic.py\output_image.png"
    # 或者，保存到你的用户桌面 (请替换 <YourUsername> 为你的实际用户名)
    # output_image_path = r"C:\Users\<YourUsername>\Desktop\output_image.png"

    # 可以调整容差值来改变对“灰色”的定义
    tolerance_value = 30

    process_image(input_image_path, output_image_path, tolerance=tolerance_value)