import os
import time
import logging
import pyshorteners
from selenium import webdriver
from functools import partial
from asyncio import get_running_loop
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserNotParticipant, UserBannedInChannel

bot = Client(
    "Tiktok Downloader Bot",
    bot_token = "6298604288:AAHWGFEeeVebX4sFH08OdcPzq4buJ9sH728",
    api_id = 2780061,
    api_hash = "f4f1200cee4788d9d7c98d7993f8a1dd"
)

UPDATES_CHANNEL = "JaguarBots"

downloader = "https://ttsave.app/"

START_TEXT = """
Hi **{}** 👋

Send me a tiktok link and I'll upload it to Telegram in HD & generate direct download link instantly (without watermark)

Follow dev on github [@ImJanindu](https://github.com/ImJanindu)
"""

START_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("📨 Channel", url="https://t.me/JaguarBots"),
            InlineKeyboardButton("🧑‍💻 Dev", url="https://t.me/About_Janindu")
        ]
    ]
)

chrome_options = Options()
chrome_options.binary_location = "/usr/bin/google-chrome-stable"
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")


@bot.on_message(filters.command("start") & filters.private)
async def start(_, message):
    msg = START_TEXT.format(message.from_user.mention)
    await message.reply_text(text = msg,
                             reply_markup = START_BUTTONS,
                             disable_web_page_preview=True, quote=True)


def download_vid(link, m, chat_id):
    try:
        browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
        #browser = webdriver.Chrome(executable_path="/app/.chromedriver/bin/chromedriver", chrome_options=chrome_options)       
        browser.get(downloader)

        time.sleep(1)

        inputt = browser.find_element(By.ID, 'input-query')
        inputt.send_keys(link)
        btnck = browser.find_element(By.ID, 'btn-download')
        btnck.click()

        WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.ID, "button-download-ready")))

        vid_link = browser.find_element(By.XPATH, '//*[@id="button-download-ready"]/a[1]').get_attribute('href')

        time.sleep(1)
        s = pyshorteners.Shortener() 
        shortened_url = s.dagd.short(vid_link)
        text = browser.find_element(By.XPATH, '//*[@id="result-container"]/div/p[1]').text
        button = [[InlineKeyboardButton("📥 Download Here 📥", url=shortened_url)]]
        markup = InlineKeyboardMarkup(button)
        m.edit("`📤 Uploading...`")
        bot.send_video(chat_id, vid_link, caption=f"**{text}** \n\n@JaguarBots", reply_markup=markup)
        m.delete()
        return
    except Exception as e:
        print(str(e))
        return m.edit("`Error 🤷‍♂️`")
    
      
@bot.on_message(filters.regex(pattern="http") & filters.private)
async def tiktok_down(_, message):
    if UPDATES_CHANNEL is not None:
        try:
            user = await _.get_chat_member(UPDATES_CHANNEL, message.from_user.id)
            if user.status == "kicked":
                return await message.reply_text("You are banned!", quote=True)
        except UserNotParticipant:
            return await message.reply_text("""You need to join @JaguarBots in order to use this bot. Being a part of this channel keeps you informed of the latest updates.
            
So please join channel and enjoy bot 😇""",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("📨 Join @JaguarBots", url=f"https://t.me/{UPDATES_CHANNEL}")
                        ]
                    ]
                ), quote=True
            )
        except Exception:
            return await message.reply_text("Something Wrong. Contact @JaguarBotsChat 👍", quote=True)
        
    if not "tiktok.com" in message.text:
        return await message.reply_text("`WTF is that URL?`", quote=True)
    
    link = message.text
    chat_id = message.chat.id
    m = await message.reply_text("`📥 Downloading...`", quote=True)
    loop = get_running_loop()
    
    loop.run_in_executor(None, partial(download_vid, link, m, chat_id))
    
    
bot.run()
