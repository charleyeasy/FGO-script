import time
import random
import os
from types import coroutine
from core.tool import tool
from configparser import ConfigParser
import threading


class auto():
    def __init__(self, ckp, spt, cls,servant_class,apl_count, apl_type, devices, timer=12000, run_time=1, ver="JP", debug=0):
        self.path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.checkpoint = ckp #menu.png
        self.support = []
        self.support = self.get_support(spt)
        self.clothes = self.get_clothes(cls)
        self.servant_class = servant_class
        self.counts = int(apl_count)  # apple counts
        self.apple = apl_type
        self.timer = int(timer)
        self.cfg = ConfigParser()
        self.cfg.read("{0}/core/button.ini".format(self.path))
        self.run_time = run_time
        self.total_time = 0
        self.now_time = 0
        self.t_begin = 0
        self.t_end = 0
        self.adbtool = tool(devices, debug=debug)
        self.ver = ver
        self.debug = debug
        self.device_name = devices
        #self.stop_printing = threading.Event()
        #self.print_thread = None
        #self.thread_lock = threading.Lock()
        #self.start_device_printing()

    def get_support(self, spt):
        if os.path.isfile("{0}/UserData/support/{1}.png".format(self.path, spt)):
            support = []
            support.append("{0}/UserData/support/{1}.png".format(self.path, spt))
            return support
        elif os.path.isdir("{0}/UserData/support/{1}".format(self.path, spt)):
            support = []
            for each in os.listdir("{0}/UserData/support/{1}".format(self.path, spt)):
                support.append(
                    "{0}/UserData/support/{1}/{2}".format(self.path, spt, each))
            
            return support
        else:
            print("無法找到助戰圖片")

    def get_clothes(self, cls):
        if cls == "all" or cls == "('all')":
            print(cls)
            return ["all"]
        if os.path.isfile("{0}/UserData/support/{1}.png".format(self.path, cls)):
            clothes = []
            clothes.append("{0}/UserData/support/{1}.png".format(self.path, cls))
            return clothes
        elif os.path.isdir("{0}/UserData/support/{1}".format(self.path, cls)):
            clothes = []
            for each in os.listdir("{0}/UserData/support/{1}".format(self.path, cls)):
                clothes.append(
                    "{0}/UserData/support/{1}/{2}".format(self.path, cls, each))
            return clothes
        else:
            print("無法找到禮裝圖片")

    def get_img_path(self, img_name):
        img = []
        img_path = "{0}/images/{1}/{2}".format(self.path, self.ver, img_name)
        img.append(img_path)
        return img

    def quick_start(self, first=False):
        self.select_task(self.checkpoint, first)
        if first:
            time.sleep(3)
            pos = self.cfg['class']['%s' %self.servant_class]
            pos = pos.split(',')
            self.adbtool.tap(pos)
        else:
            time.sleep(6)

        self.advance_support(self.support,self.clothes)
        if first or self.now_time == 1:
            self.start_battle()

    def select_task(self, ckp: str, first=False):
        if first or self.now_time == 0:
            print("[INFO] Waiting Task selected")
            # self.adbtool.compare(self.get_img_path(self.checkpoint)):
            while not self.adbtool.compare(self.get_img_path(self.checkpoint)):
                pass
            self.adbtool.tap((1100, 170))
        time.sleep(0.5)
        self.t_begin = time.time()
        noapcheck1=self.adbtool.compare(self.get_img_path("noap.png"))
        noapcheck2=self.adbtool.compare(self.get_img_path("noap2.png"))
        print("No Ap Check1:",noapcheck1,"No Ap Check2::",noapcheck2)
        if noapcheck1 or noapcheck2:
            print("[INFO] Out of AP!")
            if self.counts >= 0:
                self.counts -= 1
                if self.counts == -1:
                    self.adbtool.tap((635, 610))
                    self.wait_ap(self.timer)
                    self.select_task(self.checkpoint, first=True)
                else:
                    self.eat_apple()
            elif self.counts == -1:
                self.adbtool.tap((635, 610))
                self.wait_ap(self.timer)
                self.select_task(self.checkpoint, first=True)
            else:
                print("[INFO] Out of appale count")
                raise NoAppleException("[INFO] 沒有蘋果了!")
        self.now_time += 1
        print("[INFO] Task selected.")

    def eat_apple(self):
        #print("[INFO]Select apple:", end='')
        if self.apple == 'gold':
            pos = self.cfg['apple']['gold']
            pos = pos.split(',')
            self.adbtool.tap(pos)
        elif self.apple == 'silver':
            pos = self.cfg['apple']['silver']
            pos = pos.split(',')
            self.adbtool.tap(pos)
        elif self.apple == 'blue':
            pos = self.cfg['apple']['blue']
            pos = pos.split(',')
            self.adbtool.tap(pos)
        elif self.apple == 'star':
            pos = self.cfg['apple']['star']
            pos = pos.split(',')
            self.adbtool.tap(pos)
        elif self.apple == 'bronze':
            self.adbtool.swipe(500, 470, 500, 20, 0.3)
            time.sleep(0.5)
            pos = self.cfg['apple']['bronze']
            pos = pos.split(',')
            self.adbtool.tap(pos)
        time.sleep(2)
        if self.adbtool.compare(self.get_img_path("confirm.png")):
            print("[INFO] Apple button Confirm")
            pos = self.cfg['apple']['use']
            pos = pos.split(',')
            self.adbtool.tap(pos)
        else:
            print("[INFO] Apple button not found")
            raise NoAppleException("[INFO] 沒有蘋果了!")

        print("[INFO] Remain apple counts:", self.counts)

    def wait_ap(self, timer):
        tStart = time.time()
        tEnd = time.time()
        print("[INFO] Start to wait AP")
        while not int(tEnd - tStart) >= timer:
            remain = timer - int(tEnd - tStart)
            if remain <= 60:
                print("[INFO] Remain", remain, "seconds", end='\r')
            else:
                remain /= 60.0
                remain = round(remain, 1)
                print("[INFO] Remain", remain, "minutes", end='\r')
            for i in range(30):  # note i用來計時沒用到
                tEnd = time.time()
                if int(tEnd - tStart) >= timer:
                    break
                time.sleep(1)

    def update_support(self):
        update_pos = self.adbtool.compare(self.get_img_path("update.png"))
        if update_pos:
            self.adbtool.tap((int(update_pos[0][0])+int(update_pos[2]/2),
                              int(update_pos[0][1])+int(update_pos[1]/2)), raw=True)
            self.adbtool.tap((835, 125))
            time.sleep(0.2)
            if self.adbtool.compare(self.get_img_path("close.png")):
                self.adbtool.tap((640, 560))
                print("[INFO] Wait to refresh friend list")
                time.sleep(2)
            else:
                self.adbtool.tap((840, 560))
                print("[INFO] friend list refresh")
                time.sleep(4)
            pos = self.cfg['class']['%s' %self.servant_class]
            pos = pos.split(',')
            self.adbtool.tap(pos)

    def advance_support(self, spt,clothes):
        flag1 = True #尋找指定的支援角色。
        flag2 = True #滾動邏輯
        Friend_not_found_count=0
        # TODO 檢查確定進選好有畫面後再繼續動作
        while flag1:
            #spt_pos = self.adbtool.compare(spt,acc=0.85)
            spt_pos=self.adbtool.find_support(spt,clothes,acc=0.85)
            #clothes_pos = self.adbtool.compare(self.get_img_path("clothes.png"),acc=0.85)

            if spt_pos == False:
                print("[INFO] Friend not found")
                Friend_not_found_count+=1

                if flag2:
                    if Friend_not_found_count>=50:
                        print("[INFO] 可能卡bug了，直接update_support")
                        self.update_support()
                        Friend_not_found_count = 0

                    bar_pos = self.adbtool.compare(
                        self.get_img_path("bar.png"))
                    if bar_pos:
                        #if self.debug:
                        print("no bar")#沒滾輪 直接更新
                        self.update_support()
                    else:
                        #if self.debug:
                        print("have bar")
                        flag2 = False
                        end_pos = self.adbtool.compare(
                            self.get_img_path("friendEnd.png"), acc=0.985)
                        if end_pos:
                            print("[INFO] End of friend list")
                            self.update_support()
                            flag2 = True
                        else:
                            
                            gap_pos, gap_h, gap_w = self.adbtool.compare(
                                self.get_img_path("friend_gap.png"), 0.8, True)
                            if gap_pos:
                                gap_pos = [x for x in gap_pos]
                                self.adbtool.swipe(gap_pos[0]+(gap_w/2), 400, gap_pos[0]+(gap_w/2), 100, 0.2)
                                time.sleep(0.5)
                            else:
                                gap_pos, gap_h, gap_w = self.adbtool.compare(
                                self.get_img_path("friend_gap2.png"), 0.8, True)#有可能助戰是藍色的NPC
                                if gap_pos:
                                    gap_pos = [x for x in gap_pos]
                                    self.adbtool.swipe(gap_pos[0]+(gap_w/2), 400, gap_pos[0]+(gap_w/2), 100, 0.2)
                                else:
                                    print("沒找到gap_pos，卡bug了")
                                    self.update_support()
                            # 假設您在某個地方需要滾動
                            #self.adbtool.scroll(direction='down', distance=100, duration=500)  # 向上滾動
                else:
                    bar_pos = self.adbtool.compare(
                        self.get_img_path("bar.png"))
                    if bar_pos:
                        if self.debug:
                            print("no bar")
                        self.update_support()
                    else:
                        end_pos = self.adbtool.compare(
                            self.get_img_path("friendEnd.png"), acc=0.985)
                        if end_pos != False:
                            print("[INFO] End of friend list")
                            self.update_support()
                            flag2 = True
                        else:
                            if self.debug:
                                print("swipe down")
                            gap_pos, gap_h, gap_w = self.adbtool.compare(
                                self.get_img_path("friend_gap.png"), 0.8, True)
                            if gap_pos:
                                gap_pos = [x for x in gap_pos]
                                self.adbtool.swipe(gap_pos[0]+(gap_w/2), 400, gap_pos[0]+(gap_w/2), 100, 0.2)
                                time.sleep(0.5)
                            else:
                                gap_pos, gap_h, gap_w = self.adbtool.compare(
                                self.get_img_path("friend_gap2.png"), 0.8, True)#有可能助戰是藍色的NPC
                                if gap_pos:
                                    gap_pos = [x for x in gap_pos]
                                    self.adbtool.swipe(gap_pos[0]+(gap_w/2), 400, gap_pos[0]+(gap_w/2), 100, 0.2)
                                else:
                                    print("沒找到gap_pos，卡bug了")
                                    self.update_support()
            else:
               
                flag1 = False
                self.adbtool.tap((int(spt_pos[0][0])+int(spt_pos[2]/2),
                                  int(spt_pos[0][1])+int(spt_pos[1]/2)), raw=True)
                #print("找到妳囉")
                

    def start_battle(self):
        start_counter=0
        while not self.adbtool.compare(self.get_img_path("start.png")):
            #print("等待開始鍵")
            start_counter+=1
            if start_counter>=5:
                if self.adbtool.compare(self.get_img_path("start2.png")):
                    print("白癡喔是戰鬥開始")
                    break
        self.adbtool.tap((1180, 670))
        print("[INFO] Battle started.  ")

    def select_servant_skill(self, skill: int, tar: int = 0):
        maybe_skip_counter=0
        while not self.adbtool.compare(self.get_img_path("attack.png")):
           #print("[BATTLE] Waiting for Attack button")
            maybe_skip_counter+=1
            self.adbtool.tap((920, 45))
            self.adbtool.tap((920, 45))
            if maybe_skip_counter>=10:
                pos = self.adbtool.compare(self.get_img_path("skip.png"))
                pos2 = self.adbtool.compare(self.get_img_path("skip_auto.png"))
                if pos or pos2:
                    print("*****FIND SKIP*****")
                    self.adbtool.tap((1240, 45))
                    time.sleep(1)
                    pos = False
                    while not pos:
                        pos = self.adbtool.compare(self.get_img_path("skip_yes.png"))
                    print("*****SKIP THAT SHIT*****")
                    self.adbtool.tap((int(pos[0][0])+int(pos[2]/2),int(pos[0][1])+int(pos[1]/2)), raw=True)
                maybe_skip_counter=0
        pos = self.cfg['skills']['%s' % skill]
        pos = pos.split(',')
        self.adbtool.tap(pos)
        if tar != 0:
            print("[SKILL] Use servent", str(int((skill-1)/3 + 1)),
                  "skill", str((skill-1) % 3 + 1), "to servent", tar)
            self.select_servant(tar, pos)
        else:
            self.adbtool.tap((920, 45))
            self.adbtool.tap((920, 45))
            self.adbtool.tap((920, 45))
            self.adbtool.tap((920, 45))
            print("[SKILL] Use servent", str(int((skill-1)/3 + 1)),
                  "skill", str((skill-1) % 3 + 1), "      ")


    def select_servant(self, servant: int, skill_pos=False):
        time.sleep(0.01)
        check_counter = 0
        check_interval = 2  # 每2次循環才檢查一次rin_select
        
        while True:
            if self.adbtool.compare(self.get_img_path("select.png")):
                break
                
            check_counter += 1
            if check_counter >= check_interval:
                if self.adbtool.compare(self.get_img_path("rin_select.png")):
                    break
                check_counter = 0
            print("[SKILL] Waiting for servent select")
            #if skill_pos:
            #    self.adbtool.tap(skill_pos)
        pos = self.cfg['servent']['%s' % servant]
        pos = pos.split(',')
        self.adbtool.tap(pos)
        self.adbtool.tap((920, 45))
        self.adbtool.tap((920, 45))
        self.adbtool.tap((920, 45))
        self.adbtool.tap((920, 45))

    def select_enemy(self, enemy: int):
        
        while not self.adbtool.compare(self.get_img_path("attack.png")):
            #print("[BATTLE] Waiting for Attack button")
            self.adbtool.tap((920, 45))
            self.adbtool.tap((920, 45))
        time.sleep(0.01)
        print("[Select] Enemy",enemy)
        pos = self.cfg['enemy']['%s' % enemy]
        pos = pos.split(',')
        self.adbtool.tap(pos)


    def select_cards(self, cards):
        time.sleep(0.01)
        #print("\033[1;35m目前設備: {}\033[0m".format(self.device_name))
        while not self.adbtool.compare(self.get_img_path("attack.png")):
            #print("[BATTLE] Waiting for Attack button")
            self.adbtool.tap((920, 45))
            self.adbtool.tap((920, 45))
        # tap ATTACK
        # 比對血量
        enemy_count, max_hp_position=self.adbtool.check_enemy()
        #print(f"敵人數量: {enemy_count}")
        #print(f"最大血量的敵人位置: {max_hp_position}")
        pos = self.cfg['attack']['button']
        pos = pos.split(',')
        self.adbtool.tap(pos)
        time.sleep(0.7)
        
        if "y" in cards:
            buster_positions = []
            time.sleep(1)
            buster_positions=self.adbtool.compare_card(self.get_img_path("buster.png"), acc=0.8)
            for i in range(len(cards) - 1, -1, -1):  # 從後往前遍歷
                if cards[i] == 'y':
                    if buster_positions:
                        cards[i] = buster_positions.pop(0)
                    else:
                        cards[i] = "x"
        if "d" in cards:
            arts_positions = []
            time.sleep(1)
            arts_positions=self.adbtool.compare_card(self.get_img_path("arts.png"), acc=0.8)
            for i in range(len(cards) - 1, -1, -1):  # 從後往前遍歷
                if cards[i] == 'd':
                    if arts_positions:
                        cards[i] = arts_positions.pop(0)
                    else:
                        cards[i] = "x"

        i=0
        while "x" in cards:
            if cards[i] == "x":
                x = random.randrange(1, 6)
                if x in cards:
                    continue
                else:
                    cards[i] = x
                    i += 1
            else:
                i += 1
        for card in cards:
            pos = self.cfg['attack']['%s' % card]
            pos = pos.split(',')
            self.adbtool.tap(pos)
            time.sleep(0.1)
        print("[BATTLE] Selected cards: ", cards)

    def select_master_skill(self, skill: int, org: int = 0, tar: int = 0):
        time.sleep(0.3)
        #print("[Select] Master Skill",org,tar)
        while not self.adbtool.compare(self.get_img_path("attack.png")):
            #print("[BATTLE] Waiting for Attack button")
            self.adbtool.tap((920, 45))
        self.toggle_master_skill()
        pos = self.cfg['master']['%s' % skill]
        pos = pos.split(',')
        pos = [x for x in pos]
        self.adbtool.tap(pos)
        print("[M_Skill] Use master skill", skill)
        if org != 0 and tar == 0:
            self.select_servant(org)
        elif org != 0:
            self.change_servant(org, tar)

    def toggle_master_skill(self):
        time.sleep(0.2)
        while not self.adbtool.compare(self.get_img_path("attack.png")):
            #print("[BATTLE] Waiting for Attack button")
            self.adbtool.tap((920, 45))
            self.adbtool.tap((920, 45))
        pos = self.cfg['master']['button']
        pos = pos.split(',')
        self.adbtool.tap(pos)
        print("[M_Skill] Toggle master skill bar")
        time.sleep(1)

    def change_servant(self, org: int, tar: int):
        time.sleep(0.2)
        while not self.adbtool.compare(self.get_img_path("order_change.png")):
            print("[M_Skill] Waiting for order change")
        pos = self.cfg['servent']['s%s'% org]
        pos = pos.split(',')
        self.adbtool.tap(pos)
        time.sleep(0.1)
        pos = self.cfg['servent']['a%s'% tar]
        pos = pos.split(',')
        self.adbtool.tap(pos)
        time.sleep(0.1)
        self.adbtool.tap((650, 620))  # confirm btn
        time.sleep(0.5)
    def finish_battle(self):
        # TODO 最佳化辨識流程

        while not self.adbtool.compare(self.get_img_path("next.png")):
            #print("[FINISH] Waiting next button")
            self.adbtool.tap((1000, 45))
        print("[FINISH] Battle finish      ")
        self.adbtool.tap((1105, 670))
        time.sleep(1)


        if self.now_time < self.run_time:
            continue_flag = True
        else:
            continue_flag = False
        ckp = False
        flag = True
        friend_flag = False
        while flag:
            time.sleep(0.1)
            pos = self.adbtool.compare(self.get_img_path("friendrequest.png"))
            self.adbtool.tap((1000, 45))
            if pos and not friend_flag:
                self.adbtool.tap((330, 610))
                friend_flag = True
                print("[FINISH] Reject friend request")
            else:
                if self.adbtool.compare(self.get_img_path("next.png")):
                    self.adbtool.tap((1105, 670))
                elif self.adbtool.compare(self.get_img_path("ingame_close.png")):
                    pos = self.adbtool.compare(self.get_img_path("ingame_close.png"))
                    self.adbtool.tap((int(pos[0][0])+int(pos[2]/2),
                                    int(pos[0][1])+int(pos[1]/2)), raw=True)
                else:
                    pos = self.adbtool.compare(self.get_img_path("continue.png"))
                    if pos:
                        flag = False
                    elif self.adbtool.compare(self.get_img_path(self.checkpoint)):
                        flag = False
                        ckp = True
        self.t_end = time.time()
        self.total_time += int(self.t_end-self.t_begin)
        print("執行 {0} 次;用時 {1} 秒; 總計 {2} 秒;".format(
            self.now_time, int(self.t_end-self.t_begin), self.total_time))
        if continue_flag:
            if not ckp:
                pos = self.adbtool.compare(self.get_img_path("continue.png"))
                self.adbtool.tap((int(pos[0][0])+int(pos[2]/2),
                                  int(pos[0][1])+int(pos[1]/2)), raw=True)
            self.quick_start(ckp)
        elif self.adbtool.compare(self.get_img_path("noap.png")):
            self.adbtool.tap((635, 610))
        elif continue_flag == False:
            pos = self.adbtool.compare(self.get_img_path("close.png"))
            while not pos:
                pos = self.adbtool.compare(self.get_img_path("close.png"))
                ckp = self.adbtool.compare(self.get_img_path(self.checkpoint))
                if ckp:
                    break
            if pos and not ckp:
                self.adbtool.tap(pos[0], raw=True)
'''
    def print_device_name(self):
        while not self.stop_printing.is_set():
            print("\033[1;38;5;219m目前設備: {}\033[0m".format(self.device_name))
            #print("\033[1;38;5;213m目前設備: {}\033[0m".format(self.device_name))
            #print("\033[1;95m目前設備: {}\033[0m".format(self.device_name))
            # 使用 wait 代替 sleep，這樣可以更快地響應停止信號
            if self.stop_printing.wait(timeout=30):
                break


    def start_device_printing(self):
        # 如果之前的線程還在運行，先停止它
        self.stop_device_printing()
        
        self.stop_printing.clear()
        self.print_thread = threading.Thread(target=self.print_device_name)
        self.print_thread.daemon = True
        self.print_thread.start()

    def stop_device_printing(self):
        with self.thread_lock:
            if self.print_thread and self.print_thread.is_alive():
                self.stop_printing.set()
                try:
                    self.print_thread.join(timeout=1)
                except RuntimeError as e:
                    print(f"警告：停止打印線程時發生錯誤: {e}")
                except Exception as e:
                    print(f"未預期的錯誤: {e}")
                finally:
                    self.print_thread = None
            else:
                print("打印線程已經停止或不存在")'''


class NoAppleException(Exception):
    pass







