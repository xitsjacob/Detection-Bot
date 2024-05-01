import requests
import os
import time
from dotenv import load_dotenv

import asyncio
import discord
from discord import Webhook
import aiohttp

load_dotenv(".env")

auth_token = os.getenv("RBLX_TOKEN")

def check_rblx_past(user_id, presence_id):
    last_status_hhp = 0
    last_status_icy = 1

    if user_id == os.getenv("HHP_RBLX") and presence_id != last_status_hhp:
        last_status_hhp = presence_id
        return True
    elif user_id == os.getenv("ICY_RBLX") and presence_id != last_status_icy:
        last_status_icy = presence_id
        return True
    else:
        return False

def get_rblx_presence(user_id):
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    data = {
        "userIds": [user_id]
    }
    url = "https://presence.roblox.com/v1/presence/users"

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        
        data = response.json()
        if len(data["userPresences"]) > 0:
            presence = data["userPresences"][0]["userPresenceType"]
            if check_rblx_past(user_id, presence):
                if presence == 1:
                    return "On Website"
                elif presence == 2:
                    return "In-game"
                else:
                    return "Offline"
        else:
            return "User not found"
    except requests.exceptions.RequestException as e:
        return f"Error fetching data: {str(e)}"

async def track_rblx_status():
    updates = 1

    while True:
        rblx_id = (os.getenv("HHP_RBLX"), os.getenv("ICY_RBLX"))

        for user_id in rblx_id:
            rblx_status = get_rblx_presence(user_id)

            try:
                async with aiohttp.ClientSession() as session:
                    webhook = Webhook.from_url(os.getenv("RBLX_WEBHOOK_URL"), session=session)
                    
                    username = f"GeorgeGodsent ({user_id})" if user_id == os.getenv("HHP_RBLX") else f"IcyQueenbee ({user_id})"
                    embed = discord.Embed(title=f"{username} | {rblx_status}")
                    await webhook.send(embed=embed, username="RBLX Detection")

                    print(f"RBLX message #{updates} sent successfully!")
                    updates += 1

            except Exception as e:
                print(f"RBLX Error sending message: {e}")

        time.sleep(120) # Check status every minute

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(track_rblx_status())
    loop.close()
