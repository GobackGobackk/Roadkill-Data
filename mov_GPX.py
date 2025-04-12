import os
from subprocess import run, PIPE

def extract_video_time_with_ffprobe(file_path):
    """使用 ffprobe 提取影片的創建時間"""
    try:
        result = run(
            ["ffprobe", "-v", "error", "-show_entries", "format_tags=creation_time",
             "-of", "default=noprint_wrappers=1:nokey=1", file_path],
            stdout=PIPE, stderr=PIPE, text=True
        )
        creation_time = result.stdout.strip()
        return creation_time if creation_time else None
    except Exception as e:
        print(f"Error extracting video time from {file_path}: {e}")
        return None

# 使用範例
video_folder = r""  # 修改為你的影片資料夾路徑

for root, _, files in os.walk(video_folder):
    for file_name in files:
        if file_name.lower().endswith((".mp4", ".mov", ".avi")):
            file_path = os.path.join(root, file_name)
            video_time = extract_video_time_with_ffprobe(file_path)
            if video_time:
                print(f"影片檔案: {file_name}，拍攝時間: {video_time}")
            else:
                print(f"影片檔案: {file_name}，無法提取拍攝時間")
