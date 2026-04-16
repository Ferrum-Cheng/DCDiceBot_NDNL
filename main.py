import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import random
import webserver

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix = '.', intents = intents)

class MockMsg:
    def __init__(self, content):
        self.content = content\

def coc_check(d_result,prob,cmd):
    if d_result == 1 and prob > 1:
        check_result = "恭喜！大成功！"
        flag = "≤"
    elif d_result == 100:
        check_result = "大失敗！"
        flag = ">"
    elif d_result >= 96 and cmd == "sc":
        check_result = "大失敗！"
        flag = ">"
    elif d_result >= 96 and prob < 50 and cmd == "cc":
        check_result = "技能值未達50！大失敗！"
        flag = ">"
    elif d_result > prob:
        check_result = "失敗！"
        flag = ">"
    elif d_result <= int(prob / 5):
        check_result = "極限成功！"
        flag = "≤"
    elif d_result <= int(prob / 2):
        check_result = "困難成功！"
        flag = "≤"
    else:
        check_result = "一般成功！"
        flag = "≤"
    return check_result, flag

def sc_alg(flag, sc_sus, sc_fail, check_result):
    if flag == "≤":
        sc_dice = sc_sus
        if "d" not in sc_sus:
            deduct_v = int(sc_sus)
        else:
            deduct_v, deduct_r = roll_dice(sc_sus)
    elif flag == ">":
        sc_dice = sc_fail
        if "d" not in sc_fail:
            deduct_v = int(sc_fail)
        else:
            if check_result == "大失敗！":
                sc_dice = sc_fail.lower().split('d')
                deduct_v = sc_dice[1]
                deduct_r = "[" + str(sc_dice[1]) + "]"
                sc_dice = "最大值：" + str(deduct_v)
            else:
                deduct_v, deduct_r = roll_dice(sc_fail)
    return sc_dice, deduct_r , deduct_v

def roll_dice(dice_string):
    try:
        #xDy
        x, y = map(int, dice_string.lower().split('d'))

        #roll
        rolls = [random.randint(1, y) for _ in range(x)]
        total = sum(rolls)

        return total, rolls
    except ValueError:
        return None, "Invalid format. Use XdY (e.g., 2d6)"

def cc_main(msg, bp_flag = None, bp_num = 0, bp_text =""):
    spell = msg.content.split(" ")
    cc_cmd = spell[0]
    prob = int(spell[1])
    try:
        info = "：" + str(spell[2])
    except IndexError:
        info = ""  # if no info
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
    return (f"CC {prob}{info}{bp_text}\n"
            f"{d_result} {flag} {prob}\n"
            f"結果：{check_result}")

def dd_main(msg, text2user =""):
    spell = msg.content.lower().split(" ")
    if "d" in spell[1]:
        dd_num = 1
        dd_msg = spell[1]
        try:
            info = "：" + str(spell[2])
        except IndexError:
            info = ""  # if no info
    else:
        dd_num = int(spell[1])
        dd_msg = spell[2]
        try:
            info = "：" + str(spell[3])
        except IndexError:
            info = ""  # if no info
    for x in range(dd_num):
        if ("+" or "-") in dd_msg:
            cal_text, step_text, total_result = sym_handler(dd_msg)
            text2user += (f"#{x + 1} {dd_msg}{info}\n"
                         f"{step_text} = {cal_text}\n"
                         f"={total_result}\n")
        else:
            total, rolls = roll_dice(dd_msg)
            text2user += (f"#{x + 1} {dd_msg}{info}\n"
                         f"{rolls}\n"
                         f"={total}\n")
    return text2user

def ps_handler(cal_text, step_text, sym):
    ps_cal = cal_text.split(str(sym))
    ps_step = step_text.split(str(sym))
    step_text = cal_text = ""
    for x in range(len(ps_cal)):
        if "d" not in ps_cal[x]:
            step_text += str(ps_step[x])
        else:
            ps_total, ps_rolls = roll_dice(str(ps_cal[x]))
            ps_cal[x] = ps_total
            step_text += str(ps_rolls)
        cal_text += str(ps_cal[x])
        if x == len(ps_cal) - 1: break
        cal_text += str(sym)
        step_text += str(sym)
    return cal_text, step_text

def sym_handler(dd_msg):
    step_text = cal_text = dd_msg
    if "+" in dd_msg:
        sym = "+"
        cal_text, step_text = ps_handler(cal_text,step_text,sym)
    if "-" in dd_msg:
        sym = "-"
        cal_text, step_text = ps_handler(cal_text,step_text,sym)
    if "d" not in cal_text:
        total_result = eval(cal_text)
    return cal_text, step_text, total_result

def sc_fuction(msg):
    spell = msg.content.split(" ")
    sc_cmd = spell[0]
    prob = int(spell[1])
    sc_statement = spell[2].lower().split('/')
    sc_sus = sc_statement[0]
    sc_fail = sc_statement[1]
    sc_value, sc_rolls = roll_dice("1d100")
    check_result, flag = coc_check(sc_value, prob, sc_cmd)
    sc_dice, deduct_r, deduct_v = sc_alg(flag, sc_sus, sc_fail, check_result)
    after_sc = prob - deduct_v
    return (f"San Check {prob}：{sc_sus}/{sc_fail}\n"
                                   f"{sc_value} {flag} {prob}\n"
                                   f"結果：{check_result}\n"
                                   f"{sc_dice} {deduct_r}\n"
                                   f"{prob} - {deduct_v} → {after_sc}")

def dr_proc(text):
    msg = MockMsg(text)
    if "cc" in text:
        text2user = cc_main(msg)
    elif "dd" in text:
        text2user = sc_fuction(msg)
    return text2user

def ccrt_text(case_code):
    match case_code:
        case 1:
            return f"昏厥或尖叫"
        case 2:
            return f"驚慌失措地逃跑"
        case 3:
            return f"歇斯底里或情緒爆發(狂笑、哭泣等等)"
        case 4:
            return f"發出嬰兒般的咿呀聲，說話無條理、速語症、多語症"
        case 5:
            return f"強烈恐懼症，可能會定在當場不能動彈"
        case 6:
            return f"殺人傾向或自殺傾向"
        case 7:
            return f"出現幻覺或妄想症"
        case 8:
            return f"不自覺地模仿旁人的動作"
        case 9:
            return f"奇怪的食欲(泥土、黏土、人肉)"
        case 10:
            return f"恍惚(像胎兒一樣蜷縮起來，忘記一切)或緊張型精神分裂(對一切失去興趣，必須有別人引導，否則無法進行任何獨立行動)"
        case _:
            return None

def ccsu_text(case_code):
    match case_code:
        case 1:
            return f"記憶缺失、健忘(症)或恍惚/緊張症"
        case 2:
            return f"嚴重的恐懼症(可能逃跑，或將所有東西都看成害怕的東西)"
        case 3:
            return f"幻覺"
        case 4:
            return f"奇怪的性取向(裸露癖、女子淫狂/男子淫狂等)"
        case 5:
            return f"找到了某樣「幸運符」(把某樣飾品、器物甚至某人當作安全毯)，如果遠離就會一事無成"
        case 6:
            return f"無法控制地抽搐、顫抖，無法藉由語言或書寫交談"
        case 7:
            return f"精神性的失明、失聰，或某個肢體無法使用"
        case 8:
            return f"反應性精神障礙(語無倫次、幻覺、妄想症或行為異常)"
        case 9:
            return f"暫時的偏執狂"
        case 10:
            return f"強迫症(不停洗手、祈禱，以特定節奏走路，不願走在某些路面上，總是檢查子彈是否上膛等等)"
        case _:
            return None

def bd7_main(code):
    f_total = []
    f_rolls = []
    if code == "":
        x = 5
        y = 3
        z = 1
    else:
        x, y, z = list(map(int, code))

    for i in range(x):
        total, rolls = roll_dice("3d6")
        f_rolls.append(str(rolls) + "×5")
        f_total.append(str(total * 5))
    for i in range(y):
        total, rolls = roll_dice("2d6")
        f_rolls.append("{" + str(rolls) + "+6}" + "×5")
        f_total.append(str((total + 6) * 5))
    for i in range(z):
        total, rolls = roll_dice("3d6")
        f_rolls.append(str(rolls) + "×5")
        f_total.append(str(total * 5))
    if x == 5 and y == 3 and z == 1:
        buildtxt = (f"=============\n"
                    f"STR：{f_rolls[0]} = {f_total[0]}\n"
                    f"CON：{f_rolls[1]} = {f_total[1]}\n"
                    f"DEX：{f_rolls[2]} = {f_total[2]}\n"
                    f"APP：{f_rolls[3]} = {f_total[3]}\n"
                    f"POW：{f_rolls[4]} = {f_total[4]}\n"
                    f"=============\n"
                    f"INT：{f_rolls[5]} = {f_total[5]}\n"
                    f"SIZ：{f_rolls[6]} = {f_total[6]}\n"
                    f"EDU：{f_rolls[7]} = {f_total[7]}\n"
                    f"=============\n"
                    f"LUK：{f_rolls[8]} = {f_total[8]}\n"
                    f"=============\n")
    else:
        buildtxt = f"自由分配屬性點數\n"
        buildtxt += f"=== 3D6 for STR, CON, DEX, APP, POW ===\n"
        for j in range(x):
            buildtxt += f"{f_rolls[j]} = {f_total[j]}\n"
        buildtxt += f"=== 2D6+6 for INT, SIZ, EDU ===\n"
        for j in range(y):
            buildtxt += f"{f_rolls[j+x]} = {f_total[j+x]}\n"
        buildtxt += f"=== 3D6 for LUK ===\n"
        for j in range(z):
            buildtxt += f"{f_rolls[j+x+y]} = {f_total[j+x+y]}\n"
        buildtxt += f"=============\n"
    return buildtxt

#manual
@bot.command()
async def man(ctx):
    await ctx.send(f"# 使用教學\n"
                   f"### dd [z] xDy±jDk (info)\n"
                   f"普通擲骰z次(描述)\n"
                   f"### cc [prob] (info)\n"
                   f"CoC技能檢定(描述)\n"
                   f"### sc [prob] xDy/jDk\n"
                   f"SAN值檢定 成功/失敗\n"
                   f"### .ccb [z] [prob] (info)\n"
                   f"獎勵骰z枚\n"
                   f"### .ccp [z] [prob] (info)\n"
                   f"懲罰骰z枚\n"
                   f"### .ccrt\n"
                   f"暫時性瘋狂\n"
                   f"### .ccsu\n"
                   f"不定期瘋狂\n"
                   f"### .sg [x_prob] [x_skill]/[y_prob] [y_skill]\n"
                   f"成長檢定\n"
                   f"### .ddr [cc_roll/dd_roll]\n"
                   f"暗骰至KP及自己\n"
                   f"### .dddr [cc_roll/dd_roll]\n"
                   f"暗骰至KP\n"
                   f"### .cc7bd (xyz)\n"
                   f"CoC7th創角\n"
                   f"### .mkKP\n"
                   f"設定暗骰指向至自己[需有KP身份組]\n"
                   f"### .rmKP\n"
                   f"消暗骰指向[需有KP身份組]\n"
                   f"### .shKP\n"
                   f"查詢暗骰指向[需有TRPG身份組]\n"
                   f"### .trpg\n"
                   f"取得TRPG身份組\n"
                   f"### .ntrpg\n"
                   f"移除TRPG身份組\n")

grp_KP_mn = None
grp_KP_id = 0

@bot.command()
async def trpg(ctx):
    role = discord.utils.get(ctx.guild.roles, name="TRPG")
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"歡迎{ctx.author.mention}進入TRPG嘅世界")
    else:
        await ctx.send("伺服器上沒有TRPG身份組")

@bot.command()
async def ntrpg(ctx):
    role = discord.utils.get(ctx.guild.roles, name="TRPG")
    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(f"期待{ctx.author.mention}下次再玩TRPG")
    else:
        await ctx.send("伺服器上沒有TRPG身份組")

@bot.command()
@commands.has_role("KP")
async def mkKP(ctx):
    global grp_KP_mn, grp_KP_id
    grp_KP_mn = ctx.author.mention
    grp_KP_id = ctx.author.id
    await ctx.send(f"暗骰指向已設置至{grp_KP_mn}")

@bot.command()
@commands.has_role("KP")
async def rmKP(ctx):
    global grp_KP_mn, grp_KP_id
    grp_KP_mn = grp_KP_id = None
    await ctx.send(f"暗骰指向已取消")

@bot.command()
@commands.has_role("TRPG")
async def shKP(ctx):
    if grp_KP_mn is None:
        await ctx.send("沒有KP被設定")
    else:
        await ctx.send(f"暗骰已設定至{grp_KP_mn}")

@bot.command()
async def ddr(ctx, *, text):
    if grp_KP_mn is None:
        await ctx.send(f"沒有KP被設定")
    else:
        text2user = dr_proc(text)
        KP = await bot.fetch_user(grp_KP_id)
        await KP.send(f"{ctx.author.mention}的暗骰\n"
                      f"{text2user}")
        await ctx.author.send(f"{ctx.author.mention}的暗骰\n"
                              f"{text2user}")
        await ctx.send(f"{ctx.author.mention}的暗骰已傳送至{grp_KP_mn}及{ctx.author.mention}的DM")

@bot.command()
async def dddr(ctx, *, text):
    if grp_KP_mn is None:
        await ctx.send(f"沒有KP被設定")
    else:
        text2user = dr_proc(text)
        KP = await bot.fetch_user(grp_KP_id)
        await KP.send(f"{ctx.author.mention}的暗骰\n"
                      f"{text2user}")
        await ctx.send(f"{ctx.author.mention}的暗骰已傳送至{grp_KP_mn}的DM")

@bot.command()
async def ccb(ctx, *, text):
    msg = text.split(" ")
    b_num = int(msg[0])
    spell = "cc " + str(msg[1])
    try:
        spell += " " + str(msg[2])
    except IndexError:
        spell += ""
    text2user = cc_main(MockMsg(spell), "b", b_num)
    await ctx.send(f"{ctx.author.mention}\n"
                   f"{text2user}")

@bot.command()
async def ccp(ctx, *, text):
    msg = text.split(" ")
    p_num = int(msg[0])
    spell = "cc " + str(msg[1])
    try:
        spell += " " + str(msg[2])
    except IndexError:
        spell += ""
    text2user = cc_main(MockMsg(spell), "p", p_num)
    await ctx.send(f"{ctx.author.mention}\n"
                   f"{text2user}")

@bot.command()
async def sg(ctx, *, text):
    text2user = ""
    skill = text.split("/")
    for x in range(len(skill)):
        msg = skill[x].split(" ")
        prob = int(msg[0])
        roll = random.randint(1, 100)
        if roll >= 96 or roll > prob:
            value = random.randint(1, 10)
            upgraded = prob + value
            text2user += (f"技能成長：{msg[1]}\n"
                          f"{roll} > {prob}：成長成功\n"
                          f"1D10 = {value}\n"
                          f"{prob} + {value} = {upgraded}\n")
        elif roll < prob:
            text2user += (f"技能成長：{msg[1]}\n"
                          f"{roll} > {prob}：成長失敗\n"
                          f"保持：{prob}\n")
    await ctx.send(f"{ctx.author.mention}\n"
                   f"{text2user}")

@bot.command()
async def cc7bd(ctx, text=""):
    text2user = bd7_main(text)
    await ctx.send(f"{ctx.author.mention}\n"
                   f"{text2user}")

@bot.command()
async def ccrt(ctx):
    case_code = random.randint(1, 10)
    text2user = ccrt_text(case_code)
    await ctx.send(f"{ctx.author.mention}\n"
                   f"#{case_code} "
                   f"{text2user}")

@bot.command()
async def ccsu(ctx):
    case_code = random.randint(1, 10)
    text2user = ccsu_text(case_code)
    await ctx.send(f"{ctx.author.mention}\n"
                   f"#{case_code} "
                   f"{text2user}")

@shKP.error
async def shKP_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send(f"{ctx.author.mention}你不是TRPG玩家!")

@mkKP.error
@rmKP.error
async def KP_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("你不是KP!")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
       return

    #coc skill check
    if message.content.startswith("cc"):
        msg = message
        text2user = cc_main(msg)
        await message.channel.send(f"{message.author.mention}\n"
                                   f"{text2user}")

    #san check
    if message.content.startswith("sc"):
        msg = message
        text2user = sc_fuction(msg)
        await message.channel.send(f"{message.author.mention}\n"
                                   f"{text2user}")

    #roll
    if message.content.startswith("dd"):
        msg = message
        text2user = dd_main(msg)
        await message.channel.send(f"{message.author.mention}\n"
                                   f"{text2user}")

    await bot.process_commands(message)

webserver.keep_alive()

bot.run(token, log_handler=handler, log_level=logging.DEBUG)