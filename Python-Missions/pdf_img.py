import os
from PIL import Image

# 1. 设置图片所在文件夹路径
folder_path = "your_image_folder_path"

# 2. 获取所有 jpg 文件
images = [f for f in os.listdir(folder_path) if f.lower().endswith('.jpg')]

# 3. 核心：自然排序。假设文件名是纯数字序列，如 "1.jpg", "2.jpg"
# 如果文件名包含前缀，比如 "img_1.jpg"，可以通过正则或字符串切片提取数字
images.sort(key=lambda x: int(os.path.splitext(x)[0])) 

# 4. 读取并转换图片
image_list = []
for img_name in images:
    img_path = os.path.join(folder_path, img_name)
    # 必须转换为 RGB 模式，否则保存 PDF 会报错（比如 RGBA 格式图片）
    img = Image.open(img_path).convert('RGB')
    image_list.append(img)

# 5. 保存为 PDF
if image_list:
    # 将第一张图片作为基础，把后面的图片追加进去
    image_list[0].save(
        r"output.pdf", 
        save_all=True, 
        append_images=image_list[1:]
    )
    print("PDF 转换完成！")
else:
    print("未找到 JPG 文件。")