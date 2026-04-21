import re
import random
from simpleeval import simple_eval

class MockMsg:
    def __init__(self, content):
        self.content = content

def coc_check(d_result,prob,cmd):
    fumble = (d_result == 100) or (d_result >= 96 and (cmd == "sc" or prob < 50))
    if d_result == 1: #Criticals
        return "恭喜！大成功！", "≤"
    elif fumble:
        result_msg = "技能值未達50！大失敗！" if (d_result >= 96 and prob < 50 and cmd == "cc") else "大失敗！"
        return result_msg, ">"
    elif d_result <= prob: #Success
        if d_result <= prob // 5:
            return "極限成功！", "≤"
        if d_result <= prob // 2:
            return "困難成功！", "≤"
        return "一般成功！", "≤"
    else:
        return "失敗！", ">"

def roll_dice(dice_string):
    try:
        x, y = map(int, dice_string.lower().split('d')) #xDy
        rolls = [random.randint(1, y) for _ in range(x)] #roll

        return sum(rolls), rolls
    except ValueError:
        return None, "Invalid format. Use XdY (e.g., 2d6)"

def eval_dice(dice_str):
    pattern = r'([+-*/]?)(\d+)d(\d+)|([+-*/]?)(\d+)'
    matches = re.finditer(pattern, dice_str)

    total = 0
    step = []

    for m in matches: #xdy
        if m.group(3):
            flag = m.group(1) or "+"
            sign = -1 if flag == "-" else 1
            num = int(m.group(2))
            face = int(m.group(3))
            ctotal, crolls = roll_dice(f"{num}d{face}")
            total += (ctotal * sign)
            step.append(f"{flag}({'+'.join(map(str, crolls))})")
        elif m.group(5):
            flag = m.group(4) or "+"
            sign = -1 if flag == "-" else 1
            const = int(m.group(5))
            total += const * sign
            step.append(f"{flag}{const}")

    full_step = "".join(step).lstrip('+')
    return total, full_step

def cc_main(msg, bp_flag = None, bp_num = 0, bp_text =""):
    spell = msg.content.split(" ")
    cc_cmd = spell[0]
    prob = min(int(spell[1]),99)
    info = " ".join(spell[2:]) if len(spell) > 2 else ""
    d_result, d_rolls = roll_dice("1d100")
    if bp_flag == "b" or bp_flag == "p":
        bp_rolls = [random.randint(0, 9) for _ in range(bp_num)]
        d_comp = int(d_result) / 10
        if bp_flag == "b":
            b_comp = min(bp_rolls)
            org_result = d_result
            if b_comp < d_comp:
                d_result = (b_comp * 10) + (org_result % 10)
        elif bp_flag == "p":
            p_comp = max(bp_rolls)
            org_result = d_result
            if p_comp > d_comp:
                d_result = (p_comp * 10) + (org_result % 10)
        bp_text = f"\n{org_result}{bp_flag}{bp_rolls}"
    check_result, flag = coc_check(d_result, prob, cc_cmd)
    return (f"CC {prob} {info}{bp_text}\n"
            f"{d_result} {flag} {prob}\n"
            f"結果：{check_result}")

def dd_main(msg, text2user =""):
    spell = msg.content.lower().split(" ")
    if "d" in spell[1]:
        dd_times = 1
        dd_msg = spell[1]
        info = " ".join(spell[2:]) if len(spell) > 2 else ""
    else:
        dd_times = int(spell[1])
        dd_msg = spell[2]
        info = " ".join(spell[3:]) if len(spell) > 3 else ""
    for x in range(dd_times):
            total, rolls = eval_dice(dd_msg)
            text2user += (f"#{x + 1} {dd_msg} {info}\n"
                          f"{rolls}\n"
                          f"={total}\n")
    return text2user

def sc_alg(flag, sc_suc, sc_fail, check_result):
    sc_fmla = sc_suc if flag == "≤" else sc_fail
    if check_result == "大失敗！":
        max_fmla = sc_fmla.lower().replace('d', '*') #replace d to * for cal
        deduct_t = deduct_r = simple_eval(max_fmla)
        return f"最大值：{max_fmla}", deduct_t, deduct_r
    else:
        deduct_t, deduct_r = eval_dice(sc_fmla)
        return sc_fmla, deduct_t, deduct_r

def sc_main(msg):
    try:
        spell = msg.split(" ")
        prob = min(int(spell[0]), 99)
        sc_suc, sc_fail = spell[1].lower().split('/')
    except (IndexError, ValueError):
        return "格式錯誤！範例：.sc 50 1/1d6"
    sc_value, _ = roll_dice("1d100")
    check_result, flag = coc_check(sc_value, prob, "sc")
    sc_dice, deduct_t, deduct_r = sc_alg(flag, sc_suc, sc_fail, check_result)
    after_sc = max(0, prob - deduct_t)
    return (f"SAN {prob}：{sc_suc}/{sc_fail}\n"
            f"{sc_value} {flag} {prob}\n"
            f"結果：{check_result}\n"
            f"{sc_dice}     {deduct_r}\n"
            f"{prob} - {deduct_t} → {after_sc}")

def dr_proc(text):
    msg = MockMsg(text)
    if "cc" in text:
        text2user = cc_main(msg)
    elif "dd" in text:
        text2user = dd_main(msg)
    return text2user