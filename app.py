# -*- coding: utf-8 -*-
import os
import asyncio
import requests
from datetime import datetime
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from flask import Flask
from threading import Thread

# Flask app to keep Render service alive
app = Flask(__name__)

@app.route('/')
def home():
    return "Free Fire Userbot is running!"

@app.route('/health')
def health():
    return {"status": "ok", "message": "Bot is active"}

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# Get credentials from environment variables
API_ID = int(os.getenv('API_ID', '0'))
API_HASH = os.getenv('API_HASH', '')
SESSION_STRING = os.getenv('SESSION_STRING', '')

# Validate environment variables
if not API_ID or not API_HASH or not SESSION_STRING:
    print("ERROR: Missing environment variables!")
    print(f"API_ID: {'OK' if API_ID else 'MISSING'}")
    print(f"API_HASH: {'OK' if API_HASH else 'MISSING'}")
    print(f"SESSION_STRING: {'OK' if SESSION_STRING else 'MISSING'}")
    exit(1)

print(f"API_ID: {API_ID}")
print(f"API_HASH: {API_HASH[:10]}...")
print(f"SESSION_STRING: {SESSION_STRING[:20]}...")

# Initialize the client with StringSession
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

def unix_to_date(timestamp):
    try:
        return datetime.fromtimestamp(int(timestamp)).strftime('%d %b %Y, %I:%M %p')
    except:
        return timestamp

def format_number(num):
    try:
        return f"{int(num):,}"
    except:
        return num

def get_region_flag(region):
    flags = {
        'BD': '\U0001F1E7\U0001F1E9 Bangladesh',
        'IN': '\U0001F1EE\U0001F1F3 India',
        'PK': '\U0001F1F5\U0001F1F0 Pakistan',
        'ID': '\U0001F1EE\U0001F1E9 Indonesia',
        'TH': '\U0001F1F9\U0001F1ED Thailand',
        'BR': '\U0001F1E7\U0001F1F7 Brazil',
        'US': '\U0001F1FA\U0001F1F8 USA',
    }
    return flags.get(region.upper(), f'\U0001F30D {region.upper()}')

def fetch_player_data(uid, server='bd'):
    url = f"https://freefire-api-2-e4j5.onrender.com/get_player_personal_show?server={server}&uid={uid}"
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API Error: Status {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def format_player_profile(data):
    try:
        basic = data.get('basicinfo', {})
        profile = data.get('profileinfo', {})
        pet = data.get('petinfo', {})
        social = data.get('socialinfo', {})
        credit = data.get('creditscoreinfo', {})
        
        message = "```\n"
        message += "\U0001F3AE Free Fire Player Profile\n\n"
        message += f"\U0001F464 Nickname: {basic.get('nickname', 'N/A')}\n"
        message += f"\U0001F194 Player ID: {basic.get('accountid', 'N/A')}\n"
        message += f"\U0001F30D Region: {get_region_flag(basic.get('region', 'N/A'))}\n"
        message += f"\U0001F9FE Account Type: Garena ({basic.get('accounttype', 'N/A')})\n"
        message += f"\U0001F3C5 Level: {basic.get('level', 'N/A')}\n"
        message += f"\u2728 EXP: {format_number(basic.get('exp', 0))}\n"
        message += f"\u2764\uFE0F Likes: {format_number(basic.get('liked', 0))}\n"
        message += f"\U0001F4C5 Created On: \U0001F5D3\uFE0F {unix_to_date(basic.get('createat', 'N/A'))}\n"
        message += f"\U0001F511 Last Login: \u23F1\uFE0F {unix_to_date(basic.get('lastloginat', 'N/A'))}\n\n"
        
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
        print("\nUserbot stopped!")🌍 Region: {get_region_flag(basic.get('region', 'N/A'))}
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
