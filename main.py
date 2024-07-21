import re
import os
from datetime import datetime, timezone, timedelta
import discord
from discord import Option, Embed, Color, TextChannel
import google.generativeai as genai
from discord import Client, Intents, Embed
from discord.ext import commands, tasks
import json
import aiohttp
from itertools import cycle
from Def import history
from Def import gen_image
import logs
import json
import requests

log = {}  # 存放短期記憶用的字典
logs.datewrite("========================================")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

# 設定配置
with open('config.json', 'r', encoding='utf-8') as config_file:
    config_data = json.load(config_file)

bot_token = config_data.get('bot_token', 'YOUR_DEFAULT_BOT_TOKEN')

# 獲取狀態消息列表，如果未設置，則使用預設值
status_messages = config_data.get('status_messages', ['對話生成中', '我是google對話機器人', '正在聊天', '不要罵我uwu'])
status_cycle = cycle(status_messages)

@tasks.loop(seconds=10)  # 每隔10秒更換一次機器人個人狀態
async def change_status():
    await bot.change_presence(activity=discord.Game(next(status_cycle)))

# 讓機器人顯示狀態
@bot.event
async def on_ready():
    print(f'{bot.user} 已上線！')
    logs.datewrite(f'{bot.user} 已上線！')
    logs.datewrite("--------------------------")
    change_status.start()

@bot.event  # 如果有訊息發送就會觸發
async def on_message(msg):
    # 檢查訊息是否包含機器人的提及
    if bot.user.mentioned_in(msg):
        channel_id = str(msg.channel.id)  # 定義變數channel_id
        with open('channel.json', 'r', encoding='utf-8') as file:
            data = json.load(file)  # 開啟json檔
            channel_list = data.get("id", [])
        if channel_id not in channel_list and isinstance(msg.channel, discord.TextChannel):  # 如果頻道id不在json檔裡面且
            return
        if msg.attachments:  # 如果訊息中有檔案就執行下面
            for attachment in msg.attachments:
                if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):  # 檢測副檔名
                    async with aiohttp.ClientSession() as session:
                        async with session.get(attachment.url) as resp:  # 讀取圖片的url並將他用aiohttp函式庫轉換成數據
                            if resp.status != 200:
                                embed = discord.Embed(title="錯誤", description="圖片載入失敗", color=discord.Color.red())
                                await msg.reply(embed=embed)  # 如果圖片分析失敗就不執行後面
                                return
                            bot_msg = await msg.reply("正在分析圖片")
                            print(f"正在分析{msg.author.name}的圖片")
                            logs.datewrite(f"正在分析{msg.author.name}的圖片")

                            image_data = await resp.read()  # 定義image_data為aiohtp回應的數據
                            dc_msg = clean_discord_message(msg.content)  # 格式化訊息
                            response_text = await gen_image(image_data, dc_msg)  # 用gen_image函式來發送圖片數據跟文字給api
                            await split_and_send_messages(msg, bot_msg, response_text, 1700)  # 如果回應文字太長就拆成兩段
                            return

        # 如果訊息不包含附件，則執行以下程式
        if isinstance(msg.channel, discord.TextChannel):
            print(f"伺服器名稱:{msg.guild.name}")
            logs.datewrite(f"伺服器名稱:{msg.guild.name}")
        else:
            print(f"伺服器名稱:私訊")
            logs.datewrite(f"伺服器名稱:私訊")
        print(f"訊息ID: {msg.id}")
        logs.datewrite(f"訊息ID: {msg.id}")
        print(f"訊息內容: {msg.content}")
        logs.datewrite(f"訊息內容: {msg.content}")
        print(f"使用者ID: {msg.author.id}")
        logs.datewrite(f"使用者ID: {msg.author.id}")
        print(f"使用者名稱: {msg.author.name}")
        logs.datewrite(f"使用者名稱: {msg.author.name}")
        if isinstance(msg.channel, discord.TextChannel):
            print(f"頻道名稱: {msg.channel.name}")
            logs.datewrite(f"頻道名稱: {msg.channel.name}")
            print(f"頻道ID: {msg.channel.id}")
            logs.datewrite(f"頻道ID: {msg.channel.id}")

        dc_msg = clean_discord_message(msg.content)  # 將訊息內容放入clean_discord_message(下面會講),簡單來說就是更改訊息的格式,然後把回傳結果放入dc_msg變數
        dc_msg = "使用者說:" + dc_msg 
        update_message_history(msg.author.id, dc_msg)  # 將dc_msg(就是使用者發送的訊息)上傳到短期記憶

        if msg.author.id in log:
            reply_text = await history(get_formatted_message_history(msg.author.id))  # 將訊息發送者的id放入get_formatted_message_history函式,然後將得到的歷史資料放入history函式來得到api回應
        else:
            reply_text = await history(msg.content)  # 如果使用者沒有歷史紀錄就直接把訊息發給api

        await msg.reply(reply_text)  # 將回應回傳給使用者
        update_message_history(msg.author.id, reply_text)  # 將api的回應上傳到短期記憶

    await bot.process_commands(msg)

@bot.slash_command(name="ai對話狀態", description="選取頻道是否開啟AI對話")
@commands.has_permissions(administrator=True)
async def ai對話狀態(ctx, 開啟: Option(bool, description="True開啟, False關閉")):
    if isinstance(ctx.channel, discord.TextChannel):
        channel_id = str(ctx.channel.id)
        with open('channel.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        channel_list = data.get("id", [])
        
        if 開啟:
            if channel_id in channel_list:
                embed = discord.Embed(title="AI 聊天", description="頻道已開啟AI聊天", color=discord.Color.green())
            else:
                channel_list.append(channel_id)
                data["id"] = channel_list
                with open('channel.json', 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=2)
                embed = discord.Embed(title="AI 聊天", description="頻道開啟AI聊天", color=discord.Color.green())
        else:
            if channel_id in channel_list:
                channel_list.remove(channel_id)
                data["id"] = channel_list
                with open('channel.json', 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=2)
                embed = discord.Embed(title="AI 聊天", description="頻道關閉AI聊天", color=discord.Color.green())
            else:
                embed = discord.Embed(title="AI 聊天", description="頻道未開啟AI聊天", color=discord.Color.red())

        await ctx.respond(embed=embed)
    else:
        embed = discord.Embed(title="錯誤", description="請在伺服器中使用此指令", color=discord.Color.red())
        await ctx.respond(embed=embed)

@bot.slash_command(name="清空短期記憶", description="清空機器人對您的短期記憶")
async def reset(ctx):
    if ctx.author.id in log:
        del log[ctx.author.id]
        embed = discord.Embed(title="記憶已清空", description="您的短期記憶已清空", color=discord.Color.green())
        await ctx.respond(embed=embed, ephemeral=True)
        logs.datewrite("已清空機器人的短期記憶")
    else:
        embed = discord.Embed(title="錯誤", description="您並無儲存的短期記憶", color=discord.Color.red())
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(AICog(bot))

def update_message_history(user_id, text):  # 定義update_message_history函式
    if user_id in log:  # 如果user_id在字典裡面
        log[user_id].append(text)  # 就把text加入以user_id命名的鍵中
        if len(log[user_id]) > 15:  # 如果user_id裡面存的資料大於15筆(數字可以自己設定,不一定要15,這代表了他的短期記憶容量)
            log[user_id].pop(0)  # 就pop最早的一筆資料
    else:
        log[user_id] = [text]  # 如果user_id不在字典裡就創建一個,並把text放入

def clean_discord_message(input_string):  # 刪除 Discord 聊天訊息中位於 < 和 > 之間的文字(讓他能夠放入短期記憶並被ai讀懂)
    bracket_pattern = re.compile(r'<[^>]+>')
    cleaned_content = bracket_pattern.sub('', input_string)
    return cleaned_content  # 返回更改格式後的字串

def get_formatted_message_history(user_id):
    if user_id in log:  # 如果user_id有在log字典裏面
        return '\n\n'.join(log[user_id])  # 返回user_id裡面存放的內容

async def split_and_send_messages(msg, bot_msg, text, max_length):
    messages = []
    for i in range(0, len(text), max_length):
        sub_message = text[i:i + max_length]  # 如果訊息長度超過max_length就把他拆開
        messages.append(sub_message)
    for string in messages:
        await bot_msg.edit(content=string, embed=None)
        print(f"已分析完畢{msg.author.name}的圖片")
        logs.datewrite(f"已分析完畢{msg.author.name}的圖片")
        logs.datewrite(string)

bot.run(bot_token)
