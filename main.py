import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import random

import core
import kp
import build
import san
import webserver

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix = '.', intents = intents)

@bot.command() #maunal
async def man(ctx):
    with open("manual.md", "r", encoding="utf-8") as f:
        man_content = f.read()
    await ctx.send(man_content)

@bot.command() #dark roll
async def dr(ctx, mode: str, *, text):
    #s (self), k (KP), b (both)
    text2user = core.dr_proc(text)
    kps = kp.load_kps()
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
    text2user = core.cc_main(core.MockMsg(f"cc {prob} {info}"), "b", b_num)
    await ctx.send(f"{ctx.author.mention}\n"
                   f"{text2user}")

@bot.command() #cc penalty
async def ccp(ctx, b_num: int, prob: int, info=""):
    text2user = core.cc_main(core.MockMsg(f"cc {prob} {info}"), "p", b_num)
    await ctx.send(f"{ctx.author.mention}\n"
                   f"{text2user}")

@bot.command() #choice
async def rand(ctx, *, text):
    sel = text.split(" ")
    code = random.randint(0, len(sel)-1)
    await ctx.send(f"{ctx.author.mention}\n"
                   f"隨機 {text}\n"
                   f"結果：{sel[code]}")

@bot.command() #san check
async def sc(ctx, *, text):
    text2user = core.sc_main(text)
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
    text2user = build.bd7_main(text)
    await ctx.send(f"{ctx.author.mention}\n"
                   f"{text2user}")

@bot.command()
async def ccrt(ctx):
    case_code = random.randint(1, 10)
    text2user = san.ccrt_text(case_code)
    await ctx.send(f"{ctx.author.mention}\n"
                   f"#{case_code} {text2user}")

@bot.command()
async def ccsu(ctx):
    case_code = random.randint(1, 10)
    text2user = san.ccsu_text(case_code)
    await ctx.send(f"{ctx.author.mention}\n"
                   f"#{case_code} {text2user}")

@bot.command() #make KP
@commands.has_role("KP")
async def mkkp(ctx):
    kp.save_kp(ctx.guild.id, ctx.author.id)
    await ctx.send(f"暗骰指向已設置至 {ctx.author.mention}")

@bot.command() #remove KP
@commands.has_role("KP")
async def rmkp(ctx):
    kp.remove_kp(ctx.guild.id)
    await ctx.send("暗骰指向已取消")

@bot.command()
@commands.has_role("TRPG")
async def shkp(ctx):
    kps = kp.load_kps()
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

@shkp.error
async def TRPG_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send(f"{ctx.author.mention}你不是TRPG玩家!")

@mkkp.error
@rmkp.error
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
        text2user = core.cc_main(msg)
        await message.channel.send(f"{message.author.mention}\n"
                                   f"{text2user}")

    #roll
    if message.content.startswith("dd"):
        msg = message
        text2user = core.dd_main(msg)
        await message.channel.send(f"{message.author.mention}\n"
                                   f"{text2user}")

    await bot.process_commands(message)

webserver.keep_alive()

bot.run(token, log_handler=handler, log_level=logging.DEBUG)