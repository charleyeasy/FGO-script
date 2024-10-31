from configparser import ConfigParser
import os
from re import escape
from core import decoder
from core.auto import auto, NoAppleException
from core import client
import sys
import tkinter as tk
from tkinter import messagebox
import win32gui
import win32api
import win32con
import win32process
import psutil


def get_cfg(path):
    cfg_path = "{}/UserData/config".format(path)
    file_list = os.listdir(cfg_path)
    cfg_list = []
    for cfg in file_list:
        if ".ini" in cfg:
            cfg_list.append(cfg)
    return cfg_list


def select_cfg(cfg_list):
    print("請選擇設定檔")
    i = 1
    for cfg in cfg_list:
        print("\033[1;34m {0}: {1}\033[0m".format(i, cfg))
        i += 1
    print("\033[1;31m e: 離開\033[0m")
    try:
        inputIndex = input(
            " 請輸入設定檔編號 [0 ~ {0}]: ".format(i-1))
        value = int(inputIndex)
        if value >= i:
            raise Exception("index is to big.")
        return value
    except (KeyboardInterrupt, SystemExit):
        raise Exception("KeyboardInterrupt")
    except Exception as e:
        if "e" == inputIndex or "E" == inputIndex:
            return -1
        else:
            print(
                "\033[1;31m編號錯誤,請確認後輸入\033[0m")
            input("請輸入enter繼續")
            return select_cfg(cfg_list)


def get_cmd_window_position():
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            if ("cmd.exe" in window_text.lower() or 
                "命令提示字元" in window_text or 
                "start" in window_text or
                "ingame_start" in window_text or
                "python" in window_text.lower()):
                hwnds.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)

    if hwnds:
        hwnd = hwnds[0]  # 使用找到的第一個匹配窗口
        rect = win32gui.GetWindowRect(hwnd)
        x, y = rect[0], rect[1]
        print("目標窗口位置:{}".format((x, y)))
        return x, y
    else:
        print("沒有找到目標窗口")
        return None


def show_message_on_cmd_screen(title, message, error=False):
    cmd_pos = get_cmd_window_position()
    root = tk.Tk()
    root.withdraw()
    
    if cmd_pos:
        x, y = cmd_pos
        root.geometry(f"+{x+50}+{y+50}")  # 設置視窗位置，稍微偏移以避免完全覆蓋CMD
    
    root.attributes('-topmost', True)  # 使視窗置頂
    root.update()
    
    if error:
        messagebox.showerror(title, message)
    else:
        messagebox.showinfo(title, message)
    
    root.destroy()



if __name__ == '__main__':
    path = os.path.dirname(os.path.abspath(__file__))
    os.system("{0}/adb/adb.exe kill-server".format(path))
    os.system("{0}/adb/adb.exe start-server".format(path))
    setting = True
    while setting:
        os.system('cls')
        try:
            device = client.get_devices(path)
        except Exception as e:
            print(e.args[0])
            break
        print("\033[1;33m你選擇的設備是: {}\n\033[0m".format(device))
        try:
            cfg_name = get_cfg(path)[int(select_cfg(get_cfg(path)))-1]
        except Exception as e:
            print(e.args[0])
            break
        print("\033[1;33m你選擇的設定檔是: {}\n\033[0m".format(cfg_name))
        setting = False
        ini_path = "{}/UserData/config/{}".format(path, cfg_name)
        cfg = ConfigParser()
        cfg.read(ini_path)
        ver = cfg['version']['version']
        support = cfg['support']['support']
        clothes = cfg['support']['clothes']
        servant_class = cfg['support']['class']
        apple_count = cfg['ap_recover']['count']
        apple = cfg['ap_recover']['apple']
        recover_time = cfg['recover_time']['recover_time']
        battle1_str = cfg['default_skill']['battle1']
        battle2_str = cfg['default_skill']['battle2']
        battle3_str = cfg['default_skill']['battle3']
        crd1_str = cfg['default_card']['battle1']
        crd2_str = cfg['default_card']['battle2']
        crd3_str = cfg['default_card']['battle3']
        codelist = [battle1_str, battle2_str,
                    battle3_str, crd1_str, crd2_str, crd3_str]
        #print(codelist)
        apple_names = {
            'star': '聖晶石',
            'gold': '金蘋果',
            'silver': '銀蘋果',
            'blue': '青蘋果',
            'bronze': '銅蘋果'
        }
        print("蘋果名稱:", apple_names.get(apple, apple))
        # 如果 apple 在 apple_names 中存在，它會返回對應的中文名稱。
        # 如果 apple 不在 apple_names 中，它會返回 apple 本身作為默認值
 
  
    while True:
        run_times = input("請輸入次數")
        while not run_times.isdigit():
            os.system('cls')
            run_times = input("請輸入次數")     
        error_flag = 0
        try:
            round = auto("menu.png", support,clothes,servant_class, int(apple_count), apple, device, int(
                recover_time) * 60, run_time=int(run_times), ver=ver)
            instr = decoder.decode(codelist)
            print("執行次數:", run_times)
            print("指令列表:")
            # 首先計算最大的序號寬度
            max_width = len(str(len(instr)))

            # 然後使用這個寬度來格式化輸出
            for i, instruction in enumerate(instr, 1):
                # 移除開頭的 "round."
                cleaned_instruction = instruction.replace("round.", "", 1)
                print(f"{f'{i}.':<{max_width+1}} {cleaned_instruction}")
                
            round.quick_start(True)
            for runs in range(int(run_times)):
                for i in range(0, len(instr)):
                    exec(instr[i])
        except NoAppleException as e:
            #print("沒有蘋果了!")
            error_flag = 1
            show_message_on_cmd_screen(f"{device}-程序完成", f"沒蘋果了。\n按確定重新開始執行。")
        except KeyboardInterrupt:
            error_flag = 1
            show_message_on_cmd_screen(f"{device}-中斷", f"腳本中斷。\n按確定重新開始執行。")
        except Exception as e:
            error_flag=1
            show_message_on_cmd_screen(f"{device}-錯誤", f"發生錯誤：{str(e)}\n按確定重新開始執行。", error=True)
        finally:
            if error_flag == 0:
                show_message_on_cmd_screen(f"{device}-程序完成", f"程序已完成。\n按確定重新開始執行。")

            #round.stop_device_printing()  # 假設 'round' 是 auto 類的實例
