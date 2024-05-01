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
rblx_id = (os.getenv("HHP_RBLX"), os.getenv("ICY_RBLX"))

async def get_rblx_presence(user_id):
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
            return presence
        else:
            return "User not found"
    except requests.exceptions.RequestException as e:
        return f"Error fetching data: {str(e)}"

async def rblx_update_check(user_id):
    last_rblx_hhp = 0
    last_rblx_icy = 2

    print(f"{last_rblx_hhp} | {last_rblx_icy}")

    try:
        presence_id = await get_rblx_presence(user_id)

        if user_id == rblx_id[0] and presence_id != last_rblx_hhp:
            last_rblx_hhp = presence_id
            print(last_rblx_hhp)
            if presence_id == 1:
                return "On Website"
            elif presence_id == 2:
                return "In-game"
            else:
                return "Offline"
        elif user_id == rblx_id[1] and presence_id != last_rblx_icy:
            last_rblx_icy = int(presence_id)
            print(last_rblx_icy)
            if presence_id == 1:
                return "On Website"
            elif presence_id == 2:
                return "In-game"
            else:
                return "Offline"
    except Exception as e:
        return print(f"Error: {e}")

    

async def track_rblx_status():
    updates = 1

    while True:

        for user_id in rblx_id:
            rblx_status = await rblx_update_check(user_id)

            try:
                if rblx_status != None:
                    async with aiohttp.ClientSession() as session:
                        webhook = Webhook.from_url(os.getenv("RBLX_WEBHOOK_URL"), session=session)
                        
                        username = f"GeorgeGodsent ({user_id})" if user_id == os.getenv("HHP_RBLX") else f"IcyQueenbee ({user_id})"
                        embed = discord.Embed(title=f"{username} | {rblx_status}")
                        await webhook.send(embed=embed, username="RBLX Detection")

                print(f"RBLX Update Check #{updates} successfully!")
                updates += 1

            except Exception as e:
                print(f"RBLX Error sending message: {e}")

        time.sleep(60) # Check status every minute

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(track_rblx_status())
    loop.close()
