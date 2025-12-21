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
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RobustVideoCrawler:
    def __init__(self, download_dir: str = "./videos", min_duration: int = 300, max_workers: int = 3):
        """
        初始化稳健视频爬虫
        
        Args:
            download_dir: 下载目录
            min_duration: 最小视频时长（秒），默认5分钟
            max_workers: 最大并发下载线程数
        """
        self.download_dir = Path(download_dir)
        self.min_duration = min_duration
        self.max_workers = max_workers
        self.downloaded_urls = set()
        self.visited_urls = set()
        self.videos_to_download = []
        self.download_attempts = {}  # 记录下载尝试次数
        
        # 创建下载目录
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # 请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # 会话
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # 常见视频网站的关键词和模式
        self.video_keywords = ['视频', 'movie', 'film', 'video', '影视', '娱乐', 'tv', 'show', '剧集']
        self.video_page_patterns = [
            r'/video/',
            r'/movie/',
            r'/film/',
            r'/play/',
            r'/watch/',
            r'/v/',
            r'\.mp4',
            r'\.avi',
            r'\.mov',
            r'\.wmv'
        ]
        
        # 下载配置
        self.chunk_size = 8192  # 分块大小
        self.max_retries = 5    # 最大重试次数
        self.timeout = 60       # 超时时间（秒）

    def set_download_directory(self, directory: str):
        """设置下载目录"""
        self.download_dir = Path(directory)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"下载目录已设置为: {directory}")

    def set_min_duration(self, duration: int):
        """设置最小视频时长"""
        self.min_duration = duration
        logger.info(f"最小视频时长已设置为: {duration}秒")

    def discover_video_sections(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        发现网站中的视频区域链接
        """
        video_sections = []
        
        # 查找包含视频关键词的链接
        for keyword in self.video_keywords:
            links = soup.find_all('a', href=True, string=re.compile(keyword, re.IGNORECASE))
            for link in links:
                href = link.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    video_sections.append(full_url)
        
        # 查找常见的视频页面模式
        for pattern in self.video_page_patterns:
            links = soup.find_all('a', href=re.compile(pattern, re.IGNORECASE))
            for link in links:
                href = link.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    video_sections.append(full_url)
        
        # 查找导航菜单中的视频相关链接
        nav_selectors = ['nav', '.navigation', '.menu', '.nav', '#nav', '#menu']
        for selector in nav_selectors:
            nav_elements = soup.select(selector)
            for nav in nav_elements:
                links = nav.find_all('a', href=True)
                for link in links:
                    link_text = link.get_text().lower()
                    if any(keyword in link_text for keyword in self.video_keywords):
                        href = link.get('href')
                        full_url = urljoin(base_url, href)
                        video_sections.append(full_url)
        
        # 去重
        return list(set(video_sections))

    def search_videos_on_site(self, base_url: str, search_terms: List[str] = None) -> List[str]:
        """
        在网站上搜索视频内容
        """
        if search_terms is None:
            search_terms = ['video', 'movie', 'film', '视频', '电影']
        
        search_urls = []
        
        # 尝试常见的搜索URL模式
        search_patterns = [
            f"{base_url.rstrip('/')}/search?q={{term}}",
            f"{base_url.rstrip('/')}/search/?q={{term}}",
            f"{base_url.rstrip('/')}/search?query={{term}}",
            f"{base_url.rstrip('/')}/search/{{term}}",
            f"{base_url.rstrip('/')}/videos/search?q={{term}}",
        ]
        
        for term in search_terms:
            for pattern in search_patterns:
                try:
                    search_url = pattern.format(term=term)
                    # 测试URL是否有效
                    response = self.session.head(search_url, timeout=5)
                    if response.status_code == 200:
                        search_urls.append(search_url)
                        logger.info(f"发现搜索URL: {search_url}")
                except:
                    continue
        
        return search_urls

    def extract_video_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """
        从页面中提取视频链接和相关信息
        """
        videos = []
        
        # 扩展视频选择器
        video_selectors = [
            # HTML5 video标签
            ('video', 'src'),
            ('video source', 'src'),
            # 嵌入式视频
            ('iframe[src*="youtube"]', 'src'),
            ('iframe[src*="vimeo"]', 'src'),
            ('iframe[src*="video"]', 'src'),
            ('iframe[src*="movie"]', 'src'),
            # 视频文件链接
            ('a[href*=".mp4"]', 'href'),
            ('a[href*=".avi"]', 'href'),
            ('a[href*=".mov"]', 'href'),
            ('a[href*=".wmv"]', 'href'),
            ('a[href*=".flv"]', 'href'),
            ('a[href*=".webm"]', 'href'),
            ('a[href*=".mkv"]', 'href'),
            # 视频播放页面
            ('a[href*="/video/"]', 'href'),
            ('a[href*="/movie/"]', 'href'),
            ('a[href*="/play/"]', 'href'),
            ('a[href*="/watch/"]', 'href'),
        ]
        
        for selector, attr in video_selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    video_url = element.get(attr)
                    if video_url:
                        # 处理相对URL
                        full_url = urljoin(base_url, video_url)
                        
                        # 获取视频标题
                        title = self.extract_video_title(element)
                        
                        # 估算视频时长
                        duration = self.estimate_video_duration(element, full_url)
                        
                        videos.append({
                            'url': full_url,
                            'title': title,
                            'duration': duration,
                            'source_page': base_url
                        })
            except Exception as e:
                logger.debug(f"提取视频链接时出错 {selector}: {e}")
                continue
        
        return videos

    def extract_video_title(self, element) -> str:
        """提取视频标题"""
        title_sources = [
            element.get('title'),
            element.get('alt'),
            element.get('data-title'),
            element.get_text(strip=True),
            element.find_previous(['h1', 'h2', 'h3', 'h4']),
            element.find_parent('div', class_=re.compile('title|name|caption')),
        ]
        
        for title in title_sources:
            if title and isinstance(title, str) and len(title.strip()) > 0:
                clean_title = re.sub(r'\s+', ' ', title.strip())
                return clean_title[:100]
            elif hasattr(title, 'get_text'):
                text = title.get_text(strip=True)
                if text:
                    clean_text = re.sub(r'\s+', ' ', text.strip())
                    return clean_text[:100]
        
        return f"video_{int(time.time())}"

    def estimate_video_duration(self, element, video_url: str) -> int:
        """估算视频时长"""
        # 从元素属性中提取
        duration_attrs = ['data-duration', 'duration', 'data-length', 'length', 'data-time']
        for attr in duration_attrs:
            duration_str = element.get(attr)
            if duration_str:
                duration = self.parse_duration_string(duration_str)
                if duration and duration > 0:
                    return duration
        
        # 从父元素或兄弟元素中查找
        parent = element.parent
        for _ in range(3):  # 向上查找3层
            if parent:
                duration_text = parent.get_text()
                duration = self.extract_duration_from_text(duration_text)
                if duration and duration > 0:
                    return duration
                parent = parent.parent
        
        # 从URL中提取
        url_duration = self.extract_duration_from_url(video_url)
        if url_duration:
            return url_duration
        
        # 默认返回中等时长
        return 600

    def extract_duration_from_url(self, url: str) -> Optional[int]:
        """从URL中提取时长信息"""
        patterns = [
            r'duration[=_-](\d+)',
            r'dur[=_-](\d+)',
            r'time[=_-](\d+)',
            r'(\d+)min',
            r'(\d+)分钟',
            r'(\d+):(\d+):(\d+)',
            r'(\d+):(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                if ':' in pattern:
                    if len(match.groups()) == 3:  # HH:MM:SS
                        hours, minutes, seconds = map(int, match.groups())
                        return hours * 3600 + minutes * 60 + seconds
                    else:  # MM:SS
                        minutes, seconds = map(int, match.groups())
                        return minutes * 60 + seconds
                else:
                    return int(match.group(1)) * 60
        
        return None

    def extract_duration_from_text(self, text: str) -> Optional[int]:
        """从文本中提取时长信息"""
        # 匹配时间格式
        time_patterns = [
            r'(\d+):(\d+):(\d+)',  # HH:MM:SS
            r'(\d+):(\d+)',        # MM:SS
            r'(\d+)\s*小时\s*(\d+)\s*分钟',
            r'(\d+)\s*小时',
            r'(\d+)\s*分钟',
            r'(\d+)\s*min',
            r'(\d+)\s*hr',
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text)
            if match:
                groups = match.groups()
                if pattern == r'(\d+):(\d+):(\d+)':
                    hours, minutes, seconds = map(int, groups)
                    return hours * 3600 + minutes * 60 + seconds
                elif pattern == r'(\d+):(\d+)':
                    minutes, seconds = map(int, groups)
                    return minutes * 60 + seconds
                elif pattern == r'(\d+)\s*小时\s*(\d+)\s*分钟':
                    hours, minutes = map(int, groups)
                    return hours * 3600 + minutes * 60
                elif pattern == r'(\d+)\s*小时':
                    return int(groups[0]) * 3600
                elif pattern in [r'(\d+)\s*分钟', r'(\d+)\s*min']:
                    return int(groups[0]) * 60
                elif pattern == r'(\d+)\s*hr':
                    return int(groups[0]) * 3600
        
        return None

    def parse_duration_string(self, duration_str: str) -> Optional[int]:
        """解析时长字符串"""
        try:
            if duration_str.isdigit():
                return int(duration_str)
            return self.extract_duration_from_text(duration_str)
        except:
            return None

    def is_video_file(self, url: str) -> bool:
        """检查URL是否是视频文件"""
        video_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.m4v', '.3gp']
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        
        return any(path.endswith(ext) for ext in video_extensions)

    def is_video_page(self, url: str) -> bool:
        """检查URL是否是视频页面"""
        for pattern in self.video_page_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        return False

    def download_video(self, video_info: Dict) -> bool:
        """稳健地下载视频文件，支持断点续传"""
        url = video_info['url']
        title = video_info['title']
        
        if url in self.downloaded_urls:
            logger.info(f"视频已下载，跳过: {title}")
            return True
        
        # 初始化下载尝试次数
        if url not in self.download_attempts:
            self.download_attempts[url] = 0
        
        # 如果不是视频文件，尝试从页面中提取视频
        if not self.is_video_file(url):
            logger.info(f"URL不是直接视频文件，尝试从页面提取: {url}")
            page_videos = self.extract_videos_from_page(url)
            if page_videos:
                # 使用页面中的第一个视频
                video_info['url'] = page_videos[0]['url']
                video_info['title'] = page_videos[0].get('title', title)
                url = video_info['url']
                logger.info(f"从页面提取到视频: {video_info['url']}")
            else:
                logger.warning(f"无法从页面提取视频: {url}")
                return False
        
        # 清理文件名
        safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)
        file_extension = self.get_file_extension(url)
        filename = self.download_dir / f"{safe_title}_{int(time.time())}{file_extension}"
        
        # 临时文件名（下载中）
        temp_filename = filename.with_suffix('.download')
        
        # 检查是否已经有部分下载的文件
        downloaded_size = 0
        if temp_filename.exists():
            downloaded_size = temp_filename.stat().st_size
            logger.info(f"发现未完成的下载，已下载: {downloaded_size / (1024*1024):.2f} MB")
        
        # 尝试下载（支持断点续传）
        for attempt in range(self.max_retries):
            try:
                self.download_attempts[url] += 1
                logger.info(f"下载尝试 {self.download_attempts[url]}/{self.max_retries}: {title}")
                
                success = self._download_with_resume(
                    url, temp_filename, filename, 
                    downloaded_size, video_info
                )
                
                if success:
                    self.downloaded_urls.add(url)
                    logger.info(f"下载完成: {filename}")
                    return True
                else:
                    logger.warning(f"下载失败，准备重试: {title}")
                    
            except Exception as e:
                logger.error(f"下载异常 {title} (尝试 {attempt+1}/{self.max_retries}): {str(e)}")
            
            # 重试前等待
            if attempt < self.max_retries - 1:
                wait_time = (attempt + 1) * 10  # 递增等待时间
                logger.info(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
        
        logger.error(f"下载失败，已达到最大重试次数: {title}")
        # 清理临时文件
        if temp_filename.exists():
            temp_filename.unlink()
        return False

    def _download_with_resume(self, url: str, temp_filename: Path, final_filename: Path, 
                            start_byte: int, video_info: Dict) -> bool:
        """支持断点续传的下载实现"""
        headers = self.headers.copy()
        
        # 如果已经有部分下载，添加Range头
        if start_byte > 0:
            headers['Range'] = f'bytes={start_byte}-'
        
        try:
            response = self.session.get(url, stream=True, timeout=self.timeout, headers=headers)
            response.raise_for_status()
            
            # 检查服务器是否支持断点续传
            if start_byte > 0 and response.status_code != 206:
                logger.warning("服务器不支持断点续传，重新开始下载")
                start_byte = 0
                if temp_filename.exists():
                    temp_filename.unlink()
            
            # 获取文件总大小
            total_size = int(response.headers.get('content-length', 0))
            if start_byte > 0 and 'content-range' in response.headers:
                # 从Content-Range头获取总大小
                content_range = response.headers.get('content-range')
                if content_range:
                    total_size = int(content_range.split('/')[-1])
            
            if total_size == 0:
                logger.warning("无法获取文件大小，可能无法检测下载完整性")
            
            # 计算实际需要下载的大小
            actual_total_size = total_size
            if start_byte > 0:
                actual_total_size = total_size - start_byte
            
            logger.info(f"开始下载: {video_info['title']}")
            logger.info(f"视频时长: {video_info['duration']}秒")
            if total_size > 0:
                logger.info(f"文件总大小: {total_size / (1024*1024):.2f} MB")
            if start_byte > 0:
                logger.info(f"已下载: {start_byte / (1024*1024):.2f} MB, 剩余: {actual_total_size / (1024*1024):.2f} MB")
            
            # 打开文件（追加模式如果已存在部分内容）
            mode = 'ab' if start_byte > 0 else 'wb'
            with open(temp_filename, mode) as f:
                downloaded_size = start_byte
                last_log_time = time.time()
                
                for chunk in response.iter_content(chunk_size=self.chunk_size):
                    if chunk:
                        f.write(chunk)
                        f.flush()  # 确保数据写入磁盘
                        downloaded_size += len(chunk)
                        
                        # 定期记录进度（避免过于频繁的日志）
                        current_time = time.time()
                        if current_time - last_log_time > 5:  # 每5秒记录一次
                            if total_size > 0:
                                percent = (downloaded_size / total_size) * 100
                                logger.info(f"下载进度: {percent:.1f}% ({downloaded_size / (1024*1024):.2f} MB / {total_size / (1024*1024):.2f} MB)")
                            else:
                                logger.info(f"已下载: {downloaded_size / (1024*1024):.2f} MB")
                            last_log_time = current_time
                
                # 下载完成后验证文件大小
                if total_size > 0 and downloaded_size != total_size:
                    logger.warning(f"文件大小不匹配: 期望 {total_size} 字节, 实际 {downloaded_size} 字节")
                    return False
            
            # 重命名临时文件为最终文件名
            temp_filename.rename(final_filename)
            
            # 验证文件完整性（基本检查）
            final_size = final_filename.stat().st_size
            if total_size > 0 and final_size != total_size:
                logger.error(f"最终文件大小不匹配: 期望 {total_size} 字节, 实际 {final_size} 字节")
                return False
            
            logger.info(f"文件验证通过: {final_filename}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"下载请求失败: {str(e)}")
            return False
        except IOError as e:
            logger.error(f"文件写入失败: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"下载过程中发生未知错误: {str(e)}")
            return False

    def extract_videos_from_page(self, page_url: str) -> List[Dict]:
        """从页面中提取视频链接"""
        try:
            soup = self.get_page_soup(page_url)
            if not soup:
                return []
            
            return self.extract_video_links(soup, page_url)
        except Exception as e:
            logger.error(f"从页面提取视频失败 {page_url}: {str(e)}")
            return []

    def get_file_extension(self, url: str) -> str:
        """从URL获取文件扩展名"""
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        
        video_extensions = {
            '.mp4': '.mp4',
            '.avi': '.avi',
            '.mov': '.mov',
            '.wmv': '.wmv',
            '.flv': '.flv',
            '.webm': '.webm',
            '.mkv': '.mkv',
            '.m4v': '.m4v',
            '.3gp': '.3gp'
        }
        
        for ext, result_ext in video_extensions.items():
            if path.endswith(ext):
                return result_ext
        
        # 默认使用mp4
        return '.mp4'

    def crawl_website_advanced(self, start_url: str, max_depth: int = 3, max_pages: int = 50):
        """
        高级网站爬取，能够发现视频区域和搜索视频内容
        
        Args:
            start_url: 起始URL
            max_depth: 最大爬取深度
            max_pages: 最大爬取页面数
        """
        logger.info(f"开始高级爬取: {start_url}")
        
        # 首先发现视频区域
        initial_soup = self.get_page_soup(start_url)
        if not initial_soup:
            logger.error(f"无法访问起始页面: {start_url}")
            return
        
        video_sections = self.discover_video_sections(initial_soup, start_url)
        logger.info(f"发现 {len(video_sections)} 个视频区域")
        
        # 尝试搜索功能
        search_urls = self.search_videos_on_site(start_url)
        logger.info(f"发现 {len(search_urls)} 个搜索URL")
        
        # 合并所有要爬取的URL
        urls_to_crawl = list(set(video_sections + search_urls + [start_url]))
        
        pages_crawled = 0
        for url in urls_to_crawl:
            if pages_crawled >= max_pages:
                break
                
            if url in self.visited_urls:
                continue
                
            try:
                logger.info(f"爬取页面: {url}")
                soup = self.get_page_soup(url)
                if not soup:
                    continue
                
                # 提取视频
                videos = self.extract_video_links(soup, url)
                logger.info(f"在页面中找到 {len(videos)} 个视频")
                
                # 收集符合条件的视频
                for video in videos:
                    if video['duration'] >= self.min_duration:
                        logger.info(f"找到符合条件的视频: {video['title']} ({video['duration']}秒)")
                        self.videos_to_download.append(video)
                    else:
                        logger.debug(f"跳过短视频: {video['title']} ({video['duration']}秒)")
                
                self.visited_urls.add(url)
                pages_crawled += 1
                
                # 随机延迟，避免被封
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                logger.error(f"爬取页面失败 {url}: {str(e)}")
                continue
        
        # 爬取完成后开始下载
        self.download_all_videos()

    def download_all_videos(self):
        """下载所有收集到的视频"""
        if not self.videos_to_download:
            logger.info("没有找到符合条件的视频")
            return
        
        logger.info(f"开始下载 {len(self.videos_to_download)} 个视频")
        
        # 使用线程池并发下载（但限制并发数，避免过多大文件同时下载）
        with ThreadPoolExecutor(max_workers=min(self.max_workers, 2)) as executor:  # 大文件下载限制并发数
            # 提交所有下载任务
            future_to_video = {
                executor.submit(self.download_video, video): video 
                for video in self.videos_to_download
            }
            
            # 等待所有任务完成
            completed = 0
            failed = 0
            for future in as_completed(future_to_video):
                video = future_to_video[future]
                try:
                    success = future.result()
                    if success:
                        completed += 1
                        logger.info(f"成功下载视频: {video['title']} ({completed}/{len(self.videos_to_download)})")
                    else:
                        failed += 1
                        logger.error(f"下载失败: {video['title']}")
                except Exception as e:
                    failed += 1
                    logger.error(f"下载视频出错 {video['title']}: {str(e)}")
        
        logger.info(f"下载完成: {completed} 成功, {failed} 失败, 总计 {len(self.videos_to_download)} 个视频")

    def get_page_soup(self, url: str) -> Optional[BeautifulSoup]:
        """获取页面的BeautifulSoup对象"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logger.error(f"获取页面失败 {url}: {str(e)}")
            return None

    def save_progress(self):
        """保存下载进度"""
        progress_file = self.download_dir / "download_progress.json"
        progress_data = {
            'downloaded_urls': list(self.downloaded_urls),
            'visited_urls': list(self.visited_urls),
            'download_dir': str(self.download_dir),
            'min_duration': self.min_duration,
            'videos_to_download_count': len(self.videos_to_download),
            'download_attempts': self.download_attempts
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
                self.visited_urls = set(progress_data.get('visited_urls', []))
                self.download_attempts = progress_data.get('download_attempts', {})
                logger.info(f"已加载 {len(self.downloaded_urls)} 个已下载记录和 {len(self.visited_urls)} 个已访问页面")

def main():
    """主函数 - 使用示例"""
    # 创建稳健爬虫实例
    crawler = RobustVideoCrawler(
        download_dir="./downloaded_videos",
        min_duration=300,  # 5分钟
        max_workers=2      # 大文件下载限制并发数
    )
    
    # 加载之前的进度
    crawler.load_progress()
    
    # 要爬取的网站列表
    websites = [
        #"https://cn.pornhub.com/",
        #"https://www.xvideos.com/",
        #"https://www.redtube.com/",
        #"https://www.youporn.com/",
        #"https://www.spankbang.com/",
        "https://2b82e435.com/category/64",
        # 添加更多视频网站...
    ]
    
    # 开始高级爬取和下载
    for website in websites:
        logger.info(f"开始爬取和下载网站: {website}")
        crawler.crawl_website_advanced(website, max_depth=2, max_pages=20)
    
    # 保存进度
    crawler.save_progress()
    
    logger.info("爬取和下载任务完成！")

if __name__ == "__main__":
    main()