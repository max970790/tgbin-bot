import telebot
import requests

# 替换为你的Telegram bot Token
BOT_TOKEN = "7619688289:AAHJ1fiBN5jGyKW8FI2xwpiLY3Xal1j16ak"
bot = telebot.TeleBot(BOT_TOKEN)

# 定义binlist.io的API
BINLIST_API_URL = "https://lookup.binlist.net/"

# 处理/start命令，发送欢迎消息
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello! Send me the first 6 digits of a BIN to get card details.")

# 处理用户发送的消息
@bot.message_handler(func=lambda message: True)
def get_card_info(message):
    bin_number = message.text.strip()
    
    # 检查用户输入是否为6位数字
    if len(bin_number) == 6 and bin_number.isdigit():
        response = requests.get(f"{BINLIST_API_URL}{bin_number}")
        
        if response.status_code == 200:
            data = response.json()
            # 从返回的JSON中获取卡片信息
            card_info = f"""
            BIN: {bin_number}
            Card Brand: {data.get('scheme', 'N/A')}
            Card Type: {data.get('type', 'N/A')}
            Card Level: {data.get('brand', 'N/A')}
            Bank Name: {data.get('bank', {}).get('name', 'N/A')}
            Bank Country: {data.get('country', {}).get('name', 'N/A')}
            """
            bot.reply_to(message, card_info)
        else:
            bot.reply_to(message, "Sorry, I couldn't fetch card details. Please try again later.")
    else:
        bot.reply_to(message, "Please send me a valid 6-digit BIN.")

# 启动Bot
bot.polling()
