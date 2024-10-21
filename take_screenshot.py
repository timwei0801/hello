import keyboard
import pyautogui
import time
import os
from datetime import datetime
import threading
import sys

class ScreenshotTaker:
    def __init__(self, folder_path="screenshots"):
        self.folder_path = folder_path
        self.screenshot_count = 0
        self.running = True
        
        # 如果資料夾不存在則創建
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            
        print("截圖程式已啟動！")
        print("按下 'F9' 鍵進行截圖")
        print("按下 'ESC' 鍵退出程式")

    def take_screenshot(self):
        # 進行截圖
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"poker_screenshot_{timestamp}.png"
        screenshot = pyautogui.screenshot()
        
        # 儲存截圖
        file_path = os.path.join(self.folder_path, filename)
        screenshot.save(file_path)
        
        self.screenshot_count += 1
        print(f"第 {self.screenshot_count} 張截圖已儲存: {filename}")

    def run(self):
        # 註冊按鍵處理器
        keyboard.on_press_key('F9', lambda _: self.take_screenshot())
        keyboard.on_press_key('esc', lambda _: self.stop())
        
        # 保持程式運行
        while self.running:
            time.sleep(0.1)  # 降低CPU使用率
            
    def stop(self):
        print("\n正在退出程式...")
        print(f"總共截取了 {self.screenshot_count} 張截圖")
        self.running = False
        sys.exit()

if __name__ == "__main__":
    # 您可以在這裡更改資料夾路徑
    screenshot_taker = ScreenshotTaker("poker_screenshots")
    try:
        screenshot_taker.run()
    except KeyboardInterrupt:
        screenshot_taker.stop()