import pandas as pd
from flask import Flask, request, render_template_string
import os
import exifread
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2

app = Flask(__name__)

# Haversine 公式計算經緯度間的距離
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # 地球半徑（公里）
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def interpolate_gps_to_mileage(photo_data, mileage_data):
    results = []
    for photo in photo_data:
        photo_lat, photo_lon = photo['Latitude'], photo['Longitude']
        if photo_lat is None or photo_lon is None:
            photo['Mileage'] = "N/A"
            results.append(photo)
            continue

        min_distance = float('inf')
        closest_point = None

        for i in range(len(mileage_data) - 1):
            curr = mileage_data.iloc[i]
            next_ = mileage_data.iloc[i + 1]

            dist_curr = haversine(photo_lat, photo_lon, curr['Latitude'], curr['Longitude'])
            dist_next = haversine(photo_lat, photo_lon, next_['Latitude'], next_['Longitude'])

            # 增加偵錯訊息
            print(f"照片座標: ({photo_lat}, {photo_lon}), 當前里程點: ({curr['Latitude']}, {curr['Longitude']}), 下一里程點: ({next_['Latitude']}, {next_['Longitude']}), 距離: {dist_curr}, {dist_next}")

            if dist_curr < min_distance:
                min_distance = dist_curr
                closest_point = curr

            if dist_next < min_distance:
                min_distance = dist_next
                closest_point = next_

            if dist_curr + dist_next <= haversine(curr['Latitude'], curr['Longitude'], next_['Latitude'], next_['Longitude']) + 0.05:
                dist_total = haversine(curr['Latitude'], curr['Longitude'], next_['Latitude'], next_['Longitude'])
                dist_to_curr = haversine(photo_lat, photo_lon, curr['Latitude'], curr['Longitude'])
                ratio = dist_to_curr / dist_total
                base_km = float(curr['Name'].replace("K+", "."))
                next_km = float(next_['Name'].replace("K+", "."))
                interpolated_km = base_km + (next_km - base_km) * ratio
                photo['Mileage'] = round(interpolated_km, 3)
                results.append(photo)
                break
        else:
            if closest_point is not None:
                base_km = float(closest_point['Name'].replace("K+", "."))
                photo['Mileage'] = round(base_km, 3)
            else:
                photo['Mileage'] = "N/A"

            results.append(photo)

    return results



# 提取 GPS 資訊
def get_gps_info(exif_data):
    gps_info = {}
    gps_tags = ["GPS GPSLatitude", "GPS GPSLatitudeRef", "GPS GPSLongitude", "GPS GPSLongitudeRef"]

    if all(tag in exif_data for tag in gps_tags):
        lat_ref = exif_data["GPS GPSLatitudeRef"].values
        lat = exif_data["GPS GPSLatitude"].values
        lon_ref = exif_data["GPS GPSLongitudeRef"].values
        lon = exif_data["GPS GPSLongitude"].values

        lat_decimal = (lat[0].num / lat[0].den) + (lat[1].num / lat[1].den / 60) + (lat[2].num / lat[2].den / 3600)
        lon_decimal = (lon[0].num / lon[0].den) + (lon[1].num / lon[1].den / 60) + (lon[2].num / lon[2].den / 3600)

        if lat_ref != "N":
            lat_decimal = -lat_decimal
        if lon_ref != "E":
            lon_decimal = -lon_decimal

        gps_info["Latitude"] = lat_decimal
        gps_info["Longitude"] = lon_decimal

    return gps_info

# 提取日期時間資訊
def get_photo_date_time(exif_data):
    date_time_tag = "EXIF DateTimeOriginal"
    if date_time_tag in exif_data:
        date_time_str = exif_data[date_time_tag].values
        try:
            date_time_obj = datetime.strptime(date_time_str, "%Y:%m:%d %H:%M:%S")
            return {
                "Date": date_time_obj.strftime("%Y-%m-%d"),
                "Time": date_time_obj.strftime("%H:%M:%S"),
                "Year": date_time_obj.year,
                "Month": date_time_obj.month,
                "Day": date_time_obj.day,
            }
        except ValueError:
            return None
    return None

# 批次處理 GPS 資料
def batch_extract_gps(folder_paths):
    result = []
    for folder_path in folder_paths:
        for root, _, files in os.walk(folder_path):
            for file_name in files:
                if file_name.lower().endswith((".jpg", ".jpeg")):
                    file_path = os.path.join(root, file_name)
                    with open(file_path, "rb") as image_file:
                        tags = exifread.process_file(image_file)
                        gps_info = get_gps_info(tags)
                        date_time_info = get_photo_date_time(tags)

                        record = {
                            "File": file_name,
                            "Latitude": gps_info.get("Latitude") if gps_info else None,
                            "Longitude": gps_info.get("Longitude") if gps_info else None,
                            "Date": date_time_info.get("Date") if date_time_info else None,
                            "Time": date_time_info.get("Time") if date_time_info else None,
                            "Path": file_path
                        }
                        result.append(record)
    return result

# 主頁面與結果顯示模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>GPS 資料提取</title>
</head>
<body>
    <h1>GPS 資料提取工具</h1>
    <form method="post">
        <label for="folder_paths">請輸入資料夾路徑（多個路徑請以分號分隔）：</label><br>
        <input type="text" id="folder_paths" name="folder_paths" required style="width: 50%;"><br><br>
        <button type="submit">提交</button>
    </form>

    {% if results %}
    <h2>提取結果</h2>
    <button onclick="copyTable()">複製表格</button>
    <button onclick="clearTable()">清除表格</button>
    <table border="1" cellspacing="0" cellpadding="5" id="results_table">
        <tr>
            <th>File</th>
            <th>Latitude</th>
            <th>Longitude</th>
            <th>Date</th>
            <th>Time</th>
            <th>Mileage</th>
            <th>Path</th>
        </tr>
        {% for record in results %}
        <tr>
            <td>{{ record.File }}</td>
            <td>{{ record.Latitude }}</td>
            <td>{{ record.Longitude }}</td>
            <td>{{ record.Date }}</td>
            <td>{{ record.Time }}</td>
            <td>{{ record.Mileage }}</td>
            <td>{{ record.Path }}</td>
        </tr>
        {% endfor %}
    </table>
    {% endif %}

    <script>
        function copyTable() {
            var range = document.createRange();
            range.selectNode(document.getElementById("results_table"));
            window.getSelection().removeAllRanges();
            window.getSelection().addRange(range);
            document.execCommand("copy");
            alert("表格已複製到剪貼簿");
        }

        function clearTable() {
            var table = document.getElementById("results_table");
            while(table.rows.length > 1) {
                table.deleteRow(1);
            }
            alert("表格已清除");
        }
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    mileage_data = pd.read_csv(r"")  # 讀取里程檔案
    if request.method == 'POST':
        folder_paths = request.form.get('folder_paths', '').split(';')  # 取得多個資料夾路徑
        folder_paths = [path.strip() for path in folder_paths]  # 去除路徑兩側的空白
        if all(os.path.exists(path) for path in folder_paths):
            photo_data = batch_extract_gps(folder_paths)
            results = interpolate_gps_to_mileage(photo_data, mileage_data)
    return render_template_string(HTML_TEMPLATE, results=results)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
