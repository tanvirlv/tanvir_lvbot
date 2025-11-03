# -*- coding: utf-8 -*-
import os
import sys
import asyncio
import logging
from datetime import datetime
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import requests

# Configure encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Logging setup
logging.basicConfig(
    format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
    level=logging.INFO
)

# Get environment variables
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")

# Initialize Telethon with StringSession
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Free Fire Userbot is running!"

@app.route('/health')
def health():
    return {"status": "alive", "bot": "running"}

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def unix_to_date(timestamp):
    try:
        timestamp = int(timestamp)
        return datetime.fromtimestamp(timestamp).strftime('%d %B %Y, %I:%M %p')
    except:
        return str(timestamp)

def format_number(num):
    try:
        return "{:,}".format(int(num))
    except:
        return str(num)

def get_rank_tier(rank):
    if rank <= 100:
        return "Heroic"
    elif rank <= 500:
        return "Diamond"
    elif rank <= 1000:
        return "Platinum"
    elif rank <= 2000:
        return "Gold"
    else:
        return "Silver/Bronze"

def fetch_player_data(uid, server="bd"):
    try:
        url = "https://freefire-api-2-e4j5.onrender.com/get_player_personal_show?server={}&uid={}".format(server, uid)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error("API Error: {}".format(e))
        return None

def format_player_profile(data):
    try:
        basic = data.get("basicinfo", {})
        pet = data.get("petinfo", {})
        social = data.get("socialinfo", {})
        credit = data.get("creditscoreinfo", {})
        
        nickname = basic.get("nickname", "N/A")
        player_id = basic.get("accountid", "N/A")
        region = basic.get("region", "N/A")
        account_type = basic.get("accounttype", "N/A")
        level = basic.get("level", "N/A")
        exp = format_number(basic.get("exp", 0))
        likes = format_number(basic.get("liked", 0))
        created_at = unix_to_date(basic.get("createat", "N/A"))
        last_login = unix_to_date(basic.get("lastloginat", "N/A"))
        
        br_rank = basic.get("rank", "N/A")
        rank_points = format_number(basic.get("rankingpoints", 0))
        max_rank = basic.get("maxrank", "N/A")
        cs_rank = basic.get("csrank", "N/A")
        cs_points = basic.get("csrankingpoints", 0)
        hippo_rank = basic.get("hipporank", "N/A")
        
        if br_rank != "N/A":
            rank_tier = get_rank_tier(int(br_rank))
        else:
            rank_tier = "N/A"
        
        pet_name = pet.get("name", "N/A")
        pet_id = pet.get("id", "N/A")
        pet_level = pet.get("level", "N/A")
        pet_exp = format_number(pet.get("exp", 0))
        pet_skin = pet.get("skinid", "N/A")
        pet_skill = pet.get("selectedskillid", "N/A")
        
        signature = social.get("signature", "N/A")
        
        veteran_expire = basic.get("veteranexpiretime", "")
        if veteran_expire:
            veteran_date = unix_to_date(veteran_expire)
        else:
            veteran_date = "N/A"
        
        credit_score = credit.get("creditscore", "N/A")
        
        if region == "BD":
            region_display = "🇧🇩 Bangladesh"
        else:
            region_display = "🌍 " + str(region)
        
        if account_type == 1:
            acc_type = "Garena (1)"
        else:
            acc_type = "Guest (" + str(account_type) + ")"
        
        lines = []
        lines.append("```")
        lines.append("🎮 Free Fire Player Profile")
        lines.append("═══════════════════════════════")
        lines.append("")
        lines.append("👤 Nickname: " + str(nickname))
        lines.append("🆔 Player ID: " + str(player_id))
        lines.append("🌍 Region: " + region_display)
        lines.append("🧾 Account Type: " + acc_type)
        lines.append("🏅 Level: " + str(level))
        lines.append("✨ EXP: " + str(exp))
        lines.append("❤️ Likes: " + str(likes))
        lines.append("📅 Created On: 🗓️ " + str(created_at))
        lines.append("🔑 Last Login: ⏱️ " + str(last_login))
        lines.append("")
        lines.append("🏆 Rank Information")
        lines.append("═══════════════════════════════")
        lines.append("🎯 Battle Royale Rank: " + str(br_rank) + " 🏵️ (" + rank_tier + ")")
        lines.append("⭐ Ranking Points: " + str(rank_points))
        lines.append("🚀 Max Rank: " + str(max_rank))
        lines.append("⚔️ Clash Squad Rank: " + str(cs_rank))
        lines.append("🎯 CS Points: " + str(cs_points))
        lines.append("🦈 Hippo Rank: " + str(hippo_rank))
        lines.append("")
        lines.append("🐾 Pet Information")
        lines.append("═══════════════════════════════")
        lines.append("🐶 Pet Name: " + str(pet_name))
        lines.append("🆔 Pet ID: " + str(pet_id))
        lines.append("📈 Level: " + str(pet_level) + " — EXP: " + str(pet_exp))
        lines.append("🎨 Skin ID: " + str(pet_skin))
        lines.append("💥 Selected Skill ID: " + str(pet_skill))
        lines.append("")
        lines.append("✍️ Social Information")
        lines.append("═══════════════════════════════")
        lines.append("💬 Signature: \"" + str(signature) + "\"")
        lines.append("")
        lines.append("🛡️ Veteran Status")
        lines.append("═══════════════════════════════")
        lines.append("🎖️ Expires: 🗓️ " + str(veteran_date))
        lines.append("")
        lines.append("⭐ Credit Score")
        lines.append("═══════════════════════════════")
        lines.append("🏅 Score: " + str(credit_score) + "/100")
        lines.append("```")
        
        return "\n".join(lines)
        
    except Exception as e:
        logging.error("Format Error: {}".format(e))
        return "```\nError formatting data: {}\n```".format(str(e))

@client.on(events.NewMessage(outgoing=True, pattern=r'(?i)^\.Cid\s+(\d+)$'))
async def cid_command(event):
    try:
        uid = event.pattern_match.group(1)
        
        processing_msg = await event.edit("🔍 Fetching player details...")
        
        data = fetch_player_data(uid)
        
        if data is None:
            await processing_msg.edit("```\nError: Unable to fetch data from API.\n```")
            return
        
        if "error" in data or "basicinfo" not in data:
            await processing_msg.edit("```\nError: Player not found. UID: {}\n```".format(uid))
            return
        
        formatted_profile = format_player_profile(data)
        
        await processing_msg.edit(formatted_profile)
        
    except Exception as e:
        logging.error("Command Error: {}".format(e))
        await event.edit("```\nError: {}\n```".format(str(e)))

@client.on(events.NewMessage(outgoing=True, pattern=r'(?i)^\.ping$'))
async def ping_command(event):
    await event.edit("```\n🏓 Pong! Bot is alive!\n```")

@client.on(events.NewMessage(outgoing=True, pattern=r'(?i)^\.help$'))
async def help_command(event):
    help_lines = []
    help_lines.append("```")
    help_lines.append("🤖 Free Fire Userbot Commands")
    help_lines.append("═══════════════════════════════")
    help_lines.append("")
    help_lines.append(".Cid [UID]")
    help_lines.append("  → Get Free Fire player details")
    help_lines.append("  → Example: .Cid 2716319203")
    help_lines.append("")
    help_lines.append(".ping")
    help_lines.append("  → Check if bot is alive")
    help_lines.append("")
    help_lines.append(".help")
    help_lines.append("  → Show this help message")
    help_lines.append("```")
    await event.edit("\n".join(help_lines))

async def main():
    try:
        await client.start()
        
        me = await client.get_me()
        logging.info("Userbot started!")
        logging.info("User: {} (@{})".format(me.first_name, me.username))
        logging.info("ID: {}".format(me.id))
        logging.info("Ready! Use .Cid [UID]")
        
        await client.run_until_disconnected()
        
    except Exception as e:
        logging.error("Start Error: {}".format(e))
        sys.exit(1)

if __name__ == "__main__":
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    logging.info("Flask started")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped")
    except Exception as e:
        logging.error("Fatal: {}".format(e))
        sys.exit(1)
