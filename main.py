import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import random

import core
import san
import kpndr
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
        self.content = content

def ps_handler(cal_text, step_text, sym):
    ps_cal = cal_text.split(str(sym))
    ps_step = step_text.split(str(sym))
    step_text = cal_text = ""
    for x in range(len(ps_cal)):
        if "d" not in ps_cal[x]:
            step_text += str(ps_step[x])
        else:
            ps_total, ps_rolls = core.roll_dice(str(ps_cal[x]))
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

def cc_main(msg, bp_flag = None, bp_num = 0, bp_text =""):
    spell = msg.content.split(" ")
    cc_cmd = spell[0]
    prob = min(int(spell[1]),99)
    try:
        info = "：" + str(spell[2])
    except IndexError:
        info = ""  # if no info
    d_result, d_rolls = core.roll_dice("1d100")
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
    check_result, flag = core.coc_check(d_result, prob, cc_cmd)
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
            text2user = (f"#{x + 1} {dd_msg}{info}\n"
                        f"{step_text} = {cal_text}\n"
                        f"={total_result}\n")
        else:
            total, rolls = core.roll_dice(dd_msg)
            text2user = (f"#{x + 1} {dd_msg}{info}\n"
                        f"{rolls}\n"
                        f"={total}\n")
    return text2user

def sc_alg(flag, sc_suc, sc_fail, check_result):
    sc_fmla = sc_suc if flag == "≤" else sc_fail
    if check_result == "大失敗！":
        max_fmla = sc_fmla.lower().replace('d', '*') #replace d to * for cal
        deduct_t = deduct_r = eval(max_fmla)
        return f"最大值：{max_fmla}", deduct_t, deduct_r
    else:
        if 'd' in sc_fmla:
            try:
                parts = sc_fmla.lower().replace('+', 'd').split('d')
                num = int(parts[0])
                sides = int(parts[1])
                modi = int(parts[2]) if len(parts) > 2 else 0
                deduct_t, deduct_r = core.roll_dice(f"{num}d{sides}")
                return sc_fmla, deduct_t + modi, f"{deduct_r}+{modi}"
            except (ValueError, IndexError):
                pass
        else:
            deduct_t = deduct_r = eval(sc_fmla)
            return sc_fmla, deduct_t, deduct_r

def sc_main(msg):
    try:
        spell = msg.split(" ")
        prob = min(int(spell[0]), 99)
        sc_suc, sc_fail = spell[1].lower().split('/')
    except (IndexError, ValueError):
        return "格式錯誤！範例：.sc 50 1/1d6"
    sc_value, _ = core.roll_dice("1d100")
    check_result, flag = core.coc_check(sc_value, prob, "sc")
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
        total, rolls = core.roll_dice("3d6")
        f_rolls.append(str(rolls) + "×5")
        f_total.append(str(total * 5))
    for i in range(y):
        total, rolls = core.roll_dice("2d6")
        f_rolls.append("{" + str(rolls) + "+6}" + "×5")
        f_total.append(str((total + 6) * 5))
    for i in range(z):
        total, rolls = core.roll_dice("3d6")
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

@bot.command() #maunal
async def man(ctx):
    with open("manual.md", "r", encoding="utf-8") as f:
        man_content = f.read()
    await ctx.send(man_content)

@bot.command() #make KP
@commands.has_role("KP")
async def mkKP(ctx):
    kpndr.save_kp(ctx.guild.id, ctx.author.id)
    await ctx.send(f"暗骰指向已設置至 {ctx.author.mention}")

@bot.command() #remove KP
@commands.has_role("KP")
async def rmKP(ctx):
    kpndr.remove_kp(ctx.guild.id)
    await ctx.send("暗骰指向已取消")

@bot.command()
@commands.has_role("TRPG")
async def shKP(ctx):
    kps = kpndr.load_kps()
    kp_id = kps.get(str(ctx.guild.id))

    if kp_id is None:
        await ctx.send("目前此伺服器沒有設定 KP。")
    else:
        kp_user = bot.get_user(int(kp_id))
        if kp_user:
            await ctx.send(f"當前伺服器的暗骰已設定至：{kp_user.mention}")
        else:
            await ctx.send(f"當前伺服器的 KP ID 為：{kp_id}")

@bot.command() #get TRPG role
async def trpg(ctx):
    role = discord.utils.get(ctx.guild.roles, name="TRPG")
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"歡迎{ctx.author.mention}進入TRPG嘅世界")
    else:
        await ctx.send("伺服器上沒有TRPG身份組")

@bot.command() #remove TRPG role
async def ntrpg(ctx):
    role = discord.utils.get(ctx.guild.roles, name="TRPG")
    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(f"期待{ctx.author.mention}下次再玩TRPG")
    else:
        await ctx.send("伺服器上沒有TRPG身份組")

@bot.command() #dark roll
async def dr(ctx, mode: str, *, text):
    #s (self), k (KP), b (both)
    text2user = dr_proc(text)
    kps = kpndr.load_kps()
    kp_id = kps.get(str(ctx.guild.id))

    if mode in ['s', 'b']: #to User
        await ctx.author.send(f"{ctx.author.name}的暗骰：\n"
                              f"{text2user}")
    if mode in ['k', 'b'] and kp_id: #to KP
        KP = await bot.fetch_user(int(kp_id))
        await KP.send(f"{ctx.author.name}的暗骰：\n"
                           f"{text2user}")
    await ctx.send("暗骰已傳送至DM")

@bot.command() #cc benefit
async def ccb(ctx, b_num: int, prob: int, info=""):
    text2user = cc_main(MockMsg(f"cc {prob} {info}"), "b", b_num)
    await ctx.send(f"{ctx.author.mention}\n"
                   f"{text2user}")

@bot.command() #cc penalty
async def ccp(ctx, b_num: int, prob: int, info=""):
    text2user = cc_main(MockMsg(f"cc {prob} {info}"), "p", b_num)
    await ctx.send(f"{ctx.author.mention}\n"
                   f"{text2user}")

@bot.command() #choice
async def rand(ctx, *, text):
    sel = text.split(" ")
    code = random.randint(0, len(sel)-1)
    await ctx.send(f"{ctx.author.mention}\n"
                   f"1d{len(sel)} [{code+1}]\n"
                   f"隨機結果：{sel[code]}")

@bot.command() #san check
async def sc(ctx, *, text):
    text2user = sc_main(text)
    await ctx.send(f"{ctx.author.mention}\n"
                   f"{text2user}")

@bot.command() #skill upgrade
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

@bot.command() #cc7 build
async def cc7bd(ctx, text=""):
    text2user = bd7_main(text)
    await ctx.send(f"{ctx.author.mention}\n"
                   f"{text2user}")

@bot.command()
async def ccrt(ctx):
    case_code = random.randint(1, 10)
    text2user = san.ccrt_text(case_code)
    await ctx.send(f"{ctx.author.mention}\n"
                   f"#{case_code} "
                   f"{text2user}")

@bot.command()
async def ccsu(ctx):
    case_code = random.randint(1, 10)
    text2user = san.ccsu_text(case_code)
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

    #roll
    if message.content.startswith("dd"):
        msg = message
        text2user = dd_main(msg)
        await message.channel.send(f"{message.author.mention}\n"
                                   f"{text2user}")

    await bot.process_commands(message)

webserver.keep_alive()

bot.run(token, log_handler=handler, log_level=logging.DEBUG)