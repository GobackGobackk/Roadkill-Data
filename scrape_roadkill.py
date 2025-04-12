import requests
from bs4 import BeautifulSoup
import pandas as pd

# 基本設定
base_url = "https://roadkill.tw/data/query"  # 請求的基本 URL
headers = {"User-Agent": "Mozilla/5.0"}  # 設置 headers 以模擬瀏覽器行為
params = {
    "row": 0,
    "rowsperpage": 25,
    "ft": "time:2024-01-01~2024-12-31",  # 設定篩選條件（2024 年）
    "page": 0  # 頁碼起始值
}
max_page = 780  # 設定最多爬取的頁數（可根據需求調整）

# 收集資料的容器
data_list = []

# 開始爬取每一頁的資料
for page in range(max_page + 1):
    params["page"] = page  # 更新當前頁碼
    print(f"正在爬取第 {page + 1} 頁...")  # 顯示目前爬取的頁數
    response = requests.get(base_url, params=params, headers=headers)  # 發送 GET 請求

    # 檢查請求是否成功
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")  # 解析網頁 HTML
        rows = soup.find_all("div", class_="tr")  # 找到所有資料列
        
        # 解析每一列資料
        for row in rows:
            # 物種（英文與中文名稱）
            species_div = row.find("div", class_="trow-item-taxonbio")
            species = species_div.find("span", class_="field_content").get_text(separator="|").split("|") if species_div else ["", ""]

            # 日期
            date = row.find("div", class_="trow-item-date").find("span", class_="field_content").text if row.find("div", class_="trow-item-date") else ""
            
            # 地點
            location = row.find("div", class_="trow-item-place").find("span", class_="field_content").text if row.find("div", class_="trow-item-place") else ""
            
            # 紀錄者
            recorded_by = row.find("div", class_="trow-item-recorded_by").find("span", class_="field_content").text if row.find("div", class_="trow-item-recorded_by") else ""
            
            # 最後修改時間
            last_modified = row.find("div", class_="trow-item-changed").find("span", class_="field_content").text if row.find("div", class_="trow-item-changed") else ""
            
            # 識別號
            nid = row.find("div", class_="trow-item-nid").find("span", class_="field_content").text if row.find("div", class_="trow-item-nid") else ""
            
            # 儲存資料到 data_list
            data_list.append({
                "Species (英文名)": species[0].strip(),
                "Species (中文名)": species[1].strip() if len(species) > 1 else "",
                "Date": date,
                "Location": location,
                "Recorded by": recorded_by,
                "Last modified": last_modified,
                "ID": nid.split(" ")[0] if nid else ""
            })
    else:
        print(f"第 {page + 1} 頁請求失敗，狀態碼：{response.status_code}")
        break  # 如果頁面請求失敗，停止抓取

# 儲存資料為 DataFrame 並匯出為 CSV
df = pd.DataFrame(data_list)

# 處理資料中的空值，並填充為空字串
df = df.fillna("")

# 儲存為 CSV 格式，設定編碼為 utf-8-sig 以支援中文
df.to_csv("2024.csv", index=False, encoding="utf-8-sig")
print("資料已匯出為 roadkill_data.csv")
