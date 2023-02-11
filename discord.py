import re
import discord
import asyncio
from datetime import datetime, timedelta
from config import BOT_TOKEN

intents=discord.Intents.all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!note'):
        note = message.content[6:]
        await message.channel.send(f'Note saved: {note}')
        await set_reminder(message, note)

async def set_reminder(message, note):
    reminder_times = await get_reminder_times(message)
    now = datetime.now()

    coroutines = []
    for reminder_time in reminder_times:
        if reminder_time < now:
            await message.channel.send('Invalid reminder time.')
        else:
            time_diff = (reminder_time - now).total_seconds()
            await message.channel.send(f"I will remind you at {reminder_time}")
            coroutines.append(sleep_then_send(message, time_diff, note))
    if coroutines:
        await asyncio.gather(*coroutines)

async def sleep_then_send(message, time_diff, note):
    await asyncio.sleep(time_diff)
    await message.channel.send(f'Reminder: {note}')

async def get_reminder_times(message):
    await message.channel.send('Enter reminder time in the form of "\d+[dhm]( \d+[dhm])*" (e.g. 1d3h30m 30m):')
    time_str = await client.wait_for('message', check=lambda m: m.author == message.author)
    return [datetime.now() + parse_timedelta(time_point) for time_point in time_str.content.split()]

def parse_timedelta(time_str):
    parts = re.findall(r'(\d+[dhm])', time_str)
    time_delta = timedelta()

    units = {
        'd': 'days',
        'h': 'hours',
        'm': 'minutes'
    }

    for part in parts:
        num = int(part[:-1])
        unit = part[-1]

        if unit in units:
            time_delta += timedelta(**{units[unit]: num})

    return time_delta

if __name__ == '__main__':
    client.run(BOT_TOKEN)