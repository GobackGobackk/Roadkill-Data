import os
import pandas as pd

# 模擬資料夾結構
root_path = r""  # 替換成你的主資料夾路徑
output_file = r""  # 輸出 Excel 檔案路徑

# 儲存提取的資料
data = []

# 遍歷資料夾結構
for folder_name in os.listdir(root_path):
    # 過濾掉非資料夾
    folder_path = os.path.join(root_path, folder_name)
    if not os.path.isdir(folder_path):
        continue

    # 提取里程數 (假設格式為 XXXK，移除 K)
    try:
        mileage = folder_name.split("_")[-1]  # 提取最後一部分
        mileage = mileage.replace("K", "")  # 移除 K
    except IndexError:
        mileage = "未知"

    # 遍歷子資料夾提取物種名稱
    for species_name in os.listdir(folder_path):
        species_path = os.path.join(folder_path, species_name)
        if os.path.isdir(species_path):
            # 添加資料到清單
            data.append({"里程": mileage, "物種名稱": species_name})

# 將資料轉為 DataFrame 並輸出到 Excel
df = pd.DataFrame(data)
df.to_excel(output_file, index=False)
print(f"資料已成功輸出到 {output_file}")
