import os
import subprocess
import numpy as np
import cv2
import time
import pytesseract
from collections import Counter
from datetime import datetime

class adbKit():
    def __init__(self, device, debug=False) -> None:
        self.path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.debug = debug
        self.capmuti = 1
        self.device = device
        self.breakline = self.get_SDK()

    def debug_get_write(self):
        t1 = time.time()
        pipe = subprocess.Popen("{0}/adb/adb.exe -s {1} shell screencap -p".format(self.path, self.device),
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        image_bytes = pipe.stdout.read()
        print(image_bytes[0:10])
        image_bytes = image_bytes.replace(b'\r\n', b'\n')
        print(image_bytes[0:10])
        t2 = time.time()
        image = cv2.imdecode(np.frombuffer(
            image_bytes, dtype='uint8'), cv2.IMREAD_COLOR)
        print("耗時 {0} 秒".format(round(t2-t1, 2)))
        cv2.imwrite("screenshot.png", image)
        raw = input("按Enter鍵關閉視窗")

    def get_SDK(self):
        SDK_version = subprocess.Popen("{0}/adb/adb.exe -s {1} shell getprop ro.build.version.release".format(
            self.path, self.device), stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        SDK_version = SDK_version.stdout.read().decode("utf-8")
        if int(SDK_version[0]) >= 7:
            return '\r\n'
        elif int(SDK_version[0]) <= 5:
            return '\r\r\n'
        else:
            print("不是android5或android7")

    def screenshots(self, raw=False):
        pipe = subprocess.Popen("{0}/adb/adb.exe -s {1} shell screencap -p".format(self.path, self.device),
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        image_bytes = pipe.stdout.read()
        image_bytes = image_bytes.replace('{0}'.format(
            self.breakline).encode(encoding="utf-8"), b'\n')
        image = cv2.imdecode(np.frombuffer(
            image_bytes, dtype='uint8'), cv2.IMREAD_COLOR)
        if image.shape[0] != 720 and image.shape[1] != 1280 and not raw:
            image = self.reimage(image)
        return image

    def reimage(self, images):
        images = cv2.resize(images, (1280, 720))
        return images

    def click(self, pointx, pointy, raw=False):
        if raw:
            Px = str(pointx)
            Py = str(pointy)
        else:
            Px = str(int(pointx)*self.capmuti)
            Py = str(int(pointy)*self.capmuti)
        if self.debug:
            print('[ADB]adb shell input tap ' + Px + ' ' + Py)
        os.system(
            '{0}/adb/adb.exe -s {1} shell input tap {2} {3}'.format(self.path, self.device, Px, Py))

    def swipe(self, x1, y1, x2, y2, delay):
        cmdSwipe = '{0}/adb/adb.exe -s {1} shell input swipe {2} {3} {4} {5} {6}'.format(
            self.path, self.device, int(x1), int(y1), int(x2), int(y2), int(delay*1000))
        if self.debug:
            print('[ADB]adb shell swipe from X:{0} Y:{1} to X:{2} Y:{3} Delay:{4}'.format(
                int(x1), int(y1), int(x2), int(y2), int(delay*1000)))
        os.system(cmdSwipe)


class tool():
    def __init__(self, device, debug=False) -> None:
        self.device_name = device
        self.debug = debug
        self.adbkit = adbKit(device)
        self.adbkit.capmuti = self.get_width_muti()
        self.screenshot = None
        self.templates = [cv2.imread(self.adbkit.path + f'/number_templates/{i}.png', 0) for i in range(10)]
        #print(self.templates)
    def get_width_muti(self):
        sample = self.adbkit.screenshots(raw=True)
        return sample.shape[0] / 720

    def recognize_hp_junk(self, image, attempts=1):
        results = []
        image_digit = 12  # 每個數字的寬度
        comma_offset = 4  # 逗號的估計寬度，根據實際情況調整       
        for _ in range(attempts):
            #print(image.shape[1])
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            recognized_number = ''
            x = gray.shape[1] - image_digit  # 從最右邊開始
            digit_count = 0
            while x >= 0:
                roi = gray[:, x:x+image_digit]
                best_match = -1
                best_score = -1
                cv2.imshow('ROI', roi)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
                for i, template in enumerate(self.templates):
                    if roi.shape != template.shape:
                        template = cv2.resize(template, (roi.shape[1], roi.shape[0]))
                    
                    res = cv2.matchTemplate(roi, template, cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, _ = cv2.minMaxLoc(res)
                    print(i,max_val)
                    if max_val > best_score:
                        best_score = max_val
                        best_match = i

                if best_score > 0.7:  # 閾值可調整
                    recognized_number = str(best_match) + recognized_number
                    digit_count += 1
                    
                    # 每三位數字後添加偏移
                    if digit_count % 3 == 0:
                        x -= comma_offset
                else:
                    if recognized_number:
                        break

                x -= image_digit
            if recognized_number:
                results.append(recognized_number)
        
            return max(results, key=results.count) if results else "0"


    def preprocess_color_filter(self, image, lower_color, upper_color):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_color, upper_color)
        result = cv2.bitwise_and(image, image, mask=mask)
        gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        return result
    

    def increase_contrast(self,image):
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl,a,b))
        return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    def recognize_hp(self, image):

        # 放大圖片
        scale_factor = 10
        enlarged = cv2.resize(image, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
        enlarged = self.increase_contrast(enlarged)
        # 顏色過濾
        processed_image = self.preprocess_color_filter(enlarged, np.array([0, 0, 0]), np.array([255, 30, 255]))

        kernel = np.ones((2,2),np.uint8)
        processed_image = cv2.morphologyEx(processed_image, cv2.MORPH_OPEN, kernel)

        #timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        #cv2.imwrite(self.adbkit.path + f"/processed_image/processed_enemy_{timestamp}.png", processed_image)
        '''
        cv2.imshow('processed_image',processed_image)
        cv2.waitKey(0)  
        cv2.destroyAllWindows()
        '''
        
        # OCR 識別
        config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789'
        hp = pytesseract.image_to_string(processed_image, config=config)
        hp = ''.join(filter(str.isdigit, hp))

        return hp if hp else "0"
    
    def check_enemy(self):
        """
        def recognize_hp(image, attempts=5):
            results = []
            for _ in range(attempts):

                # OCR
                config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
                hp = pytesseract.image_to_string(image, config=config)
                hp = ''.join(filter(str.isdigit, hp))
                if hp:
                    results.append(hp)
            
            # 返回最常見的結果，如果沒有結果則返回空字符串
            return Counter(results).most_common(1)[0][0] if results else ""
        """
        # 數字識別部分
        time.sleep(1)

        self.screenshot_temp = self.adbkit.screenshots()
        
        enemy1 = self.screenshot_temp[40:62,110:220]
        enemy2 = self.screenshot_temp[40:62,360:470]
        enemy3 = self.screenshot_temp[40:62,610:720]
        # 顯示敵人血量圖像
        """
        cv2.imshow('Enemy 1 HP', enemy1)
        cv2.imshow('Enemy 2 HP', enemy2)
        cv2.imshow('Enemy 3 HP', enemy3)
        cv2.waitKey(0)  
        cv2.destroyAllWindows()"""
        # 多次辨識
        enemy_hps = [self.recognize_hp(enemy) for enemy in [enemy1, enemy2, enemy3]]
        # 轉換血量為整數，如果轉換失敗則設為0
        enemy_hps = [int(hp) if hp.isdigit() else 0 for hp in enemy_hps]

        # 計算敵人數量（血量不為0的敵人）
        enemy_count = sum(1 for hp in enemy_hps if hp > 0)

        # 找出血量最高的敵人位置
        max_hp_position = enemy_hps.index(max(enemy_hps)) + 1 if any(enemy_hps) else 0
        #print("\033[1;38;5;213m目前設備: {}\033[0m".format(self.device_name))
        # 使用亮青色輸出所有信息
        bright_cyan = '\033[1;38;5;219m'
        reset = '\033[0m'
        # 設置固定寬度
        # 設置固定寬度
        width = 22

        def get_string_width(s):
            # 計算字符串的顯示寬度
            return sum(2 if ord(c) > 127 else 1 for c in s)

        def create_line(text):
            # 計算文本的實際顯示寬度
            text_width = get_string_width(text)
            # 計算所需的填充
            padding = ' ' * (width - text_width - 4)  # 4 是為了 '| ' 和 ' |'
            return f"{bright_cyan}| {text}{padding} |{reset}"

        # 創建框和內容
        border = f"{bright_cyan}+{'-' * (width - 2)}+{reset}"
        content = []

        for i, hp in enumerate(enemy_hps, 1):
            if hp > 0:
                content.append(create_line(f"敵人{i}血量: {hp}"))
            else:
                content.append(create_line(f"敵人{i}血量: 無"))

        content.append(create_line(f"敵人數量: {enemy_count}"))
        content.append(create_line(f"最大血量位置: {max_hp_position}"))

        # 輸出框和內容
        print(border)
        for line in content:
            print(line)
        print(border)

        return (enemy_count, max_hp_position)

        """self.screenshot_temp = self.adbkit.screenshots()
        
        enemy1 = self.screenshot_temp[45:56,110:218]
        enemy2 = self.screenshot_temp[45:56,360:468]
        enemy3 = self.screenshot_temp[45:56,610:718]

        enemy_hps = [self.recognize_hp(enemy) for enemy in [enemy1, enemy2, enemy3]]

        # 轉換血量為整數，如果轉換失敗則設為0
        enemy_hps = [int(hp) if hp.isdigit() else 0 for hp in enemy_hps]

        # 計算敵人數量（血量不為0的敵人）
        enemy_count = sum(1 for hp in enemy_hps if hp > 0)

        # 找出血量最高的敵人位置
        max_hp_position = enemy_hps.index(max(enemy_hps)) + 1 if any(enemy_hps) else 0

        for i, hp in enumerate(enemy_hps, 1):
            print(f"敵人{i}血量: {hp}")

        print(f"敵人數量: {enemy_count}")
        print(f"最大血量的敵人位置: {max_hp_position}")

        return (enemy_count, max_hp_position)"""
    def find_support(self,support_list,clothes, acc=0.85):

        support_imgs = []
        self.screenshot = self.adbkit.screenshots()
        cv2.rectangle(self.screenshot, (240, 0), (1280, 720),
                        color=(0, 0, 0), thickness=-1)

        for item in support_list:
            support_imgs.append(cv2.imread(item))

        all_matched_support_positions = set()
        
        threshold = 10  # 設定閾值，若座標差異小於此值則視為同一位置
        for index, img in enumerate(support_imgs):
            find_height, find_width = img.shape[:2:]
            result = cv2.matchTemplate(
                self.screenshot, img, cv2.TM_CCOEFF_NORMED)
            # 获取所有匹配结果
            locations = np.where(result >= acc)
            
            
            # 將當前圖片的所有匹配位置加入總集合
            for y, x in zip(locations[0], locations[1]):
                # 檢查是否有相近的位置已存在
                is_duplicate = False
                positions_to_remove = set()
                
                for existing_x, existing_y in all_matched_support_positions:
                    if (abs(x - existing_x) < threshold and 
                        abs(y - existing_y) < threshold):
                        # 找到相近位置，使用平均值
                        new_x = (x + existing_x) // 2
                        new_y = (y + existing_y) // 2
                        positions_to_remove.add((existing_x, existing_y))
                        x, y = new_x, new_y
                        is_duplicate = True
                
                # 移除舊的位置並添加新的平均位置
                for pos in positions_to_remove:
                    all_matched_support_positions.remove(pos)
                all_matched_support_positions.add((x, y))
            
            # 最終 all_matched_positions 包含了所有唯一的匹配位置
            # 如果需要轉換為列表

        # 使用亮青色輸出所有匹配位置
        bright_cyan = '\033[1;38;5;219m'
        reset = '\033[0m'
        '''
            # 計算最長行的長度
        title = "[Support]  All Matched Positions:"
        max_length = max(len(title), max(len(f"Position: {pos}") for pos in all_matched_support_positions) if all_matched_support_positions else 0)
        
        # 創建框和輸出內容
        border = f"{bright_cyan}+{'-' * (max_length + 4)}+{reset}"
        
        # 輸出框和內容
        print(border)
        print(f"{bright_cyan}| {title:<{max_length}} |{reset}")
        print(border)
        for pos in all_matched_support_positions:
            print(f"{bright_cyan}| Position: {str(pos):<{max_length-10}} |{reset}")
        print(border)
        '''
        unique_support_positions = list(all_matched_support_positions)
        # 如果 clothes[0] 是 "all"，直接返回 unique_support_positions
        if clothes[0] == "all":
            for sup_pos in unique_support_positions:
                print(f"{bright_cyan}助戰好友位置: {sup_pos}{reset}")
                sup_pos = [x*self.adbkit.capmuti for x in sup_pos]
                return sup_pos, find_height * self.adbkit.capmuti, find_width * self.adbkit.capmuti  # 返回符合條件的support位置
        else:
            # 處理禮裝圖片比對
            clothes_img = cv2.imread(clothes[0])

            all_matched_clothes_positions = set()
            
            result = cv2.matchTemplate(
                self.screenshot, clothes_img, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= 0.95)
            
            for y, x in zip(locations[0], locations[1]):
                # 檢查是否有相近的位置已存在
                is_duplicate = False
                positions_to_remove = set()
                
                for existing_x, existing_y in all_matched_clothes_positions:
                    if (abs(x - existing_x) < threshold and 
                        abs(y - existing_y) < threshold):
                        # 找到相近位置，使用平均值
                        new_x = (x + existing_x) // 2
                        new_y = (y + existing_y) // 2
                        positions_to_remove.add((existing_x, existing_y))
                        x, y = new_x, new_y
                        is_duplicate = True
                
                # 移除舊的位置並添加新的平均位置
                for pos in positions_to_remove:
                    all_matched_clothes_positions.remove(pos)
                all_matched_clothes_positions.add((x, y))
            '''
            title = "[Clothes]  All Matched Positions:"
            max_length = max(len(title), max(len(f"Position: {pos}") for pos in all_matched_clothes_positions) if all_matched_clothes_positions else 0)
            
            border = f"{bright_cyan}+{'-' * (max_length + 4)}+{reset}"
            
            print(border)
            print(f"{bright_cyan}| {title:<{max_length}} |{reset}")
            print(border)
            for pos in all_matched_clothes_positions:
                print(f"{bright_cyan}| Position: {str(pos):<{max_length-10}} |{reset}")
            print(border)
            '''
            unique_clothes_positions = list(all_matched_clothes_positions)
            
            # 比對support和clothes的位置關係
            threshold_y = 110  # y軸容許的最大差距

            for sup_pos in unique_support_positions:
                for clothes_pos in unique_clothes_positions:
                    y_diff = clothes_pos[1] - sup_pos[1]  # clothes應在support下方
                    if 0 < y_diff < threshold_y:  # y差距在容許範圍內且clothes在下方
                        print(f"{bright_cyan}助戰好友位置: {sup_pos}{reset}")
                        sup_pos = [x*self.adbkit.capmuti for x in sup_pos]
                        return sup_pos, find_height*self.adbkit.capmuti, find_width*self.adbkit.capmuti # 返回符合條件的support位置
        
        return False

    def compare(self, img_list, acc=0.85, special=False):
        #self.check_enemy()
        # 檢查是否為support圖片
        if any("support" in img_path for img_path in img_list):
            sup_flag=1
        else:   
            sup_flag=0

        imgs = []
        self.screenshot = self.adbkit.screenshots()
        if sup_flag:
            cv2.rectangle(self.screenshot, (240, 0), (1280, 720),
                          color=(0, 0, 0), thickness=-1)

        for item in img_list:
            imgs.append(cv2.imread(item))

        if special:
            cv2.rectangle(self.screenshot, (0, 0), (1280, 420),
                          color=(0, 0, 0), thickness=-1)
        for index, img in enumerate(imgs):
            find_height, find_width = img.shape[:2:]
            #print(img)
            
            result = cv2.matchTemplate(
                self.screenshot, img, cv2.TM_CCOEFF_NORMED)
            reslist = cv2.minMaxLoc(result)
            if self.debug:
                cv2.rectangle(self.screenshot, reslist[3], (
                    reslist[3][0]+find_width, reslist[3][1]+find_height), color=(0, 250, 0), thickness=2)
            img_name = os.path.basename(img_list[index])
                #print(f"{img_name} acc rate:", round(reslist[1], 2))
            if sup_flag:
                if reslist[1] > 0.8:
                    print(f"\033[1;38;5;219m[Support] {img_name} acc rate: {round(reslist[1], 2)}\033[0m")
                else:
                    print(f"[Support] {img_name} acc rate: {round(reslist[1], 2)}")

                #if self.debug:
                    # 獲取當前圖像的文件名（不包括路徑）
                    #print(f"[Detect] {img_name} acc rate:", round(reslist[1], 2))
            pos = [reslist[3][0], reslist[3][1]]
            pos = [x*self.adbkit.capmuti for x in pos]
                
            #self.show_detection_result(reslist[3], find_width, find_height, round(reslist[1], 2), img_name)
            if reslist[1] > acc:    
                #if not sup_flag:
                    return pos, find_height*self.adbkit.capmuti, find_width*self.adbkit.capmuti
        if special:
            return False, 0, 0
        else:
            return False

    
    def compare_card(self, img_list, acc=0.85):
        imgs = []
        self.screenshot = self.adbkit.screenshots()
        for item in img_list:
            imgs.append(cv2.imread(item))

        for index, img in enumerate(imgs):
            find_height, find_width = img.shape[:2:]

            result = cv2.matchTemplate(self.screenshot, img, cv2.TM_CCOEFF_NORMED)

            # 展平结果数组并获取排序后的索引
            flat_result = result.flatten()
            sorted_indices = np.argsort(flat_result)[::-1]  # 从大到小排序

            # 初始化一个集合来存储属于 buster 的类别
            card_categories = set()
            def assign_value(pos):
                if 0 <= pos[0] < 256:
                    return 1
                elif 256 <= pos[0] < 512:
                    return 2
                elif 512 <= pos[0] < 768:
                    return 3
                elif 768 <= pos[0] < 1024:
                    return 4
                elif 1024 <= pos[0] < 1280:
                    return 5
                else:
                    return 0  # 超出範圍
            # 遍历排序后的索引
            for index in sorted_indices:
                score = flat_result[index]
                if score <= 0.9:
                    break  # 因为是从大到小排序，后面的分数都小于 0.85

                # 计算位置并转换为 (x, y) 形式
                pos = np.unravel_index(index, result.shape)
                pos = [pos[1], pos[0]]

                # 根据 pos[0] 分类
                category = assign_value(pos)
                if category != 0:
                    card_categories.add(category)
            # 根據圖片名稱輸出不同的提示
            if "buster.png" in str(img_list):
                print("Buster Card Location:", card_categories)
            elif "arts.png" in str(img_list):
                print("Arts Card Location:", card_categories)
            # 返回属于 buster 的类别
            return list(card_categories)

        return False
    def show_detection_result(self, top_left, width, height, acc_rate, img_name):
        # 創建截圖的副本，以免修改原始截圖
        display_img = self.screenshot.copy()
        
        # 在識別位置繪製矩形
        bottom_right = (top_left[0] + width, top_left[1] + height)
        cv2.rectangle(display_img, top_left, bottom_right, (0, 255, 0), 2)
        
        # 添加文字顯示準確率和圖像名稱
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(display_img, f"{img_name}: {acc_rate}", (10, 30), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
        
        # 顯示圖像
        cv2.imshow("檢測結果", display_img)
        cv2.waitKey(0)  # 顯示1秒
        cv2.destroyAllWindows()

    def tap(self, pos, raw=False):
        # 添加一个计时器变量
        if not hasattr(self, 'last_print_time'):
            self.last_print_time = time.time()
        
        # 检查是否已经过了30秒
        current_time = time.time()
        if current_time - self.last_print_time >= 30:
            print("\033[1;38;5;219m目前設備: {}\033[0m".format(self.device_name))
            self.last_print_time = current_time  # 重置计时器
            
        if raw:
            self.adbkit.click(pos[0], pos[1], raw=True)
        else:
            self.adbkit.click(pos[0], pos[1])

    def swipe(self, x1, y1, x2, y2, delay):
        self.adbkit.swipe(x1, y1, x2, y2, delay)




