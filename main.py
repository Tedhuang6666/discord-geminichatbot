import re
import os
from datetime import datetime,timezone,timedelta
import discord
import google.generativeai as genai
from discord.ext import commands, tasks
import json
import aiohttp
from itertools import cycle
from Def import history #從Def.py導入history函式
from Def import gen_image #導入gen_image函式
import datetime
import logs #導入自定義日誌系統(logs.py)
import json
import requests


logs.datewrite("========================================")

log = {} #創建一個名稱叫log的字典存放短期記憶

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all()) #設定discordbot，prefix是指令前綴，可以自己改

# 設定配置項
with open('config.json', 'r', encoding='utf-8') as config_file:
    config_data = json.load(config_file)

bot_token = config_data.get('bot_token', '你...不會覺得這個也有預設吧?')


# 獲取狀態消息列表，如果未設置，則使用預設值
status_messages = config_data.get('status_messages', ['對話生成中', '我是google對話機器人', '正在聊天', '不要罵我uwu'])
status_cycle = cycle(status_messages)

@tasks.loop(seconds=10)  # 每隔10秒更換一次機器人個人狀態
async def change_status():
    await bot.change_presence(activity=discord.Game(next(status_cycle)))

#讓機器人顯示狀態
@bot.event
async def on_ready():
    print(f'{bot.user} 已上線！')
    logs.datewrite(f'{bot.user} 已上線！')
    logs.datewrite("--------------------------")
    change_status.start() 

@bot.event  #如果有訊息發送就會觸發
async def on_message(msg):   #如果有訊息發送就會觸發

    if msg.author == bot.user:   #如果訊息發送者是自己就不再執行下面的程式
        return
    if isinstance(msg.channel, discord.TextChannel):   #如果訊息在文字頻道就執行下面
      can_send = msg.channel.permissions_for(msg.guild.me).send_messages   #can_send用來檢查頻道是否有發言權限
      if bool(can_send) != True:   #如果機器人沒有發言權限就不執行下面程式
          print("沒有權限在此頻道發言")
          logs.datewrite("錯誤L沒有權限在此頻道發言")
          return
    
    if msg.content.lower() == "stopaichat":   #如果訊息內容="stopaichat"就執行下面
        if isinstance(msg.channel, discord.TextChannel):
            channel_id = str(msg.channel.id)   #定義channel_id為發送訊息的頻道id
            with open('channel.json', 'r', encoding='utf-8') as file:   #打開json檔案
            
            #此處的json檔就是發送訊息的白名單

                data = json.load(file)   #定義data為json檔案裡面讀到的資料
            channel_list = data.get("id", [])   #定義channel_list為json裡面鍵值為"id"的資料,如果沒有這個資料就返回空的列表
            
            if str(msg.channel.id) in channel_list: #如果channel id在channel_list裡面
                channel_list.remove(channel_id)   #從json檔裡面移除頻道id
                await msg.reply("頻道關閉AI聊天")  #回傳訊息給使用者

            data["id"] = channel_list
            with open('channel.json', 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=2)   #儲存上面json檔變更的內容
            return 
        else:
            await msg.reply("請在伺服器中使用此指令")
            return


    if msg.content.lower() == "openaichat":  #如果訊息內容="openaichat"就執行下面
       if isinstance(msg.channel, discord.TextChannel):
        channel_id = str(msg.channel.id)  #定義channel_id變數為頻道id
        
        

        with open('channel.json', 'r', encoding='utf-8') as file:
            data = json.load(file)  #打開json檔
        channel_list = data.get("id", [])  #定義channel_list為json檔裡面的資料



        if str(msg.channel.id) in channel_list: #如果頻道id已經記錄在json檔案裡面的話就執行下面
            await msg.reply("頻道開啟AI聊天")
            return
        channel_list.append(channel_id)  #如果json裡面沒有此頻道id,就把此頻道id加入json檔
        data["id"] = channel_list
        with open('channel.json', 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=2)  #儲存變更
        await msg.reply("頻道開啟AI聊天")
        return
       else:
            await msg.reply("請在伺服器中使用此指令")
            return
       
    

    if msg.content.lower() == "openaichatserver":  #如果訊息內容="openaichatserver"就執行下面

    
        with open('channel.json', 'r', encoding='utf-8') as file:
            data = json.load(file)  # 讀取json檔
        channel_list = data.get("id", []) #定義channel_list為json裡面的資料


        if isinstance(msg.channel, discord.TextChannel):
            guild = msg.guild
            channel_list = data.get("id", [])
            for channel in guild.channels:
                if str(channel.id) not in channel_list:
                    channel_list.append(str(channel.id))  #將伺服器所有的頻道id輸入到json中

            with open('channel.json', 'w', encoding='utf-8') as json_file:
                json.dump({"id": channel_list}, json_file, indent=2)

            await msg.reply("已解鎖伺服器所有文字頻道")
            print(f"已解鎖 {msg.guild.name} 上所有文字頻道")
            logs.datewrite(f"已解鎖 {msg.guild.name} 上所有文字頻道")
            return
        else:
            await msg.reply("請在伺服器中使用此指令")
            return

    channel_id = str(msg.channel.id) #定義變數channel_id
    with open('channel.json', 'r', encoding='utf-8') as file:
        data = json.load(file)  #開啟json檔
    channel_list = data.get("id", [])
    if bot.user.mentioned_in(msg):
        if channel_id not in channel_list and isinstance(msg.channel, discord.TextChannel):  # 如果頻道id不在json檔裡面
            return  # 就不執行下面程式
    else:
        return

    if msg.content.lower() == "reset": #如果訊息內容="reset"
        if msg.author.id in log:
            del log[msg.author.id] #清空短期記憶
            await msg.reply("您的短期記憶已清空")
            logs.datewrite("已清空機器人的短期記憶")
           
        else:
            await msg.reply("並無儲存的短期記憶")
        return

    if msg.attachments: #如果訊息中有檔案就執行下面

        
        for attachment in msg.attachments: 
            
            if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']): #檢測副檔名
                async with aiohttp.ClientSession() as session:
                    async with session.get(attachment.url) as resp: #讀取圖片的url並用aiohttp函式庫轉換成數據
                        if resp.status != 200:
                            await msg.reply('圖片載入失敗') #如果圖片分析失敗就直接返回
                            return
                        bot_msg = await msg.reply("正在分析圖片")
                        print(f"正在分析{msg.author.name}的圖片")
                        logs.datewrite(f"正在分析{msg.author.name}的圖片")
                        
                        image_data = await resp.read()  #定義image_data為aiohtp回應的數據
                        dc_msg = clean_discord_message(msg.content) #格式化訊息
                        response_text = await gen_image(image_data, dc_msg) #用gen_image函式來發送圖片數據跟文字給api
                        await split_and_send_messages(msg, bot_msg, response_text, 1700) #如果回應文字太長就拆成兩段
                        return




    # print後台和日誌輸出訊息的詳細資料 可以刪
    #==========================================
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
 #==========================================

    dc_msg = clean_discord_message(msg.content) #將訊息內容放入clean_discord_message
    dc_msg = "使用者說:" + dc_msg 
    update_message_history(msg.author.id, dc_msg) #將dc_msg(使用者訊息)上傳到短期記憶

    if msg.author.id in log:
        reply_text = await history(get_formatted_message_history(msg.author.id)) #將訊息發送者的id放入get_formatted_message_history函式，然後將得到的歷史資料放入history函式來得到api回應
    else:
        reply_text = await history(msg.content)    #如果使用者沒有歷史紀錄就直接把訊息發給api
       
    await msg.reply(reply_text)  #將回應回傳給使用者
    update_message_history(msg.author.id, reply_text) #將api的回應上傳到短期記憶
    return

    await bot.process_commands(msg)

      
def update_message_history(user_id, text): #定義update_message_history函式
    if user_id in log:  #如果user_id在字典裡面
        log[user_id].append(text)   #就把text加入以user_id命名的鍵中
        if len(log[user_id]) > 15: #如果user_id裡面存的資料大於15筆(數字可以自己設定,不一定要15,這代表了他的短期記憶容量)
            log[user_id].pop(0) #就pop(移除)最早的一筆資料
    else:
        log[user_id] = [text] #如果user_id不在字典裡就創建一個,並把對話放入

def clean_discord_message(input_string): #刪除 Discord 聊天訊息中位於 < 和 > 之間的文字(讓他能夠放入短期記憶並被ai讀懂)
    bracket_pattern = re.compile(r'<[^>]+>')
    cleaned_content = bracket_pattern.sub('', input_string)
    return cleaned_content  #返回更改格式後的字串
    
def get_formatted_message_history(user_id):
    if user_id in log: #如果user_id有在log字典裏面
        return '\n\n'.join(log[user_id]) #返回user_id裡面存放的內容


async def split_and_send_messages(msg, bot_msg, text, max_length):
    messages = []
    for i in range(0, len(text), max_length):
        sub_message = text[i:i+max_length]  #如果訊息長度超過max_length就把他拆開
        messages.append(sub_message)
    for string in messages:
        await bot_msg.edit(content = string)
        print(f"已分析完畢{msg.author.name}的圖片")
        logs.datewrite(f"已分析完畢{msg.author.name}的圖片")
        logs.datewrite(string)
    
bot.run(bot_token)
