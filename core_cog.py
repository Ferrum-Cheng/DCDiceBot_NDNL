import random

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
        total = sum(rolls)

        return total, rolls
    except ValueError:
        return None, "Invalid format. Use XdY (e.g., 2d6)"