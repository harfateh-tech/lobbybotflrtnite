import asyncio
import os
import json
import fortnitepy

# Fetch configuration safely from the environment variables
# If not found, it falls back to a placeholder string
EMAIL = os.environ.get("EPIC_EMAIL", "harfatehsidhu99@gmail.com")
PASSWORD = os.environ.get("EPIC_PASSWORD", "idkcuh12345@")
MAIN_ACCOUNT_NAME = os.environ.get("MAIN_ACCOUNT_NAME", "FortniteBest100")

# File name where persistent tokens will be stored
AUTH_FILE = "device_auths.json"

def get_auth():
    """Dynamically switches between Saved Session Tokens and Manual Login."""
    if os.path.exists(AUTH_FILE):
        with open(AUTH_FILE, "r") as f:
            data = json.load(f)
            print("🔑 Found saved session! Logging in automatically...")
            return fortnitepy.DeviceAuth(
                account_id=data["account_id"],
                device_id=data["device_id"],
                secret=data["secret"]
            )
    else:
        print("📝 First-time run setup. Logging in via Email/Password...")
        return fortnitepy.EmailAndPasswordAuth(
            email=EMAIL,
            password=PASSWORD
        )

# Initialize the Headless Client with the dynamic login credentials
client = fortnitepy.Client(auth=get_auth())

@client.event
async def event_ready():
    print(f"✅ Bot is online and logged into: {client.user.display_name}")
    
    # Securely extract and save the login token if it is the first time running
    if not os.path.exists(AUTH_FILE):
        auth_details = await client.create_device_auth()
        
        with open(AUTH_FILE, "w") as f:
            json.dump({
                "account_id": client.user.id,
                "device_id": auth_details["device_id"],
                "secret": auth_details["secret"]
            }, f, indent=4)
        print(f"💾 Persistent session saved to '{AUTH_FILE}'! Next run will bypass login.")

@client.event
async def event_friend_request(request):
    if request.display_name == MAIN_ACCOUNT_NAME:
        await request.accept()
        print(f"🤝 Accepted friend request from: {MAIN_ACCOUNT_NAME}")

@client.event
async def event_party_invite(invite):
    if invite.sender.display_name == MAIN_ACCOUNT_NAME:
        await invite.join()
        print("🚀 Joined your lobby party.")

@client.event
async def event_party_member_join(member):
    if member.id == client.user.id:
        print("⚡ Ready state active!")
        await client.user.party.me.set_ready(True)

@client.event
async def event_party_member_state_change(member, before, after):
    if member.display_name == MAIN_ACCOUNT_NAME:
        if not client.user.party.me.readied:
            await client.user.party.me.set_ready(True)

@client.event
async def event_party_game_state_update(state):
    if str(state) in ["GameStatus.IN_MATCH", "GameStatus.CONNECTING"]:
        print("🛑 Match loading detected! Leaving party to preserve Level 1...")
        await client.user.party.me.leave()
        print("🌟 Bot disconnected. Have a great match!")

# Execute the asynchronous engine
asyncio.run(client.start())
