import os
import cv2
from ultralytics import YOLO

# ================= 配置区域 =================
# 请在此处填入你的实际路径 (Windows路径建议前面加r，防止转义字符报错)
INPUT_FOLDER = r"D:\Legion\Downloads\dataset\down\test_down"  
MODEL_PATH = r"D:\escherichia_train\weights\best.pt"    
# ============================================

def main():
    # 1. 自动生成 result 文件夹路径
    result_folder = os.path.join(INPUT_FOLDER, "result")
    txt_output_path = os.path.join(result_folder, "detection_log.txt")

    # 2. 如果 result 文件夹不存在，则创建它
    if not os.path.exists(result_folder):
        os.makedirs(result_folder)
        print(f"已创建结果文件夹: {result_folder}")

    # 3. 加载 YOLOv12 模型
    print("正在加载模型，请稍候...")
    try:
        model = YOLO(MODEL_PATH)
    except Exception as e:
        print(f"模型加载失败，请检查路径或确保ultralytics是最新版。错误信息: {e}")
        return

    # 4. 定义支持的图片格式
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')

    # 5. 打开 txt 文件准备写入记录
    # 使用 utf-8 编码防止 Windows 下中文乱码
    with open(txt_output_path, 'w', encoding='utf-8') as f:
        f.write("=== YOLOv12 图片检测置信度记录 ===\n\n")

        # 遍历输入文件夹下的所有文件
        for filename in os.listdir(INPUT_FOLDER):
            if filename.lower().endswith(valid_extensions):
                img_path = os.path.join(INPUT_FOLDER, filename)
                print(f"正在处理: {filename} ...")

                # 运行推理 (直接静默运行，避免控制台输出过多信息)
                results = model(img_path, verbose=False)
                result = results[0]  # 因为每次只传了一张图片，所以取第0个结果

                # 生成带有识别框和置信度的渲染图片
                annotated_img = result.plot()

                # 保存图片到 result 文件夹
                save_path = os.path.join(result_folder, filename)
                cv2.imwrite(save_path, annotated_img)

                # 将检测结果写入 txt 文件
                f.write(f"图片文件: {filename}\n")
                
                # result.boxes 包含了检测到的所有目标信息
                if len(result.boxes) == 0:
                    f.write("  [!] 未检测到任何目标\n")
                else:
                    for box in result.boxes:
                        # 获取类别索引并转换为具体的类别名称
                        cls_id = int(box.cls[0])
                        class_name = model.names[cls_id]
                        # 获取置信度
                        conf = float(box.conf[0])
                        
                        f.write(f"  - 检测到: {class_name}, 置信度: {conf:.4f}\n")
                
                f.write("-" * 40 + "\n")

    print("\n" + "="*40)
    print(f"处理完成！\n所有渲染图片及结果记录已保存至:\n{result_folder}")

if __name__ == "__main__":
    main()