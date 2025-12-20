import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd # 为了方便处理数据，我们使用 pandas

def scrape_shanghairanking_with_selenium(url, max_retries=3):
    """
    使用 Selenium 加载页面，然后用 BeautifulSoup 解析。
    尝试滚动页面或点击加载更多按钮（如果存在）。
    """
    # --- 请根据你的系统和 ChromeDriver 位置修改路径 ---
    # 例如 Windows: "D:/chromedriver.exe"
    # 例如 macOS/Linux: "/usr/local/bin/chromedriver"
    service = Service('chromedriver') # 请确保 chromedriver 在 PATH 中或指定路径
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless') # 取消注释此行以无头模式运行 (不显示浏览器窗口)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    universities = []
    try:
        print(f"正在打开页面: {url}")
        driver.get(url)
        
        # 等待页面主要内容加载
        wait = WebDriverWait(driver, 10)
        # 等待排名表格出现 (根据实际页面元素调整定位器)
        table_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.rk-table, table"))) # 尝试常见的表格类名或标签

        # --- 检查是否有“加载更多”或分页按钮 ---
        # 这里需要根据实际网页结构查找，假设可能的按钮
        load_more_button_selector = "button.load-more, a.more-link, .pager-next" # 示例选择器，请根据实际调整
        page_button_selector = ".pagination .page-item a" # 示例分页按钮选择器，请根据实际调整
        
        # 尝试滚动到底部，看是否触发动态加载 (如果适用)
        print("尝试滚动页面以加载更多内容...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scroll_attempts = 10 # 设置最大滚动次数，避免无限循环

        while scroll_attempts < max_scroll_attempts:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2) # 等待内容加载

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("页面高度未变，可能已加载全部内容或滚动加载机制不适用。")
                break
            last_height = new_height
            scroll_attempts += 1
            print(f"已滚动 {scroll_attempts} 次...")

        # 尝试查找并点击“加载更多”按钮 (如果存在)
        try:
            load_more_button = driver.find_element(By.CSS_SELECTOR, load_more_button_selector)
            print("找到“加载更多”按钮，尝试点击...")
            driver.execute_script("arguments[0].click();", load_more_button) # 使用 JS 点击，更可靠
            time.sleep(3) # 等待点击后内容加载
        except NoSuchElementException:
            print(f"未找到“加载更多”按钮 (选择器: {load_more_button_selector})")

        # 获取页面完全加载后的源代码
        page_source = driver.page_source

        # 使用 BeautifulSoup 解析
        soup = BeautifulSoup(page_source, 'html.parser')

        # 尝试查找表格 (可能需要根据实际HTML结构调整)
        table = soup.find('table', class_='rk-table') # 假设类名是 rk-table，根据实际检查
        if not table:
             table = soup.find('table') # 作为备选

        if not table:
            print("在页面源代码中未找到排名表格。")
            return universities

        rows = table.find_all('tr')
        if not rows:
            print("在表格中未找到行数据。")
            return universities

        print(f"找到 {len(rows)-1} 行数据 (包含表头)。开始解析...")
        for row in rows[1:]: # 跳过表头
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 5: # 确保有足够列
                try:
                    rank = cells[0].get_text(strip=True)
                    name_cell = cells[1]
                    # 提取学校名称 (处理图片和文本)
                    img_tag = name_cell.find('img')
                    name_text = name_cell.get_text(strip=True)
                    if img_tag:
                        # 简单移除 img 标签后的内容，通常中文名在后面
                        import re
                        clean_text = re.sub(r'<img[^>]*>', '', str(name_cell))
                        clean_text = BeautifulSoup(clean_text, 'html.parser').get_text()
                        # 提取中文名 (假设中文名在最前面，且包含中文字符)
                        name_match = re.match(r'([^\x00-\x7F\s]+)', clean_text.strip())
                        name = name_match.group(1).strip() if name_match else clean_text.strip().split('\n')[0]
                    else:
                        name = name_text.split('\n')[0] if '\n' in name_text else name_text

                    location = cells[2].get_text(strip=True)
                    type_ = cells[3].get_text(strip=True)
                    score = cells[4].get_text(strip=True)

                    if rank and name and location and type_ and score:
                        university = {
                            'rank': rank,
                            'name': name,
                            'location': location,
                            'type': type_,
                            'score': score
                        }
                        universities.append(university)
                    else:
                        print(f"警告: 某行数据不完整，跳过。数据: {university}")

                except (IndexError, AttributeError) as e:
                    print(f"处理行时出错: {e}")
                    continue

        print(f"成功解析 {len(universities)} 条大学数据。")

    except TimeoutException:
        print("页面加载超时。")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        driver.quit() # 确保关闭浏览器

    return universities

if __name__ == "__main__":
    url = "https://www.shanghairanking.cn/rankings/bcur/2025"
    print("开始使用 Selenium 爬取软科 2025 中国大学排行榜...")

    ranking_data = scrape_shanghairanking_with_selenium(url)

    if ranking_data:
        df = pd.DataFrame(ranking_data)
        print("\n--- 爬取到的大学排名数据 ---")
        # 显示所有行 (如果数据量大，可以只显示前100或全部)
        # 由于网页只显示前30名，这里显示所有爬取到的
        print(df.to_string(index=False)) 

        # 如果你想强制显示前100名，即使数据不足
        print(f"\n--- 前 100 名大学清单 (共 {len(df)} 所) ---")
        top_100_df = df.head(100) # 取前100条，如果不足则取全部
        print(top_100_df.to_string(index=False))
        
        # 可选：保存到 CSV 文件
        # df.to_csv('shanghairanking_bcur_2025.csv', index=False, encoding='utf-8-sig')
        # print("\n数据已保存到 'shanghairanking_bcur_2025.csv'")
    else:
        print("未能获取到任何大学排名数据。")
