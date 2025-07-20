import requests
import os

def download_video(url, folder_path='./', video_ID=0):
    global video_counter
    response = requests.get(url, stream=True)  # 使用requests獲取影片內容
    if response.status_code == 200:  # 確認請求成功
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        filename = f'{video_ID}.mp4'
        print('filename-->', filename)
        file_path = os.path.join(folder_path, filename)
        # 開啟一個文件以寫入二進制數據
        with open(file_path, 'wb') as f:
            # 寫入獲取到的影片內容
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:  # 過濾掉保持連接的chunk
                    f.write(chunk)
        print(f"影片已保存到 {file_path}")
        video_counter = video_counter + 1
    else:
        print("影片下載失敗")

