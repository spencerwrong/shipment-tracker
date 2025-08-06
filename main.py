import configparser
import datetime
import discord 
from carriers.ups import UPSClient

from discord.ext import commands

config = configparser.RawConfigParser()   
configFilePath = 'config.ini'
config.read(configFilePath)

DISCORD_BOT_TOKEN = config.get('Discord', 'bot_token')
UPS_CLIENT_ID = config.get('UPS', 'client_id')
UPS_CLIENT_SECRET = config.get('UPS', 'client_secret')
UPS_USE_SANDBOX = config.getboolean('UPS', 'use_sandbox')

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents)

ups_client = UPSClient(UPS_CLIENT_ID, UPS_CLIENT_SECRET, UPS_USE_SANDBOX)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


@bot.command()
async def ups(ctx, tracking_number):
    response = ups_client.ups_track(tracking_number)

    try:
        shipment = response['trackResponse']['shipment'][0]
        package = shipment['package'][0]

        tracking_number = package.get('trackingNumber', 'N/A')
        current_status = package.get('currentStatus', {}).get('description', 'Unknown')
        is_delivered = current_status.upper() == 'DELIVERED'

        # Origin and destination
        origin = next((addr["address"] for addr in package["packageAddress"] if addr["type"] == "ORIGIN"), {})
        destination = next((addr["address"] for addr in package["packageAddress"] if addr["type"] == "DESTINATION"), {})
        origin_str = ", ".join(filter(None, [origin.get("city", ""), origin.get("stateProvince", ""), origin.get("countryCode", "")]))
        dest_str = ", ".join(filter(None, [destination.get("city", ""), destination.get("stateProvince", ""), destination.get("countryCode", "")]))

        # Weight and dimensions
        weight = package.get("weight", {})
        weight_str = f"{weight.get('weight')} {weight.get('unitOfMeasurement')}"
        dim = package.get("dimension", {})
        dim_str = f"{dim.get('length')} x {dim.get('width')} x {dim.get('height')} {dim.get('unitOfDimension')}"

        # ETA or delivery date
        eta_str = "N/A"
        if is_delivered:
            delivery_date = package["deliveryDate"][0]["date"]
            delivery_time = package["deliveryTime"]["endTime"]
            eta_dt = datetime.datetime.strptime(delivery_date + delivery_time, "%Y%m%d%H%M%S")
            eta_str = eta_dt.strftime("%Y-%m-%d %H:%M:%S")
        elif package.get("deliveryDate"):
            # Show estimated delivery
            delivery_date = package["deliveryDate"][0]["date"]
            eta_dt = datetime.datetime.strptime(delivery_date, "%Y%m%d")
            eta_str = eta_dt.strftime("%Y-%m-%d")

        delivery_loc = package.get("deliveryInformation", {}).get("location", "Unknown")

        embed = discord.Embed(
            title=f"UPS Tracking Info - {tracking_number}"
        )
        embed.add_field(name="Status", value=current_status, inline=False)
        embed.add_field(name="From", value=origin_str or "Unknown", inline=True)
        embed.add_field(name="To", value=dest_str or "Unknown", inline=True)
        embed.add_field(name="ETA" if not is_delivered else "Delivered At", value=eta_str, inline=False)
        embed.add_field(name="Weight", value=weight_str, inline=True)
        embed.add_field(name="Dimensions", value=dim_str, inline=True)
        embed.add_field(name="Left At", value=delivery_loc, inline=False)

        activities = package.get("activity", [])
        timeline_lines = []
        for activity in activities[0:5]:
            date = activity.get("date", "")
            time = activity.get("time", "")
            desc = activity.get("status", {}).get("description", "N/A")
            loc = activity.get("location", {}).get("address", {})
            city = loc.get("city", "")
            state = loc.get("stateProvince", "")
            country = loc.get("countryCode", "")
            loc_str = ", ".join(filter(None, [city, state, country]))
            try:
                dt = datetime.datetime.strptime(date + time, "%Y%m%d%H%M%S")
                dt_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                dt_str = f"{date} {time}"
            timeline_lines.append(f"`{dt_str}` • {desc} • {loc_str or 'N/A'}")

        embed.add_field(name="Recent Activity", value="\n".join(timeline_lines) or "No activity found", inline=False)
        embed.set_footer(text="UPS Worldwide Tracking")

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"Error retrieving tracking info: {e}")


bot.run(DISCORD_BOT_TOKEN)