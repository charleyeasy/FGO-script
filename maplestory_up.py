from pynput.keyboard import Key, Listener, Controller
import time
from threading import Thread

# 設定按鍵
key_left = Key.left
key_right = Key.right
key_up = Key.up
key_down = Key.down
key_alt = Key.alt_l

# 控制變數
is_up_pressed = False
is_left_pressed = False
is_right_pressed = False
is_alt_pressed = False

def press_keys():
    while True:
        if is_up_pressed and is_alt_pressed:
            if not (is_left_pressed or is_right_pressed):
                # 按下左鍵
                Controller().press(key_left)
                Controller().release(key_left)
                time.sleep(0.01)  # 等待一段時間
                # 按下右鍵
                Controller().press(key_right)
                Controller().release(key_right)
                time.sleep(0.01)  # 等待一段時間


def on_press(key):
    global is_up_pressed, is_left_pressed, is_right_pressed, is_alt_pressed
    #print(f'{key} pressed')
    if key == key_up:
        is_up_pressed = True
    elif key == key_left:
        is_left_pressed = True
    elif key == key_right:
        is_right_pressed = True
    elif key == key_alt:
        is_alt_pressed = True

def on_release(key):
    global is_up_pressed, is_left_pressed, is_right_pressed, is_alt_pressed
    #print(f'{key} released')
    if key == key_up:
        is_up_pressed = False
    elif key == key_left:
        is_left_pressed = False
    elif key == key_right:
        is_right_pressed = False
    elif key == key_alt:
        is_alt_pressed = False


# 開始按鍵執行緒
controller = Controller()
Thread(target=press_keys, daemon=True).start()
print("開始執行")
# 開始監聽鍵盤事件
with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()