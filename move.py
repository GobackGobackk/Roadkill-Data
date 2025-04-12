import os
import shutil

# 主目錄路徑
main_directory = r""  # 替換為你的主目錄路徑

# 遍歷主目錄及其所有子目錄
for root, dirs, files in os.walk(main_directory):
    for file_name in files:
        # 檢查檔案是否為圖片（這裡假設圖片格式為 .jpg 和 .jpeg，您可以根據實際情況添加其他格式）
        if file_name.lower().endswith((".jpg", ".jpeg")):
            old_filepath = os.path.join(root, file_name)
            new_filepath = os.path.join(main_directory, file_name)
            
            # 移動檔案
            shutil.move(old_filepath, new_filepath)
            print(f"檔案 {file_name} 已經從 {root} 移動到 {main_directory}")

print("所有照片已經成功移動到上層目錄。")
