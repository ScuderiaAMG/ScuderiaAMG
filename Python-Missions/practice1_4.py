import requests
from bs4 import BeautifulSoup
import time
import random
from prettytable import PrettyTable

def scrape_ranking(url):
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

if __name__ == "__main__":
    url = "https://www.shanghairanking.cn/rankings/bcur/2025"
    print("开始爬取软科中国大学排名 (2025)...")
    ranking_data = scrape_ranking(url)
    table = PrettyTable()
    table.field_names = ["排名", "学校名称", "省市", "类型", "总分"]
    for uni in ranking_data[:100]:
        table.add_row([uni['rank'], uni['name'], uni['location'], uni['type'], uni['score']])
    table.align["学校名称"] = "l"
    table.align["省市"] = "c"
    table.align["类型"] = "c"
    print(table)