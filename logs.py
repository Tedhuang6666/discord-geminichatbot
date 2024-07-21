from datetime import datetime
import os

def datewrite(content):
    # 取得當前日期
    current_date = datetime.today().strftime("%Y-%m-%d")
    log_dir = 'log'
    log_file_path = os.path.join(log_dir, f'{current_date}.txt')  
    
    # 檢查是否需要創建新的日誌文件
    if not os.path.exists(log_file_path):
        os.makedirs(log_dir, exist_ok=True)  # 確保log目錄存在
    
    # 取得當前時間
    current_time = datetime.today().strftime("%Y/%m/%d %H:%M:%S")
    
    # 將內容和時間寫入日誌文件
    with open(log_file_path, 'a', encoding='utf-8') as file:
        file.write(f"{current_time} {content}\n")
