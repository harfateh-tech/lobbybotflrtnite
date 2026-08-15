import asyncio
import os
import json
import rebootpy  # Using the updated library to fix Epic Games login errors

# Your hardcoded account details
EMAIL = "harfatehsidhu99@gmail.com"
PASSWORD = "idkcuh12345@"
MAIN_ACCOUNT_NAME = "FortniteBest100"

AUTH_FILE = "device_auths.json"

def get_auth():
    if os.path.exists(AUTH_FILE):
        with open(AUTH_FILE, "r") as f:
            data = json.load(f)
            print("🔑 Persistent token found! Logging in...")
            return rebootpy.DeviceAuth(
                account_id=data["account_id"],
                device_id=data["device_id"],
                secret=data["secret"]
            )
    else:
        print("📝 First-time setup login mode activated.")
        return rebootpy.EmailAndPasswordAuth(
            email=EMAIL,
            password=PASSWORD
        )

# Initialize using the rebootpy client engine
client = rebootpy.Client(auth=get_auth())

@client.event
async def event_ready():
    print(f"✅ Your Bot is ONLINE as: {client.user.display_name}")
    if not os.path.exists(AUTH_FILE):
        auth_details = await client.create_device_auth()
        with open(AUTH_FILE, "w") as f:
            json.dump({
                "account_id": client.user.id,
                "device_id": auth_details["device_id"],
                "secret": auth_details["secret"]
            }, f, indent=4)
        print(f"💾 Token saved to server storage!")

@client.event
async def event_friend_request(request):
    if request.display_name == MAIN_ACCOUNT_NAME:
        await request.accept()
        print(f"🤝 Accepted friend request from: {MAIN_ACCOUNT_NAME}")

@client.event
async def event_party_invite(invite):
    if invite.sender.display_name == MAIN_ACCOUNT_NAME:
        await invite.join()
        print("🚀 Joined your lobby room!")

@client.event
async def event_party_member_join(member):
    # FORCE INSTANT READY: Locks it in the exact millisecond the bot lands in your lobby
    if member.id == client.user.id:
        print("⚡ FORCING READY STATUS NOW...")
        await client.user.party.me.set_ready(True)

@client.event
async def event_party_member_state_change(member, before, after):
    # Keep enforcing ready status if you shift menus or change game modes
    if member.display_name == MAIN_ACCOUNT_NAME:
        if not client.user.party.me.readied:
            await client.user.party.me.set_ready(True)
            print("⚡ Re-enforced bot READY status.")

@client.event
async def event_party_game_state_update(state):
    # Safely leaves the party when matchmaking starts loading
    if str(state) in ["GameStatus.IN_MATCH", "GameStatus.CONNECTING"]:
        print("🛑 Match loading! Leaving party to preserve Level 1 status...")
        await client.user.party.me.leave()
        print("🌟 Disconnected safely. Go win your bot match!")

asyncio.run(client.start())
