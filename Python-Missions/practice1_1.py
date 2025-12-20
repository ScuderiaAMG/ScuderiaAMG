import requests
from bs4 import BeautifulSoup
import time
import random

def scrape_ranking(url):

  headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'
  }
  
  try:
    response = requests.get(url, headers=headers)
    response.raise_for_status() 
    response.encoding = response.apparent_encoding 
  except requests.exceptions.RequestException as e:
    print(f"请求失败: {e}")
    return []

  soup = BeautifulSoup(response.text, 'html.parser')
  
  table = soup.find('table')
  if not table:
    print("未找到对应数据")
    return []

  universities = []
  rows = table.find_all('tr')
  for row in rows[1:]:
    cells = row.find_all(['td']) 
    if len(cells) >= 6: 
      try:
        rank = cells[0].get_text(strip=True)
        name_info = cells[1].get_text(strip=True)
        name = name_info.split('\n')[0] if '\n' in name_info else name_info
        location = cells[2].get_text(strip=True)
        type = cells[3].get_text(strip=True)
        score = cells[4].get_text(strip=True)
        
        university = {
          'rank': rank,
          'name': name,
          'location': location,
          'type': type,
          'score': score
        }
        universities.append(university)
        time.sleep(random.uniform(0.5, 1.5))
        
      except IndexError:
        print(f"索引错误! {row}")
        continue
  return universities

if __name__ == "__main__":
  url = "https://www.shanghairanking.cn/rankings/bcur/2025"
  ranking_data = scrape_ranking(url)

  if ranking_data:
    for uni in ranking_data[:100]: 
      print(f"排名: {uni['rank']}, 学校名称: {uni['name']}, 省市: {uni['location']}, 类型: {uni['type']}, 总分: {uni['score']}")
    
  else:
    print("查找数据失败")