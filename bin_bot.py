import os
import telebot
import requests
from flask import Flask, request

# 你的Bot Token
BOT_TOKEN = "7619688289:AAHJ1fiBN5jGyKW8FI2xwpiLY3Xal1j16ak"
bot = telebot.TeleBot(BOT_TOKEN)

# Flask应用
app = Flask(__name__)

# 获取Render的环境变量（动态URL）
BASE_URL = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
WEBHOOK_URL = f"https://{BASE_URL}/webhook" if BASE_URL else None

# 设置Webhook
def set_webhook():
    if WEBHOOK_URL:
        bot.remove_webhook()
        bot.set_webhook(url=WEBHOOK_URL)
        print(f"Webhook已设置：{WEBHOOK_URL}")
    else:
        print("未检测到WEBHOOK URL，跳过设置Webhook！")

# 处理Webhook的POST请求
@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

# 处理/start命令
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello! Send me the first 6 digits of a BIN to get card details.")

# 处理BIN查询
@bot.message_handler(func=lambda message: True)
def get_bin_info(message):
    bin_number = message.text.strip()
    if len(bin_number) == 6 and bin_number.isdigit():
        response = requests.get(f"https://lookup.binlist.net/{bin_number}")
        if response.status_code == 200:
            data = response.json()
            card_info = f"""
            BIN: {bin_number}
            Card Brand: {data.get('scheme', 'N/A')}
            Card Type: {data.get('type', 'N/A')}
            Bank: {data.get('bank', {}).get('name', 'N/A')}
            Country: {data.get('country', {}).get('name', 'N/A')}
            """
            bot.reply_to(message, card_info)
        else:
            bot.reply_to(message, "Sorry, I couldn't fetch card details.")
    else:
        bot.reply_to(message, "Please send a valid 6-digit BIN.")

# 启动应用
if __name__ == "__main__":
    set_webhook()  # 部署时动态设置Webhook
    app.run(host="0.0.0.0", port=8080)
