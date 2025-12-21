import os
import re
import time
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import json
from pathlib import Path
import logging
from typing import List, Dict, Optional

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VideoCrawler:
    def __init__(self, download_dir: str = "./videos", min_duration: int = 300):
        """
        初始化视频爬虫
        
        Args:
            download_dir: 下载目录
            min_duration: 最小视频时长（秒），默认5分钟
        """
        self.download_dir = Path(download_dir)
        self.min_duration = min_duration
        self.downloaded_urls = set()
        
        # 创建下载目录
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # 请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 会话
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def set_download_directory(self, directory: str):
        """设置下载目录"""
        self.download_dir = Path(directory)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"下载目录已设置为: {directory}")

    def set_min_duration(self, duration: int):
        """设置最小视频时长"""
        self.min_duration = duration
        logger.info(f"最小视频时长已设置为: {duration}秒")

    def extract_video_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """
        从页面中提取视频链接和相关信息
        
        Args:
            soup: BeautifulSoup对象
            base_url: 基础URL
            
        Returns:
            视频信息列表
        """
        videos = []
        
        # 常见的视频标签和属性
        video_selectors = [
            # HTML5 video标签
            ('video', 'src'),
            ('video source', 'src'),
            # 嵌入式视频（YouTube, Vimeo等）
            ('iframe[src*="youtube"]', 'src'),
            ('iframe[src*="vimeo"]', 'src'),
            # 其他常见的视频容器
            ('a[href*=".mp4"]', 'href'),
            ('a[href*=".avi"]', 'href'),
            ('a[href*=".mov"]', 'href'),
            ('a[href*=".wmv"]', 'href'),
            ('a[href*=".flv"]', 'href'),
            ('a[href*=".webm"]', 'href'),
        ]
        
        for selector, attr in video_selectors:
            elements = soup.select(selector)
            for element in elements:
                video_url = element.get(attr)
                if video_url:
                    # 处理相对URL
                    full_url = urljoin(base_url, video_url)
                    
                    # 获取视频标题
                    title = self.extract_video_title(element)
                    
                    # 估算视频时长（这里需要根据具体网站调整）
                    duration = self.estimate_video_duration(element, full_url)
                    
                    videos.append({
                        'url': full_url,
                        'title': title,
                        'duration': duration,
                        'element': str(element)[:100]  # 用于调试
                    })
        
        return videos

    def extract_video_title(self, element) -> str:
        """提取视频标题"""
        # 从常见属性中提取标题
        title_sources = [
            element.get('title'),
            element.get('alt'),
            element.get_text(strip=True),
            element.find_previous(['h1', 'h2', 'h3', 'h4']),
            element.find_parent().get('title') if element.find_parent() else None
        ]
        
        for title in title_sources:
            if title and isinstance(title, str) and len(title) > 0:
                return title[:100]  # 限制标题长度
            elif hasattr(title, 'get_text'):
                text = title.get_text(strip=True)
                if text:
                    return text[:100]
        
        return "未知标题"

    def estimate_video_duration(self, element, video_url: str) -> int:
        """
        估算视频时长
        注意：这是一个示例实现，实际应用中需要根据具体网站调整
        """
        # 方法1: 从URL中提取时长信息
        url_duration = self.extract_duration_from_url(video_url)
        if url_duration:
            return url_duration
        
        # 方法2: 从元素属性中提取
        duration_attrs = ['data-duration', 'duration', 'data-length', 'length']
        for attr in duration_attrs:
            duration_str = element.get(attr)
            if duration_str:
                duration = self.parse_duration_string(duration_str)
                if duration:
                    return duration
        
        # 方法3: 从父元素或兄弟元素中查找时长信息
        parent = element.parent
        if parent:
            duration_text = parent.get_text()
            duration = self.extract_duration_from_text(duration_text)
            if duration:
                return duration
        
        # 默认返回一个中等时长，实际使用中可能需要更精确的方法
        return 600  # 默认10分钟

    def extract_duration_from_url(self, url: str) -> Optional[int]:
        """从URL中提取时长信息"""
        # 这里可以根据具体网站的URL模式进行调整
        patterns = [
            r'duration[=_-](\d+)',
            r'dur[=_-](\d+)',
            r'time[=_-](\d+)',
            r'(\d+)min',
            r'(\d+)分钟'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return int(match.group(1)) * 60  # 转换为秒
        
        return None

    def extract_duration_from_text(self, text: str) -> Optional[int]:
        """从文本中提取时长信息"""
        # 匹配 "HH:MM:SS" 或 "MM:SS" 格式
        time_pattern = r'(\d+):(\d+)(?::(\d+))?'
        match = re.search(time_pattern, text)
        if match:
            if match.group(3):  # HH:MM:SS
                hours, minutes, seconds = map(int, match.groups())
                return hours * 3600 + minutes * 60 + seconds
            else:  # MM:SS
                minutes, seconds = map(int, match.groups()[:2])
                return minutes * 60 + seconds
        
        # 匹配 "X分钟" 格式
        minute_pattern = r'(\d+)\s*分钟'
        match = re.search(minute_pattern, text)
        if match:
            return int(match.group(1)) * 60
        
        return None

    def parse_duration_string(self, duration_str: str) -> Optional[int]:
        """解析时长字符串"""
        try:
            # 如果是纯数字，假设是秒数
            if duration_str.isdigit():
                return int(duration_str)
            
            # 尝试解析时间格式
            return self.extract_duration_from_text(duration_str)
        except:
            return None

    def is_video_file(self, url: str) -> bool:
        """检查URL是否是视频文件"""
        video_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.m4v']
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        
        return any(path.endswith(ext) for ext in video_extensions)

    def download_video(self, video_info: Dict) -> bool:
        """
        下载视频文件
        
        Args:
            video_info: 视频信息字典
            
        Returns:
            下载是否成功
        """
        url = video_info['url']
        title = video_info['title']
        
        # 跳过已下载的URL
        if url in self.downloaded_urls:
            logger.info(f"视频已下载，跳过: {title}")
            return False
        
        # 检查是否是视频文件
        if not self.is_video_file(url):
            logger.warning(f"URL不是视频文件: {url}")
            return False
        
        try:
            # 清理文件名
            safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)
            filename = self.download_dir / f"{safe_title}_{int(time.time())}.mp4"
            
            logger.info(f"开始下载: {title}")
            logger.info(f"视频时长: {video_info['duration']}秒")
            logger.info(f"视频URL: {url}")
            
            # 发送HEAD请求获取文件信息
            head_response = self.session.head(url, allow_redirects=True)
            content_length = head_response.headers.get('content-length')
            
            if content_length:
                file_size = int(content_length)
                logger.info(f"文件大小: {file_size / (1024*1024):.2f} MB")
            
            # 下载文件
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            self.downloaded_urls.add(url)
            logger.info(f"下载完成: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"下载失败 {title}: {str(e)}")
            return False

    def crawl_website(self, url: str, max_pages: int = 10):
        """
        爬取网站并下载视频
        
        Args:
            url: 起始URL
            max_pages: 最大爬取页面数
        """
        visited_urls = set()
        urls_to_visit = [url]
        pages_crawled = 0
        
        while urls_to_visit and pages_crawled < max_pages:
            current_url = urls_to_visit.pop(0)
            
            if current_url in visited_urls:
                continue
                
            try:
                logger.info(f"爬取页面: {current_url}")
                response = self.session.get(current_url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 提取视频链接
                videos = self.extract_video_links(soup, current_url)
                logger.info(f"在页面中找到 {len(videos)} 个视频")
                
                # 过滤并下载符合条件的视频
                for video in videos:
                    if video['duration'] >= self.min_duration:
                        logger.info(f"找到符合条件的视频: {video['title']} ({video['duration']}秒)")
                        self.download_video(video)
                    else:
                        logger.info(f"跳过短视频: {video['title']} ({video['duration']}秒)")
                
                # 提取新的链接继续爬取
                new_links = self.extract_links(soup, current_url)
                for link in new_links:
                    if link not in visited_urls and link not in urls_to_visit:
                        urls_to_visit.append(link)
                
                visited_urls.add(current_url)
                pages_crawled += 1
                
                # 礼貌性延迟
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"爬取页面失败 {current_url}: {str(e)}")
                continue

    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """提取页面中的所有链接"""
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(base_url, href)
            
            # 过滤掉非HTTP链接和明显不是内容页的链接
            if (full_url.startswith('http') and 
                not any(ignore in full_url for ignore in ['#', 'javascript:', 'mailto:'])):
                links.append(full_url)
        
        return links

    def save_progress(self):
        """保存下载进度"""
        progress_file = self.download_dir / "download_progress.json"
        progress_data = {
            'downloaded_urls': list(self.downloaded_urls),
            'download_dir': str(self.download_dir),
            'min_duration': self.min_duration
        }
        
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)

    def load_progress(self):
        """加载下载进度"""
        progress_file = self.download_dir / "download_progress.json"
        if progress_file.exists():
            with open(progress_file, 'r', encoding='utf-8') as f:
                progress_data = json.load(f)
                self.downloaded_urls = set(progress_data.get('downloaded_urls', []))
                logger.info(f"已加载 {len(self.downloaded_urls)} 个已下载记录")

def main():
    """主函数 - 使用示例"""
    # 创建爬虫实例
    crawler = VideoCrawler()
    
    # 配置参数
    crawler.set_download_directory("./my_videos")  # 设置下载目录
    crawler.set_min_duration(300)  # 设置最小时长（5分钟）
    
    # 加载之前的下载进度（如果存在）
    crawler.load_progress()
    
    # 要爬取的网站URL列表
    websites = [
        "https://cn.pornhub.com/",
        # 添加更多网站URL...
    ]
    
    # 开始爬取
    for website in websites:
        logger.info(f"开始爬取网站: {website}")
        crawler.crawl_website(website, max_pages=5)  # 每个网站最多爬取5页
    
    # 保存下载进度
    crawler.save_progress()
    
    logger.info("爬取任务完成！")

if __name__ == "__main__":
    main()