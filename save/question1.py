import discord
from discord.ext import commands

class CommandNode:
    def __init__(self, command, prev=None):
        self.command = command
        self.prev = prev

class CommandHistory:
    def __init__(self):
        self.history = {}

    def add_command(self, user_id, command):
        if user_id not in self.history:
            self.history[user_id] = CommandNode(command)
        else:
            self.history[user_id] = CommandNode(command, self.history[user_id])

    def get_last_command(self, user_id):
        if user_id not in self.history:
            return None
        return self.history[user_id].command

    def get_all_commands(self, user_id):
        if user_id not in self.history:
            return []
        commands = []
        node = self.history[user_id]
        while node:
            commands.append(node.command)
            node = node.prev
        return commands

    def get_previous_command(self, user_id):
        if user_id not in self.history:
            return None
        if not self.history[user_id].prev:
            return self.history[user_id].command
        self.history[user_id] = self.history[user_id].prev
        return self.history[user_id].command

    def get_next_command(self, user_id):
        if user_id not in self.history:
            return None
        if not self.history[user_id].prev:
            return self.history[user_id].command
        if not self.history[user_id].prev.prev:
            return self.history[user_id].prev.command
        self.history[user_id] = self.history[user_id].prev
        return self.history[user_id].command

    def clear_history(self, user_id):
        if user_id in self.history:
            self.history[user_id] = None

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents = intents)

history = CommandHistory()

@bot.event
async def on_ready():
    print("Bot is ready")

@bot.command()
async def last(ctx):
    last_command = history.get_last_command(ctx.author.id)
    if last_command:
        await ctx.send(f"Your last command was: {last_command}")
    else:
        await ctx.send("You haven't entered any command yet")

@bot.command()
async def all(ctx):
    all_commands = history.get_all_commands(ctx.author.id)
    if all_commands:
        commands_str = "\n".join(all_commands)
        await ctx.send(f"Your command history:\n{commands_str}")
    else:
        await ctx.send("You haven't entered any command yet")

@bot.command()
async def prev(ctx):
    previous_command = history.get_previous_command(ctx.author.id)
    if previous_command:
        await ctx.send(f"Your previous command was: {previous_command}")
    else:
        await ctx.send("You are already at the beginning of your command history")

@bot.command()
async def next(ctx):
    next_command = history.get_next_command(ctx.author.id)
    if next_command:
        await ctx.send(f"Your next command was: {next_command}")
    else:
        await ctx.send("You are already at the ending of your command history")

@bot.command()
async def clear_history(ctx):
    history.clear_history(ctx.author.id)
    await ctx.send("Your command history has been cleared")

@bot.command()
async def hello(ctx):
    await ctx.send("Hello, world!")
    history.add_command(ctx.author.id, "hello")
    
@bot.command()
async def test(ctx):
    await ctx.send("test, world!")
    history.add_command(ctx.author.id, "test")
    


bot.run("MTA5MTI2MDIxNzEwMDA4NzMwOA.GTJYvI.5cWrx6EnRQSqyc4H6cZblbCyKKUXWEQ9SMwbZ0")
