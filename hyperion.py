import discord
import asyncio
import psutil

from discord.ext import commands


pids = []
bot = commands.Bot(command_prefix='=', owner_id='280833495700471817')

async def on_ready(self):
    print('Logged in as', self.user)


@commands.command(name='add', description='add a bot to monitor')
async def add_pid(ctx, pid: int, *, name: str):
    """
    Usage: add <pid> <name>
    """
    global pids
    if psutil.pid_exists(pid):
        pids.append(BotPid(pid, name))
        ctx.channel.send(f'bot {name} with pid {pid} added to monitoring')
    else:
        ctx.channel.send(f'pid {pid} not found')


@commands.command(name='list', description='list the bots monitored')
async def list_bots(ctx):
    global pids
    ctx.channel.send('\n'.join([f'{p.name}: {p.pid}' for p in pids]))


@commands.command(name='update', description='update a bots pid')
async def update_pid(ctx, pid: int, *, name: str):
    """
    Usage: update <pid> <name>
    """
    global pids
    arr = [p for p in pids if p.name == name]
    if psutil.pid_exists(pid) and len(arr) == 1:
        pids.remove(arr[0])
        pids.append(BotPid(pid, name))
        ctx.channel.send(f'bot {name} updated with pid {pid}')
    else:
        ctx.channel.send(f'pid {pid} or {name} not found')


async def monitor():
    global pids
    await bot.wait_until_ready()

    while not bot.is_closed():
        backup = pids
        for p in pids:
            if not psutil.pid_exists(p.pid):
                owner = bot.fetch_user(bot.owner_id)
                dmc = owner.dm_channel
                if dmc is None:
                    owner.create_dm()
                dmc = owner.dm_channel
                dmc.send(f'{p.name}({p.pid}) is probably offline')
                backup.remove(p)
        pids = backup

        await asyncio.sleep(60)


class BotPid():
    def __init__(self, pid, name):
        self.pid = pid
        self.name = name


if __name__ == '__main__':
    secret = ''
    with open('secret.key', 'r') as f:
        secret = f.readline().strip()
    bot.loop.create_task(monitor())
    bot.run(secret)