import os
import cv2
from datetime import datetime
from core.tool import tool


def tap_position(device, x, y, raw=False):
    t = tool(device, debug=False)
    """
    點擊指定座標位置
    
    參數:
        x: x座標
        y: y座標 
        raw: 是否使用原始座標(預設False)
    """
    t.tap((x, y), raw=raw)
    

    


if __name__ == "__main__":
    # 假設設備名稱為 "emulator-5556"，請根據實際情況修改
    device = "emulator-5556"
    tap_position(device, 90, 120)
    tap_position(device, 160, 120)
    tap_position(device, 230, 120)
    tap_position(device, 300, 120)
    tap_position(device, 370, 120)
    tap_position(device, 428, 120)
    tap_position(device, 506, 120)
    tap_position(device, 574, 120)
    tap_position(device, 642, 120)
    tap_position(device, 708, 120)

