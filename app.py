import os
import asyncio
from datetime import datetime
from telethon import TelegramClient, events
from flask import Flask
from threading import Thread
import aiohttp
import logging

# Setup logging
logging.basicConfig(
    format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
    level=logging.INFO
)

# Environment variables
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
SESSION_STRING = os.getenv('SESSION_STRING')
PORT = int(os.getenv('PORT', 10000))

# Initialize Telethon Client
client = TelegramClient('userbot', API_ID, API_HASH)

# Flask app for Render deployment
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Free Fire Userbot is Running!"

@app.route('/health')
def health():
    return {"status": "healthy", "bot": "running"}

def run_flask():
    """Run Flask in a separate thread"""
    app.run(host='0.0.0.0', port=PORT)

def unix_to_date(timestamp):
    """Convert Unix timestamp to readable date"""
    try:
        if isinstance(timestamp, str):
            timestamp = int(timestamp)
        return datetime.fromtimestamp(timestamp).strftime('%d %b %Y, %I:%M %p')
    except:
        return "N/A"

def format_number(num):
    """Format numbers with commas"""
    try:
        return f"{int(num):,}"
    except:
        return str(num)

def get_region_flag(region):
    """Get flag emoji for region"""
    flags = {
        'BD': '🇧🇩 Bangladesh',
        'IN': '🇮🇳 India',
        'PK': '🇵🇰 Pakistan',
        'US': '🇺🇸 USA',
        'BR': '🇧🇷 Brazil',
        'ID': '🇮🇩 Indonesia',
        'TH': '🇹🇭 Thailand',
        'VN': '🇻🇳 Vietnam',
        'MY': '🇲🇾 Malaysia',
        'PH': '🇵🇭 Philippines',
    }
    return flags.get(region.upper(), f'🌍 {region}')

async def fetch_player_data(uid, server='bd'):
    """Fetch player data from API"""
    url = f"https://freefire-api-2-e4j5.onrender.com/get_player_personal_show?server={server}&uid={uid}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None
    except Exception as e:
        logging.error(f"API Error: {e}")
        return None

def format_player_info(data):
    """Format player information into beautiful text"""
    try:
        basic = data.get('basicinfo', {})
        profile = data.get('profileinfo', {})
        pet = data.get('petinfo', {})
        social = data.get('socialinfo', {})
        credit = data.get('creditscoreinfo', {})
        
        # Build formatted message
        message = f"""```
🎮 Free Fire Player Profile
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 Nickname: {basic.get('nickname', 'N/A')}
🆔 Player ID: {basic.get('accountid', 'N/A')}
🌍 Region: {get_region_flag(basic.get('region', 'Unknown'))}
🧾 Account Type: {'Garena' if basic.get('accounttype') == 1 else 'Guest'} ({basic.get('accounttype', 'N/A')})
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
