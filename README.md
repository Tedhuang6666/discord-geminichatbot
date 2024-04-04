# discord-geminichatbot
一個參考他人程式所更改而成的python版本聊天機器人

旨在能讓沒有任何程式基礎的使用者創建自己的機器人，提升AI領域得普遍能見度與對程式興趣

---

### 聲明
此機器人程式部分參考自[yimang大大之github專案][1]

此機器人不含任何營利及私人用途，僅是希望推廣並降低AI相關學習門檻

若有bug或使用及設定上問題至Discord私訊Tedhuang6666，感謝您~

此非專業人士所撰寫，若有興趣深入研究更專業的程式可參考這兩個專案:

[木呱及nelsonGX所作之discord-gemini-ai][2]

[yiman及nelsonGX所作之discord-gemini-chat-bot][1]
 
  [1]: https://github.com/imyimang/discord-gemini-chat-bot        "discord-gemini-chat-bot"
  [2]: https://github.com/peter995peter/discord-gemini-ai  "discord-gemini-ai"

---

### 功能特色

* 連接語言模型:這是一個利用google開發的gemini模型並連結至discord機器人的聊天機器人

* 短期記憶:具有短期記憶功能的文字聊天（記憶句數上限可自訂，詳見「深入配置」）

* 圖片辨識:能夠進行粗略的圖片及gif辨識

* 私訊支援:能在私訊頻道中使用

* 日誌系統:獨特的日誌系統，並且依據日期編排，能讓開發者依據日誌修正機器人的回答

* 白名單系統:使用指令開啟該頻道的白名單

* 簡易的配置:透過配置文件進行簡易的配置，即使不熟悉程式也能輕鬆使用

這個程式是一個 Discord 聊天機器人，使用 Python 語言開發，利用 Discord.py 和其他相關庫來實現以上功能。

---

### 指令
✅openaichat➡️開啟此頻道的ai聊天

✅stopaichat➡️關閉此頻道的ai聊天(即使mention也是一樣)

✅openaichatserver➡️開啟整個dc討論區的ai聊天

✅reset➡️重製使用此指令用戶的短期記憶

(以上指令皆無權限限制，任何人都可以使用)

---

### 檔案結構
- main.py: 主程式檔案，包含了 Discord 聊天機器人的主要邏輯。
- Def.py: 將資料傳至gemini api來獲取回覆或分析圖片。
- logs.py: 記錄機器人運行日誌的模組。
- config.json: 存放配置項，如機器人的 token。
- channel.json: 存放開啟聊天功能的頻道列表。

---

### 注意事項
- 請務必妥善保管機器人的 token，避免洩露給他人。
- 請遵守 Discord 平台的使用規範，避免濫用機器人進行垃圾訊息、廣告等行為。

---

### 使用說明

*(詳細資訊請參閱wiki)*

1. 在 Discord 開發者平台建立一個機器人，並獲取 token。
2. 將 token 填入 `config.json` 檔案中的 `bot_token` 欄位。
3. 取得
3. 在 Discord 上部署機器人，並設置所需的權限。
4. 使用 `openaichat` 指令在特定頻道開啟聊天功能，使用 `stopaichat` 指令關閉。
5. 通過與機器人對話，享受智能聊天的樂趣！
