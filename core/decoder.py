def skill_btn(var):
    return {
        'a': int(1),
        'b': int(2),
        'c': int(3),
        'd': int(4),
        'e': int(5),
        'f': int(6),
        'g': int(7),
        'h': int(8),
        'i': int(9),
        'm': True,
        'x': True,
        't': True,
    }.get(var, False)  # 'error'為預設返回值，可自設定


def crd_btn(var):
    return {
        'a': int(6),
        'b': int(7),
        'c': int(8),
        '1': int(1),
        '2': int(2),
        '3': int(3),
        '4': int(4),
        '5': int(5),
    }.get(var, '0')  # 'error'為預設返回值，可自設定


def chk_card(crd):
    crd_list = []
    for x in crd:
        if x == "x":
            crd_list.append("\"{}\"".format(x))
        elif x=="y":
            crd_list.append("\"{}\"".format(x))
        elif x=="d":
            crd_list.append("\"{}\"".format(x))
        else:
            crd_list.append(crd_btn(x))
    # for i in range(len(crd)):
    #     if crd[i] != 'x':
    #         crd_list.append(crd_btn(crd[i]))
    #     else:
    #         pass
    return crd_list


def chk_skill(skill):
    cast_skill = []
    # print("round.waiting_phase(%s)"%nextround)
    for i in range(len(skill)):
        if skill_btn(skill[i]):
            if skill[i] == 'm':
                if not skill_btn(skill[i+1]):
                    if i + 2 < len(skill):
                        if not skill_btn(skill[i+2]):
                            cast_skill.append(
                                "round.select_master_skill(%s, %s)" % (skill[i+1], skill[i+2]))
                        else:
                            cast_skill.append(
                                "round.select_master_skill(%s)" % skill[i+1])
                    else:
                        cast_skill.append(
                            "round.select_master_skill(%s)" % skill[i+1])
            elif skill[i] == 'x':
                cast_skill.append(
                    "round.select_master_skill(3, %s, %s)" % (skill[i+1], skill[i+2]))
            elif skill[i] == 't':#點敵人
                cast_skill.append(
                    "round.select_enemy(%s)" % skill[i+1])
            elif i + 1 < len(skill):
                if not skill_btn(skill[i+1]):
                    cast_skill.append("round.select_servant_skill(%s, %s)" % (
                        skill_btn(skill[i]), skill[i+1]))
                else:
                    cast_skill.append(
                        "round.select_servant_skill(%s)" % skill_btn(skill[i]))
            else:
                cast_skill.append(
                    "round.select_servant_skill(%s)" % skill_btn(skill[i]))
    return cast_skill


def decode(code):
    combat_order = []
        # 檢查 crd3_str 和 battle3_str 是否為空字串
    if code[2] == "" and code[5] == "":
        loop_range = 2  # 如果 crd3_str 和 battle3_str 都是空字串，則迴圈範圍為 2
    else:
        loop_range = 3  # 否則，迴圈範圍為 3
    for i in range(loop_range):
        combat_order += chk_skill(code[i])
        if len(chk_card(code[i+3])) == 1:
            seq = chk_card(code[i+3])
            combat_order.append(
                "round.select_cards([{}])".format(str(seq[0])))
        elif len(chk_card(code[i+3])) == 2:
            seq = chk_card(code[i+3])
            combat_order.append(
                "round.select_cards([{}, {}])".format(str(seq[0]), str(seq[1])))
        elif len(chk_card(code[i+3])) == 3:
            seq = chk_card(code[i+3])
            combat_order.append(
                "round.select_cards([{}, {}, {}])".format(str(seq[0]), str(seq[1]), str(seq[2])))
    combat_order.append("round.finish_battle()")
    return combat_order
