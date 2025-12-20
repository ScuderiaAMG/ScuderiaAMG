import requests
from bs4 import BeautifulSoup
import time
import random
from prettytable import PrettyTable

def scrape_ranking_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return []
    soup = BeautifulSoup(response.text, 'html.parser')
    table_element = soup.find('table')
    if not table_element:
        print("未找到表格元素")
        return []
    universities = []
    rows = table_element.find_all('tr')
    for row in rows[1:]:
        cells = row.find_all(['td'])
        if len(cells) >= 6:
            try:
                rank = cells[0].get_text(strip=True)
                name_info = cells[1].get_text(strip=True)
                name = name_info.split('\n')[0] if '\n' in name_info else name_info
                location = cells[2].get_text(strip=True)
                type_ = cells[3].get_text(strip=True)
                score = cells[4].get_text(strip=True)
                university = {
                    'rank': rank,
                    'name': name,
                    'location': location,
                    'type': type_,
                    'score': score
                }
                universities.append(university)
            except IndexError:
                continue
    return universities

def scrape_all_pages(base_url, total_rankings=100):
    all_universities = []
    page = 1
    while len(all_universities) < total_rankings:
        url = f"{base_url}?page={page}"
        print(f"正在爬取第 {page} 页...")
        page_universities = scrape_ranking_page(url)
        if not page_universities:
            print(f"第 {page} 页没有获取到数据，停止爬取。")
            break
        all_universities.extend(page_universities)
        page += 1
        time.sleep(random.uniform(0.5, 1.5))
    return all_universities[:total_rankings]

if __name__ == "__main__":
    base_url = "https://www.compassedu.hk/rk"
    ranking_data = scrape_all_pages(base_url, 100)
    table = PrettyTable()
    table.field_names = ["排名", "学校名称", "省市", "类型", "总分"]
    for uni in ranking_data:
        table.add_row([uni['rank'], uni['name'], uni['location'], uni['type'], uni['score']])
    table.align["学校名称"] = "l"
    table.align["省市"] = "c"
    table.align["类型"] = "c"
    print(table)