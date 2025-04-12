import os
import pandas as pd

# 讀取CSV檔案
csv_file = r""
df = pd.read_csv(csv_file)

# 設定檔案的主目錄
main_directory = r""  # 替換為你的主目錄路徑

# 將里程欄位轉換為字符串並加上 "K"（例如 15.355 變成 15.355K）
df['Mileage'] = df['Mileage'].apply(lambda x: f"{x:.3f}K")

# 遍歷主目錄及其所有子目錄
for root, dirs, files in os.walk(main_directory):
    for index, row in df.iterrows():
        old_filename = row['File']  # 原始檔名
        species = row['物種']  # 物種名稱
        mileage = row['Mileage']  # 里程
        old_filepath = os.path.join(root, old_filename)
        
        # 檢查檔案是否存在
        if os.path.exists(old_filepath):
            # 新檔名格式: DSC_2903_物種_里程K
            new_filename = f"{old_filename.split('.')[0]}_{species}_{mileage}.{old_filename.split('.')[-1]}"
            new_filepath = os.path.join(root, new_filename)
            
            # 重新命名檔案
            os.rename(old_filepath, new_filepath)
            print(f"檔案 {old_filename} 已經重新命名為 {new_filename}")
        else:
            print(f"檔案 {old_filename} 不存在於路徑 {root}，無法重新命名。")
