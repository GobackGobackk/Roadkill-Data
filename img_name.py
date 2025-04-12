import os
import pandas as pd
import re

def parse_file_name(file_name):
    match = re.match(r"^([a-zA-Z0-9_]+)_([\u4e00-\u9fa5]+)_(\d+\.\d+K)", file_name)
    if match:
        return {
            "File Code": match.group(1),
            "Species Name": match.group(2),
            "Mileage": match.group(3)
        }
    return None

def extract_file_data(folder_path):
    result = []
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                parsed_data = parse_file_name(file_name)
                if parsed_data:
                    result.append(parsed_data)
    return result

def save_to_excel(data, output_path):
    df = pd.DataFrame(data)
    df.to_excel(output_path, index=False)

# 指定資料夾路徑
folder_path = r""
# 指定輸出 Excel 路徑
output_path = "output.xlsx"

data = extract_file_data(folder_path)
save_to_excel(data, output_path)

print(f"已成功將結果儲存到 {output_path}")
