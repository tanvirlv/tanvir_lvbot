# -*- coding: utf-8 -*-
import os
import sys
import asyncio
import logging
from datetime import datetime
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events
import requests

# Set stdout encoding to UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Set up logging
logging.basicConfig(
    format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
    level=logging.INFO
)

# Environment variables
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")

# Initialize Telethon client
client = TelegramClient(SESSION_STRING, API_ID, API_HASH)

# Flask app for keeping service alive
app = Flask(__name__)

@app.route('/')
def home():
    return "Free Fire Userbot is running!"

@app.route('/health')
def health():
    return {"status": "alive", "bot": "running"}

def run_flask():
    """Run Flask in a separate thread"""
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def unix_to_date(timestamp):
    """Convert Unix timestamp to readable date"""
    try:
        timestamp = int(timestamp)
        return datetime.fromtimestamp(timestamp).strftime('%d %B %Y, %I:%M %p')
    except:
        return str(timestamp)

def format_number(num):
    """Format number with commas"""
    try:
        return "{:,}".format(int(num))
    except:
        return str(num)

def get_rank_tier(rank):
    """Get rank tier based on rank number"""
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
    """Fetch player data from API"""
    try:
        url = "https://freefire-api-2-e4j5.onrender.com/get_player_personal_show?server={}&uid={}".format(server, uid)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error("API Error: {}".format(e))
        return None
    except Exception as e:
        logging.error("Error: {}".format(e))
        return None

def format_player_profile(data):
    """Format player profile with emojis"""
    try:
        basic = data.get("basicinfo", {})
        profile = data.get("profileinfo", {})
        pet = data.get("petinfo", {})
        social = data.get("socialinfo", {})
        credit = data.get("creditscoreinfo", {})
        
        # Basic Information
        nickname = basic.get("nickname", "N/A")
        player_id = basic.get("accountid", "N/A")
        region = basic.get("region", "N/A")
        account_type = basic.get("accounttype", "N/A")
        level = basic.get("level", "N/A")
        exp = format_number(basic.get("exp", 0))
        likes = format_number(basic.get("liked", 0))
        created_at = unix_to_date(basic.get("createat", "N/A"))
        last_login = unix_to_date(basic.get("lastloginat", "N/A"))
        
        # Rank Information
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
        
        # Pet Information
        pet_name = pet.get("name", "N/A")
        pet_id = pet.get("id", "N/A")
        pet_level = pet.get("level", "N/A")
        pet_exp = format_number(pet.get("exp", 0))
        pet_skin = pet.get("skinid", "N/A")
        pet_skill = pet.get("selectedskillid", "N/A")
        
        # Social Information
        signature = social.get("signature", "N/A")
        
        # Veteran Status
        veteran_expire = basic.get("veteranexpiretime", "")
        if veteran_expire:
            veteran_date = unix_to_date(veteran_expire)
        else:
            veteran_date = "N/A"
        
        # Credit Score
        credit_score = credit.get("creditscore", "N/A")
        
        # Region Flag
        if region == "BD":
            region_flag = "🇧🇩"
            region_name = "Bangladesh"
        else:
            region_flag = "🌍"
            region_name = region
        
        # Account Type Name
        if account_type == 1:
            acc_type_name = "Garena"
        else:
            acc_type_name = "Guest"
        
        # Build message parts
        parts = []
        parts.append("```")
        parts.append("🎮 Free Fire Player Profile")
        parts.append("═══════════════════════════════")
        parts.append("")
        parts.append("👤 Nickname: " + str(nickname))
        parts.append("🆔 Player ID: " + str(player_id))
        parts.append("🌍 Region: " + region_flag + " " + str(region_name))
        parts.append("🧾 Account Type: " + acc_type_name + " (" + str(account_type) + ")")
        parts.append("🏅 Level: " + str(level))
        parts.append("✨ EXP: " + str(exp))
        parts.append("❤️ Likes: " + str(likes))
        parts.append("📅 Created On: 🗓️ " + str(created_at))
        parts.append("🔑 Last Login: ⏱️ " + str(last_login))
        parts.append("")
        parts.append("🏆 Rank Information")
        parts.append("═══════════════════════════════")
        parts.append("🎯 Battle Royale Rank: " + str(br_rank) + " 🏵️ (" + rank_tier + ")")
        parts.append("⭐ Ranking Points: " + str(rank_points))
        parts.append("🚀 Max Rank: " + str(max_rank))
        parts.append("⚔️ Clash Squad Rank: " + str(cs_rank))
        parts.append("🎯 CS Points: " + str(cs_points))
        parts.append("🦈 Hippo Rank: " + str(hippo_rank))
        parts.append("")
        parts.append("🐾 Pet Information")
        parts.append("═══════════════════════════════")
        parts.append("🐶 Pet Name: " + str(pet_name))
        parts.append("🆔 Pet ID: " + str(pet_id))
        parts.append("📈 Level: " + str(pet_level) + " — EXP: " + str(pet_exp))
        parts.append("🎨 Skin ID: " + str(pet_skin))
        parts.append("💥 Selected Skill ID: " + str(pet_skill))
        parts.append("")
        parts.append("✍️ Social Information")
        parts.append("═══════════════════════════════")
        parts.append("💬 Signature: \"" + str(signature) + "\"")
        parts.append("")
        parts.append("🛡️ Veteran Status")
        parts.append("═══════════════════════════════")
        parts.append("🎖️ Expires: 🗓️ " + str(veteran_date))
        parts.append("")
        parts.append("⭐ Credit Score")
        parts.append("═══════════════════════════════")
        parts.append("🏅 Score: " + str(credit_score) + "/100")
        parts.append("```")
        
        # Join all parts
        message = "\n".join(parts)
        
        return message
        
    except Exception as e:
        logging.error("Formatting Error: {}".format(e))
        return "```\n❌ Error formatting player data: {}\n```".format(str(e))

@client.on(events.NewMessage(outgoing=True, pattern=r'(?i)^\.Cid\s+(\d+)$'))
async def cid_command(event):
    """Handle .Cid command"""
    try:
        # Extract UID from command
        uid = event.pattern_match.group(1)
        
        # Send processing message
        processing_msg = await event.edit("🔍 Fetching player details...")
        
        # Fetch data from API
        data = fetch_player_data(uid)
        
        if data is None:
            await processing_msg.edit("```\n❌ Error: Unable to fetch data from API. Please try again later.\n```")
            return
        
        # Check if data contains error
        if "error" in data or "basicinfo" not in data:
            await processing_msg.edit("```\n❌ Error: Player not found or invalid UID: {}\n```".format(uid))
            return
        
        # Format the profile
        formatted_profile = format_player_profile(data)
        
        # Send the formatted profile
        await processing_msg.edit(formatted_profile)
        
    except Exception as e:
        logging.error("Command Error: {}".format(e))
        await event.edit("```\n❌ Error: {}\n```".format(str(e)))

@client.on(events.NewMessage(outgoing=True, pattern=r'(?i)^\.ping$'))
async def ping_command(event):
    """Test command to check if bot is working"""
    await event.edit("```\n🏓 Pong! Bot is alive!\n```")

@client.on(events.NewMessage(outgoing=True, pattern=r'(?i)^\.help$'))
async def help_command(event):
    """Help command"""
    help_text = "```\n"
    help_text += "🤖 Free Fire Userbot Commands\n"
    help_text += "═══════════════════════════════\n\n"
    help_text += ".Cid [UID]\n"
    help_text += "  → Get Free Fire player details\n"
    help_text += "  → Example: .Cid 2716319203\n\n"
    help_text += ".ping\n"
    help_text += "  → Check if bot is alive\n\n"
    help_text += ".help\n"
    help_text += "  → Show this help message\n"
    help_text += "```"
    await event.edit(help_text)

async def main():
    """Main function to start the bot"""
    try:
        # Start the client
        await client.start()
        
        me = await client.get_me()
        logging.info("Userbot started successfully!")
        logging.info("Logged in as: {} (@{})".format(me.first_name, me.username))
        logging.info("User ID: {}".format(me.id))
        logging.info("Free Fire Userbot is ready!")
        logging.info("Use .Cid [UID] to get player details")
        
        # Keep the client running
        await client.run_until_disconnected()
        
    except Exception as e:
        logging.error("Error starting bot: {}".format(e))
        sys.exit(1)

if __name__ == "__main__":
    # Start Flask in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    logging.info("Flask server started")
    
    # Start the Telegram client
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
    except Exception as e:
        logging.error("Fatal error: {}".format(e))
        sys.exit(1)🧾 Account Type: {'Garena' if basic.get('accounttype') == 1 else 'Guest'} ({basic.get('accounttype', 'N/A')})
🏅 Level: {basic.get('level', 'N/A')}
✨ EXP: {format_number(basic.get('exp', 0))}
❤️ Likes: {format_number(basic.get('liked', 0))}
📅 Created On: {unix_to_date(basic.get('createat', 0))}
🔑 Last Login: {unix_to_date(basic.get('lastloginat', 0))}

🏆 Rank Information
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Battle Royale Rank: {basic.get('rank', 'N/A')} 🏵️
⭐ Ranking Points: {format_number(basic.get('rankingpoints', 0))}
🚀 Max Rank: {basic.get('maxrank', 'N/A')}
⚔️ Clash Squad Rank: {basic.get('csrank', 'N/A')}
🎯 CS Points: {basic.get('csrankingpoints', 'N/A')}
🏆 CS Max Rank: {basic.get('csmaxrank', 'N/A')}
🦈 Hippo Rank: {basic.get('hipporank', 'N/A')}
💎 Hippo Points: {basic.get('hipporankingpoints', 'N/A')}
"""

        # Pet information
        if pet:
            message += f"""
🐾 Pet Information
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐶 Pet Name: {pet.get('name', 'N/A')}
🆔 Pet ID: {pet.get('id', 'N/A')}
📈 Level: {pet.get('level', 'N/A')} — EXP: {format_number(pet.get('exp', 0))}
🎨 Skin ID: {pet.get('skinid', 'N/A')}
💥 Selected Skill ID: {pet.get('selectedskillid', 'N/A')}
"""

        # Social & Additional Info
        signature = social.get('signature', 'Free Fire! Battle in Style!')
        message += f"""
✍️ Signature
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 "{signature}"
"""

        # Veteran Status
        if basic.get('veteranexpiretime'):
            message += f"""
🛡️ Veteran Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎖️ Expires: {unix_to_date(basic.get('veteranexpiretime'))}
"""

        # Credit Score
        if credit:
            message += f"""
💳 Credit Score
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⭐ Score: {credit.get('creditscore', 'N/A')}/100
"""

        # Version & Badge
        message += f"""
📱 Additional Info
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎮 Release Version: {basic.get('releaseversion', 'N/A')}
🏅 Badge Count: {basic.get('badgecnt', 0)}
🎖️ Badge ID: {basic.get('badgeid', 'N/A')}
🎪 Season ID: {basic.get('seasonid', 'N/A')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```"""
        
        return message
    except Exception as e:
        logging.error(f"Formatting Error: {e}")
        return f"```\n❌ Error formatting player data\n```"

@client.on(events.NewMessage(pattern=r'(?i)^[./!]cid\s+(\d+)(?:\s+(\w+))?'))
async def check_id_handler(event):
    """Handler for .cid command"""
    try:
        # Extract UID and server from command
        match = event.pattern_match
        uid = match.group(1)
        server = match.group(2) if match.group(2) else 'bd'
        
        # Send processing message
        processing_msg = await event.reply("🔍 Fetching player details... Please wait...")
        
        # Fetch data from API
        data = await fetch_player_data(uid, server.lower())
        
        if data and 'basicinfo' in data:
            # Format and send the result
            formatted_data = format_player_info(data)
            await processing_msg.edit(formatted_data)
        else:
            await processing_msg.edit(
                f"```\n❌ Player not found!\n\n"
                f"🆔 UID: {uid}\n"
                f"🌍 Server: {server.upper()}\n\n"
                f"Please check the UID and server.\n```"
            )
    
    except Exception as e:
        logging.error(f"Command Error: {e}")
        await event.reply(f"```\n❌ An error occurred:\n{str(e)}\n```")

@client.on(events.NewMessage(pattern=r'(?i)^[./!]help'))
async def help_handler(event):
    """Handler for .help command"""
    help_text = """```
🤖 Free Fire Player Info Bot

📌 Commands:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔹 .cid <UID> [server]
   Get player details by UID
   
   Example:
   .cid 2716319203
   .cid 2716319203 bd
   .cid 2716319203 in

🔹 .help
   Show this help message

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌍 Available Servers:
BD, IN, PK, US, BR, ID, TH, etc.

Default server: BD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```"""
    await event.reply(help_text)

async def main():
    """Main function to start the bot"""
    logging.info("🚀 Starting Free Fire Userbot...")
    
    # Start the client
    await client.start(session=SESSION_STRING)
    
    # Get current user info
    me = await client.get_me()
    logging.info(f"✅ Userbot started as: {me.first_name} (@{me.username})")
    logging.info("📝 Bot is ready! Use .cid <UID> to check player details")
    
    # Keep the bot running
    await client.run_until_disconnected()

if __name__ == '__main__':
    # Start Flask in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    logging.info(f"🌐 Flask server started on port {PORT}")
    
    # Start the Telegram bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("👋 Bot stopped by user")
    except Exception as e:
        logging.error(f"❌ Fatal error: {e}")        lines.append(f"\U0001F680 Max Rank: {basic.get('maxrank', 'N/A')}")
        lines.append(f"\u2694\uFE0F Clash Squad Rank: {basic.get('csrank', 'N/A')}")
        lines.append(f"\U0001F3AF CS Points: {basic.get('csrankingpoints', 'N/A')}")
        lines.append(f"\U0001F988 Hippo Rank: {basic.get('hipporank', 'N/A')}")
        lines.append(f"\U0001F396\uFE0F Hippo Points: {basic.get('hipporankingpoints', 'N/A')}")
        
        if pet:
            lines.append("")
            lines.append("\U0001F43E Pet Information")
            lines.append(f"\U0001F436 Pet Name: {pet.get('name', 'N/A')}")
            lines.append(f"\U0001F194 Pet ID: {pet.get('id', 'N/A')}")
            lines.append(f"\U0001F4C8 Level: {pet.get('level', 'N/A')} \u2014 EXP: {format_number(pet.get('exp', 0))}")
            lines.append(f"\U0001F3A8 Skin ID: {pet.get('skinid', 'N/A')}")
            lines.append(f"\U0001F4A5 Selected Skill ID: {pet.get('selectedskillid', 'N/A')}")
        
        signature = social.get('signature', '')
        if signature and signature != "Free Fire! Battle in Style!":
            lines.append("")
            lines.append(f"\u270D\uFE0F Signature: \U0001F4AC \"{signature}\"")
        
        veteran_expire = basic.get('veteranexpiretime')
        if veteran_expire:
            lines.append("")
            lines.append("\U0001F6E1\uFE0F Veteran Status")
            lines.append(f"\U0001F396\uFE0F Expires: \U0001F5D3\uFE0F {unix_to_date(veteran_expire)}")
        
        if credit.get('creditscore'):
            lines.append("")
            lines.append(f"\U0001F4B3 Credit Score: {credit.get('creditscore', 'N/A')}/100")
        
        lines.append("```")
        return "\n".join(lines)
    except Exception as e:
        return f"```\n\u274C Error: {str(e)}\n```"

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.cid (\d+)$'))
async def handle_cid_command(event):
    try:
        uid = event.pattern_match.group(1)
        status_msg = await event.reply("\U0001F50D Fetching player data...")
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, fetch_player_data, uid)
        if data and data.get('basicinfo'):
            profile_message = format_player_profile(data)
            await status_msg.edit(profile_message)
        else:
            await status_msg.edit("```\n\u274C Player not found or API error occurred.\n```")
    except Exception as e:
        await event.reply(f"```\n\u274C Error: {str(e)}\n```")

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.help$'))
async def help_command(event):
    lines = []
    lines.append("```")
    lines.append("\U0001F3AE Free Fire Player Info Bot")
    lines.append("")
    lines.append("Commands:")
    lines.append(".cid <uid> - Get player details")
    lines.append(".help - Show this help message")
    lines.append("")
    lines.append("Example:")
    lines.append(".cid 2716319203")
    lines.append("```")
    await event.reply("\n".join(lines))

async def main():
    try:
        print("Starting Free Fire Userbot...")
        await client.connect()
        if not await client.is_user_authorized():
            print("Session string is invalid!")
            return
        me = await client.get_me()
        print(f"Logged in as: {me.first_name}")
        print("Userbot is running!")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    print("Flask server started")
    try:
        client.loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Userbot stopped!")        
        message += "\U0001F3C6 Rank Information\n"
        message += f"\U0001F3AF Battle Royale Rank: {basic.get('rank', 'N/A')} \U0001F3F5\uFE0F\n"
        message += f"\u2B50 Ranking Points: {format_number(basic.get('rankingpoints', 0))}\n"
        message += f"\U0001F680 Max Rank: {basic.get('maxrank', 'N/A')}\n"
        message += f"\u2694\uFE0F Clash Squad Rank: {basic.get('csrank', 'N/A')}\n"
        message += f"\U0001F3AF CS Points: {basic.get('csrankingpoints', 'N/A')}\n"
        message += f"\U0001F988 Hippo Rank: {basic.get('hipporank', 'N/A')}\n"
        message += f"\U0001F396\uFE0F Hippo Points: {basic.get('hipporankingpoints', 'N/A')}\n"

        if pet:
            message += "\n\U0001F43E Pet Information\n"
            message += f"\U0001F436 Pet Name: {pet.get('name', 'N/A')}\n"
            message += f"\U0001F194 Pet ID: {pet.get('id', 'N/A')}\n"
            message += f"\U0001F4C8 Level: {pet.get('level', 'N/A')} \u2014 EXP: {format_number(pet.get('exp', 0))}\n"
            message += f"\U0001F3A8 Skin ID: {pet.get('skinid', 'N/A')}\n"
            message += f"\U0001F4A5 Selected Skill ID: {pet.get('selectedskillid', 'N/A')}\n"

        signature = social.get('signature', '')
        if signature and signature != "Free Fire! Battle in Style!":
            message += f"\n\u270D\uFE0F Signature: \U0001F4AC \"{signature}\"\n"
        
        veteran_expire = basic.get('veteranexpiretime')
        if veteran_expire:
            message += "\n\U0001F6E1\uFE0F Veteran Status\n"
            message += f"\U0001F396\uFE0F Expires: \U0001F5D3\uFE0F {unix_to_date(veteran_expire)}\n"

        if credit.get('creditscore'):
            message += f"\n\U0001F4B3 Credit Score: {credit.get('creditscore', 'N/A')}/100\n"

        message += "```"
        return message
        
    except Exception as e:
        return f"```\n\u274C Error formatting player data: {str(e)}\n```"

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.cid (\d+)$'))
async def handle_cid_command(event):
    try:
        uid = event.pattern_match.group(1)
        
        status_msg = await event.reply("\U0001F50D Fetching player data...")
        
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, fetch_player_data, uid)
        
        if data and data.get('basicinfo'):
            profile_message = format_player_profile(data)
            await status_msg.edit(profile_message)
        else:
            await status_msg.edit("```\n\u274C Player not found or API error occurred.\nPlease check the UID and try again.\n```")
            
    except Exception as e:
        await event.reply(f"```\n\u274C Error: {str(e)}\n```")

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.help$'))
async def help_command(event):
    help_text = "```\n"
    help_text += "\U0001F3AE Free Fire Player Info Bot\n\n"
    help_text += "Commands:\n"
    help_text += ".cid <uid> - Get player details\n"
    help_text += ".help - Show this help message\n\n"
    help_text += "Example:\n"
    help_text += ".cid 2716319203\n"
    help_text += "```"
    await event.reply(help_text)

async def main():
    try:
        print("Starting Free Fire Userbot...")
        print("Connecting to Telegram...")
        
        await client.connect()
        
        if not await client.is_user_authorized():
            print("Session string is invalid or expired!")
            print("Please generate a new session string.")
            return
        
        me = await client.get_me()
        print(f"Logged in as: {me.first_name} (@{me.username})")
        print("Userbot is running! Use .cid <uid> to fetch player info")
        
        await client.run_until_disconnected()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    print("Flask server started")
    
    try:
        client.loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\nUserbot stopped!") Region: {get_region_flag(basic.get('region', 'N/A'))}
🧾 Account Type: Garena ({basic.get('accounttype', 'N/A')})
🏅 Level: {basic.get('level', 'N/A')}
✨ EXP: {format_number(basic.get('exp', 0))}
❤️ Likes: {format_number(basic.get('liked', 0))}
📅 Created On: 🗓️ {unix_to_date(basic.get('createat', 'N/A'))}
🔑 Last Login: ⏱️ {unix_to_date(basic.get('lastloginat', 'N/A'))}

🏆 Rank Information
🎯 Battle Royale Rank: {basic.get('rank', 'N/A')} 🏵️
⭐ Ranking Points: {format_number(basic.get('rankingpoints', 0))}
🚀 Max Rank: {basic.get('maxrank', 'N/A')}
⚔️ Clash Squad Rank: {basic.get('csrank', 'N/A')}
🎯 CS Points: {basic.get('csrankingpoints', 'N/A')}
🦈 Hippo Rank: {basic.get('hipporank', 'N/A')}
🎖️ Hippo Points: {basic.get('hipporankingpoints', 'N/A')}
"""

        # Add pet information if available
        if pet:
            message += f"""
🐾 Pet Information
🐶 Pet Name: {pet.get('name', 'N/A')}
🆔 Pet ID: {pet.get('id', 'N/A')}
📈 Level: {pet.get('level', 'N/A')} — EXP: {format_number(pet.get('exp', 0))}
🎨 Skin ID: {pet.get('skinid', 'N/A')}
💥 Selected Skill ID: {pet.get('selectedskillid', 'N/A')}
"""

        # Add signature if available
        signature = social.get('signature', '')
        if signature and signature != "Free Fire! Battle in Style!":
            message += f"""
✍️ Signature: 💬 "{signature}"
"""
        
        # Add veteran status if available
        veteran_expire = basic.get('veteranexpiretime')
        if veteran_expire:
            message += f"""
🛡️ Veteran Status
🎖️ Expires: 🗓️ {unix_to_date(veteran_expire)}
"""

        # Add credit score
        if credit.get('creditscore'):
            message += f"""
💳 Credit Score: {credit.get('creditscore', 'N/A')}/100
"""

        message += "```"
        return message
        
    except Exception as e:
        return f"```\n❌ Error formatting player data: {str(e)}\n```"

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.cid (\d+)$'))
async def handle_cid_command(event):
    """Handle .cid command"""
    try:
        uid = event.pattern_match.group(1)
        
        # Send processing message
        status_msg = await event.reply("🔍 Fetching player data...")
        
        # Fetch player data using requests (sync)
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, fetch_player_data, uid)
        
        if data and data.get('basicinfo'):
            # Format and send the profile
            profile_message = format_player_profile(data)
            await status_msg.edit(profile_message)
        else:
            await status_msg.edit("```\n❌ Player not found or API error occurred.\nPlease check the UID and try again.\n```")
            
    except Exception as e:
        await event.reply(f"```\n❌ Error: {str(e)}\n```")

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.help$'))
async def help_command(event):
    """Help command"""
    help_text = """```
🎮 Free Fire Player Info Bot

Commands:
.cid <uid> - Get player details
.help - Show this help message

Example:
.cid 2716319203
```"""
    await event.reply(help_text)

async def main():
    """Main function to start the bot"""
    try:
        print("Starting Free Fire Userbot...")
        print("Connecting to Telegram...")
        
        # Connect without start() to avoid phone prompt
        await client.connect()
        
        # Check if authorized
        if not await client.is_user_authorized():
            print("❌ Session string is invalid or expired!")
            print("Please generate a new session string.")
            return
        
        # Get current user info
        me = await client.get_me()
        print(f"✅ Logged in as: {me.first_name} (@{me.username})")
        print("✅ Userbot is running! Use .cid <uid> to fetch player info")
        
        await client.run_until_disconnected()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    # Start Flask in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    print("✅ Flask server started")
    
    # Start Telegram client
    try:
        client.loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\n❌ Userbot stopped!")⚔️ Clash Squad Rank: {basic.get('csrank', 'N/A')}
🎯 CS Points: {basic.get('csrankingpoints', 'N/A')}
🦈 Hippo Rank: {basic.get('hipporank', 'N/A')}
🎖️ Hippo Points: {basic.get('hipporankingpoints', 'N/A')}
"""

        # Add pet information if available
        if pet:
            message += f"""
🐾 Pet Information
🐶 Pet Name: {pet.get('name', 'N/A')}
🆔 Pet ID: {pet.get('id', 'N/A')}
📈 Level: {pet.get('level', 'N/A')} — EXP: {format_number(pet.get('exp', 0))}
🎨 Skin ID: {pet.get('skinid', 'N/A')}
💥 Selected Skill ID: {pet.get('selectedskillid', 'N/A')}
"""

        # Add signature if available
        signature = social.get('signature', '')
        if signature and signature != "Free Fire! Battle in Style!":
            message += f"""
✍️ Signature: 💬 "{signature}"
"""
        
        # Add veteran status if available
        veteran_expire = basic.get('veteranexpiretime')
        if veteran_expire:
            message += f"""
🛡️ Veteran Status
🎖️ Expires: 🗓️ {unix_to_date(veteran_expire)}
"""

        # Add credit score
        if credit.get('creditscore'):
            message += f"""
💳 Credit Score: {credit.get('creditscore', 'N/A')}/100
"""

        message += "```"
        return message
        
    except Exception as e:
        return f"```\n❌ Error formatting player data: {str(e)}\n```"

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.cid (\d+)$'))
async def handle_cid_command(event):
    """Handle .cid command"""
    try:
        uid = event.pattern_match.group(1)
        
        # Send processing message
        status_msg = await event.reply("🔍 Fetching player data...")
        
        # Fetch player data using requests (sync)
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, fetch_player_data, uid)
        
        if data and data.get('basicinfo'):
            # Format and send the profile
            profile_message = format_player_profile(data)
            await status_msg.edit(profile_message)
        else:
            await status_msg.edit("```\n❌ Player not found or API error occurred.\nPlease check the UID and try again.\n```")
            
    except Exception as e:
        await event.reply(f"```\n❌ Error: {str(e)}\n```")

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.help$'))
async def help_command(event):
    """Help command"""
    help_text = """```
🎮 Free Fire Player Info Bot

Commands:
.cid <uid> - Get player details
.help - Show this help message

Example:
.cid 2716319203
```"""
    await event.reply(help_text)

async def main():
    """Main function to start the bot"""
    print("Starting Free Fire Userbot...")
    await client.start()
    print("✅ Userbot is running! Use .cid <uid> to fetch player info")
    await client.run_until_disconnected()

if __name__ == '__main__':
    # Start Flask in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    print("✅ Flask server started")
    
    # Start Telegram client
    try:
        client.loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\n❌ Userbot stopped!")
