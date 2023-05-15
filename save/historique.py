import discord
from discord.ext import commands

class Node:
    def __init__(self, data=None, next_node=None):
        self.data = data
        self.next_node = next_node

class LockedQueue:
    def __init__(self):
        self.queue = []
        self.locked = False

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False

    def is_locked(self):
        return self.locked

    def put(self, item):
        if not self.locked:
            self.queue.append(item)
            return True
        else:
            return False

    def get(self):
        if not self.locked and len(self.queue) > 0:
            return self.queue.pop(0)
        else:
            return None

class CommandHistory:
    def __init__(self):
        self.head = None
        self.tail = None
        self.current = None
        self.locked_queue = LockedQueue()

    def add_command(self, command):
        self.locked_queue.lock()
        try:
            new_node = Node(command, None)
            if self.head is None:
                self.head = new_node
                self.tail = new_node
            else:
                self.tail.next_node = new_node
                self.tail = new_node
            self.current = self.tail
        finally:
            self.locked_queue.unlock()

    def get_last_command(self):
        if self.tail is None:
            return None
        return self.tail.data

    def get_last_command_by_user(self, user_id):
        current_node = self.tail
        while current_node is not None:
            if current_node.data['user_id'] == user_id:
                return current_node.data['command']
            current_node = current_node.next_node
        return None

    def get_all_commands_by_user(self, user_id):
        commands = []
        current_node = self.head
        while current_node is not None:
            if current_node.data['user_id'] == user_id:
                commands.append(current_node.data['command'])
            current_node = current_node.next_node
        return commands

    def move_backwards(self):
        if self.current is not None and self.current != self.head:
            previous_node = self.head
            while previous_node.next_node != self.current:
                previous_node = previous_node.next_node
            self.current = previous_node

    def move_forwards(self):
        if self.current is not None and self.current != self.tail:
            self.current = self.current.next_node

    def clear_history(self):
        self.locked_queue.lock()
        try:
            self.head = None
            self.tail = None
            self.current = None
        finally:
            self.locked_queue.unlock()
        
class MyBot(commands.Bot):
    def __init__(self):
        global intents
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents)
        # Initialisation de la hashtable pour stocker l'historique
        self.history = {}

        # Initialisation de l'objet CommandHistory pour gérer l'historique de toutes les commandes
        self.command_history = CommandHistory()
        
    # Définition de la fonction d'ajout d'une commande à l'historique
    def add_to_history(self, user_id, command):
        if user_id not in self.history:
            self.history[user_id] = []
        self.history[user_id].append(command)
        # Ajout de la commande à l'historique global
        self.command_history.add_command({'user_id': user_id, 'command': command})
        # Mettre à jour la position actuelle
        self.command_history.current = self.command_history.tail
        
    

# Création de l'instance du bot
bot = MyBot()

# Définition de la commande "test" pour tester l'ajout d'une commande à l'historique
@bot.command()
async def test(ctx):
    # Ajout de la commande à l'historique
    bot.add_to_history(ctx.author.id,ctx.message.content)
    await ctx.send(f"Commande ajoutée à l'historique de {ctx.author.name}.")
    

@bot.command(name='hello')
async def hello(ctx):
    bot.add_to_history(ctx.author.id,ctx.message.content)
    await ctx.send('Hello!')


# Définition de la commande "all" pour afficher toutes les commandes d'un utilisateur
@bot.command(name='all')
async def all(ctx):
    user_id = ctx.author.id
    bot.command_history.locked_queue.put(user_id)
    queue = bot.command_history.locked_queue.get()
    if  queue == user_id:
        commands = bot.command_history.get_all_commands_by_user(user_id)
        if len(commands) == 0:
            await ctx.send("Aucune commande trouvée dans l'historique.")
        else:
            all_commands = "\n".join(commands)
            await ctx.send(f"Toutes les commandes de {ctx.author.name}:\n{all_commands}")
    else :
        bot.command_history.locked_queue.put(user_id)
        await ctx.send("<@{ctx.author.id}> est en train de consulté l'historique.")


# Définition de la commande "last" pour afficher la dernière commande d'un utilisateur
@bot.command(name='last')
async def last(ctx):
    user_id = ctx.author.id
    last_command = bot.command_history.get_last_command_by_user(user_id)
    if last_command is None:
        await ctx.send("Aucune commande trouvée dans l'historique.")
    else:
        await ctx.send(f"Dernière commande de {ctx.author.name}: {last_command}")
        
        
# Définition de la commande "back" pour reculer dans l'historique
@bot.command(name='back')
async def back(ctx):
    bot.command_history.move_backwards()
    last_command = bot.command_history.current.data
    if last_command is None:
        await ctx.send("Aucune commande trouvée dans l'historique.")
    else:
        await ctx.send(f"Commande précédente de {ctx.author.name}: {last_command['command']}")


# Définition de la commande "forward" pour avancer dans l'historique
@bot.command(name='next')
async def forward(ctx):
    bot.command_history.move_forwards()
    last_command = bot.command_history.current.data
    if last_command is None:
        await ctx.send("Aucune commande trouvée dans l'historique.")
    else:
        await ctx.send(f"Commande suivante de {ctx.author.name}: {last_command['command']}")


# Définition de la commande "clear" pour vider l'historique
@bot.command(name='clear')
async def clear(ctx):
    bot.command_history.clear_history()
    await ctx.send(f"Historique de {ctx.author.name} vidé.")