import pandas as pd
import simplekml

def csv_to_kml_grouped(csv_file, kml_file):
    # 讀取 CSV 檔案
    df = pd.read_csv(csv_file, encoding='utf-8')
    
    # 按經緯度和計畫名稱分組，將「原始資料紀錄」合併為一個描述
    grouped = df.groupby(['經度', '緯度', '計畫名稱'])['中名'].apply('\n'.join).reset_index()
    
    # 建立 KML 物件
    kml = simplekml.Kml()
    
    # 遍歷分組後的資料，新增地標
    for _, row in grouped.iterrows():
        # 添加地標
        pnt = kml.newpoint(
            name=row['計畫名稱'],  # 地標名稱
            description=row['中名'],  # 合併的描述
            coords=[(row['經度'], row['緯度'])]  # 經度、緯度
        )
    
    # 儲存為 KML 檔案
    kml.save(kml_file)
    print(f"KML 檔案已生成: {kml_file}")

# 使用範例
csv_file = r''  # 替換為你的 CSV 檔案路徑
kml_file = 'output.kml'  # 替換為輸出的 KML 檔案路徑
csv_to_kml_grouped(csv_file, kml_file)
