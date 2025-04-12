import requests
from bs4 import BeautifulSoup
import pandas as pd

# 讀取 CSV 檔案
csv_file = r""  # 請將路徑替換為您的 CSV 檔案位置
data = pd.read_csv(csv_file)

# 根據 ID 欄位生成 URL 清單
base_url = "https://roadkill.tw/occurrence/"
data['URL'] = base_url + data['ID'].astype(str)

# 定義資料提取函數
def extract_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # 檢查請求是否成功
        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取地點、死因和類群
        location = soup.find(string="地點").find_next().text.strip() if soup.find(string="地點") else "N/A"
        cause_of_death = soup.find(string="死因").find_next().text.strip() if soup.find(string="死因") else "N/A"
        group = soup.find(string="類群").find_next().text.strip() if soup.find(string="類群") else "N/A"

        return {
            "地點": location,
            "死因": cause_of_death,
            "類群": group
        }
    except Exception as e:
        print(f"爬取 {url} 時發生錯誤: {e}")
        return {
            "地點": "N/A",
            "死因": "N/A",
            "類群": "N/A"
        }

# 爬取每個 URL 並儲存結果
results = []
for idx, row in data.iterrows():
    print(f"正在爬取 {row['URL']} ...")
    result = extract_data(row['URL'])
    result.update(row.to_dict())  # 將原始資料與爬取結果結合
    results.append(result)

# 將結果轉換為 DataFrame
final_df = pd.DataFrame(results)

# 匯出至 Excel
output_file = r""  # 請替換為所需輸出路徑
final_df.to_excel(output_file, index=False)

print(f"資料已匯出至 {output_file}")
