import os
import cv2
from datetime import datetime
from core.tool import tool

def capture_and_save_screenshot(device):
    # 初始化 tool 類
    t = tool(device, debug=True)
    
    # 獲取截圖
    screenshot = t.adbkit.screenshots()
    
    # 創建保存目錄
    folder = "screenshots"
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.png"
    filepath = os.path.join(folder, filename)
    
    # 保存截圖
    cv2.imwrite(filepath, screenshot)
    print(f"截圖已保存: {filepath}")
    


if __name__ == "__main__":
    # 假設設備名稱為 "emulator-5556"，請根據實際情況修改
    device = "emulator-5556"
    capture_and_save_screenshot(device)
