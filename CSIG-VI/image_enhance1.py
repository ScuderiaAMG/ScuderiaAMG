def enhance_images(input_dir, model_path, output_dir):
    """增强输入文件夹中的所有图像"""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # 加载模型
    model = DarkVisionNet()
    model.load_state_dict(torch.load(model_path))
    model.to(device)
    model.eval()
    
    # 处理所有图像
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    for img_path in input_path.glob('*.*'):
        if img_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
            # 读取图像
            image = cv2.imread(str(img_path))
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            original_size = image.shape[:2]
            
            # 预处理
            image = image.astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(image).permute(2, 0, 1).unsqueeze(0).to(device)
            
            # 推理
            with torch.no_grad():
                enhanced = model(image_tensor)
            
            # 后处理
            enhanced = enhanced.squeeze(0).permute(1, 2, 0).cpu().numpy()
            enhanced = (enhanced * 255).astype(np.uint8)
            
            # 保持原始分辨率
            enhanced = cv2.resize(enhanced, (original_size[1], original_size[0]))
            
            # 保存结果
            output_image = cv2.cvtColor(enhanced, cv2.COLOR_RGB2BGR)
            cv2.imwrite(str(output_path / img_path.name), output_image)
            
            print(f'Processed: {img_path.name}')

# 使用示例
if __name__ == "__main__":
    enhance_images('input', 'results/final_model.pth', 'enhanced_results')