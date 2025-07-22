from pynput import keyboard
import time

# 控制變數
is_typing = False
controller = keyboard.Controller()

def press_shift_enter():
    """模擬按下 shift + Enter"""
    controller.press(keyboard.Key.shift_r)  # 按下 shift 鍵
    controller.press(keyboard.Key.enter)  # 按下 Enter 鍵
    controller.release(keyboard.Key.enter)  # 放開 Enter 鍵
    controller.release(keyboard.Key.shift_r)  # 放開 shift 鍵
    time.sleep(0.05)

def press_enter():
    """模擬按下 Enter"""
    controller.press(keyboard.Key.enter)  # 按下 Enter 鍵
    controller.release(keyboard.Key.enter)  # 放開 Enter 鍵
    time.sleep(0.05)

def type_text(text_to_type):
    """自動輸入文本"""
    global is_typing
    is_typing = True
    press_shift_enter()
    for char in text_to_type:
        if char == ' ':  # 如果字符是空白鍵
            controller.press(keyboard.Key.space)  # 按下空白鍵
            controller.release(keyboard.Key.space)  # 放開空白鍵
        else:
            controller.type(char)  # 輸入字符
        time.sleep(0.05)  # 等待一段時間以模擬打字速度
    press_enter()
    is_typing = False  # 在輸入結束後將 is_typing 設置為 False

def type_text_START(text_to_type):
    """自動輸入文本"""
    global is_typing
    is_typing = True
    for char in text_to_type:
        if char == ' ':  # 如果字符是空白鍵
            controller.press(keyboard.Key.space)  # 按下空白鍵
            controller.release(keyboard.Key.space)  # 放開空白鍵
        else:
            controller.type(char)  # 輸入字符
        time.sleep(0.05)  # 等待一段時間以模擬打字速度
    press_enter()
    is_typing = False  # 在輸入結束後將 is_typing 設置為 False

def start_typing():
    global is_typing
    is_typing = True
    currently_pressed.clear()  # 清空 currently_pressed 集合
    print("開始自動輸入...")
    press_enter()
    #type_text("他媽的為什麼不給狗幹一幹")  
    #type_text("吃屎長大的垃圾")  
    #type_text("你媽養你不如養狗")  
    #type_text("可悲底層操機掰")  
    #type_text("自動打字測試1")
    #type_text("自動打字測試2")
    #type_text("自動打字測試3")
    #type_text("自動打字測試4")

    type_text("我就想請問")
    type_text("您們到底在")
    type_text("裝什麼")
    type_text("是台北市垃圾袋嗎")
    type_text("這麼會裝")
    type_text("拿這麼多頭")
    type_text("還不是得輸")
    type_text("真的超爛")
    type_text("拜託")
    type_text("趕緊刪遊戲")
    '''
    type_text("沒錯")
    type_text("只有你")
    type_text("你是智慧的結晶")
    type_text("你是文明的瑰寶")
    type_text("你是人類的獨苗")
    type_text("你是上帝的遺珠")
    type_text("你是最後的希望")
    type_text("你是電")
    type_text("你是光")
    type_text("你是唯一的神話")
    type_text("總而言之")
    type_text("言而總之")
    type_text("你們真的是")
    type_text("有夠爛的")
    '''
    is_typing = False
currently_pressed = set()

def on_press(key):
    # 將按下的鍵添加到當前按下的集合中
    currently_pressed.add(key)
    print(f'按下：{key}')  # 打印按下的鍵

    # 檢查是否按下 Ctrl 鍵和 F1 鍵
    if keyboard.Key.f1 in currently_pressed and (keyboard.Key.ctrl_l in currently_pressed or keyboard.Key.ctrl_r in currently_pressed):
        if not is_typing:
            start_typing()  # 開始自動輸入文本

def on_release(key):
    # 當釋放鍵時，從當前按下的集合中移除
    try:
        currently_pressed.remove(key)
    except KeyError:
        pass  # 如果鍵不在集合中，則忽略



# 開始監聽鍵盤事件
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    print("按下 Ctrl + F1 開始自動輸入，按下 Esc 鍵退出")
    listener.join()