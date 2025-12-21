# Python网络视频爬虫

## 注意事项

· 请遵守目标网站的 robots.txt 和使用条款

· 尊重版权和隐私

· 适当调整请求频率，避免对目标网站造成过大压力

## 可以根据需要修改以下部分：

1. 视频识别规则：在 extract_video_links 方法中添加更多选择器

2. 时长提取逻辑：根据目标网站结构调整 estimate_video_duration 方法

3. 文件类型：在 is_video_file 方法中添加更多视频格式

## 基本使用

crawler = VideoCrawler()

crawler.crawl_website("https://example.com/videos")

## 高级配置

crawler.set_download_directory("./custom_videos")

crawler.set_min_duration(600)  # 10分钟

crawler.crawl_website("https://target-site.com", max_pages=20)# permanent