import os
import asyncio
import requests
from datetime import datetime
from telethon import TelegramClient, events
from flask import Flask
from threading import Thread

# Flask app to keep Render service alive
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Free Fire Userbot is running!"

@app.route('/health')
def health():
    return {"status": "ok", "message": "Bot is active"}

def run_flask():
    """Run Flask in a separate thread"""
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# Get credentials from environment variables
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
SESSION_STRING = os.getenv('SESSION_STRING')

# Initialize the client
client = TelegramClient(SESSION_STRING, API_ID, API_HASH)

def unix_to_date(timestamp):
    """Convert Unix timestamp to readable date"""
    try:
        return datetime.fromtimestamp(int(timestamp)).strftime('%d %b %Y, %I:%M %p')
    except:
        return timestamp

def format_number(num):
    """Format number with commas"""
    try:
        return f"{int(num):,}"
    except:
        return num

def get_region_flag(region):
    """Get flag emoji for region"""
    flags = {
        'BD': '🇧🇩 Bangladesh',
        'IN': '🇮🇳 India',
        'PK': '🇵🇰 Pakistan',
        'ID': '🇮🇩 Indonesia',
        'TH': '🇹🇭 Thailand',
        'BR': '🇧🇷 Brazil',
        'US': '🇺🇸 USA',
    }
    return flags.get(region.upper(), f'🌍 {region.upper()}')

def fetch_player_data(uid, server='bd'):
    """Fetch player data from API using requests"""
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
    """Format player data into readable profile"""
    try:
        basic = data.get('basicinfo', {})
        profile = data.get('profileinfo', {})
        pet = data.get('petinfo', {})
        social = data.get('socialinfo', {})
        credit = data.get('creditscoreinfo', {})
        
        # Format the profile message
        message = f"""```
🎮 Free Fire Player Profile

👤 Nickname: {basic.get('nickname', 'N/A')}
🆔 Player ID: {basic.get('accountid', 'N/A')}
🌍 Region: {get_region_flag(basic.get('region', 'N/A'))}
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
