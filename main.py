import configparser
import datetime
import discord 
from ups import ups_track, ups_create_token

from discord.ext import commands

config = configparser.RawConfigParser()   
configFilePath = 'config.ini'
config.read(configFilePath)

DISCORD_BOT_TOKEN = config.get('Keys', 'discordbottoken')
UPS_CLIENT_ID = config.get('Keys', 'upsclientid')
UPS_CLIENT_SECRET = config.get('Keys', 'upsclientsecret')

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def ups(ctx, tracking_number):
    access_token = ups_create_token(UPS_CLIENT_ID, UPS_CLIENT_SECRET)['access_token']
    response = ups_track(tracking_number, access_token)
    
    shipment = response['trackResponse']['shipment'][0]
    package = shipment['package'][0]

    tracking_number = package['trackingNumber']
    status = package['activity'][0]['status']['description']
    formatted_response = f'Tracking Number: {tracking_number}\nStatus: {status}'

    if status == 'DELIVERED ':
        delivery_date = package['deliveryDate'][0]['date']
        delivery_time = package['deliveryTime']['endTime']
        formatted_delivery_date = datetime.datetime.strptime(delivery_date, "%Y%m%d").strftime("%Y/%m/%d")
        formatted_delivery_time = datetime.datetime.strptime(delivery_time, "%H%M%S").strftime("%H:%M:%S")
        formatted_response += f'\nDelivery Date: {formatted_delivery_date} {formatted_delivery_time}'

    await ctx.send(formatted_response)

bot.run(DISCORD_BOT_TOKEN)