import discord, json
from discord.ext import commands 

# fonction pour sauvegarder les données
def sauvegarder_donnees(donnees, fichier):
    with open(fichier, 'w') as f:
        json.dump(donnees, f)

# fonction pour charger les données
def charger_donnees(fichier):
    with open(fichier) as f:
        donnees = json.load(f)
    return donnees

# recherhce si une sauvegarde existe et importe la sauvegarde
import os
fichier = "donnees.json"
if os.path.isfile(fichier):
    donnees = charger_donnees(fichier)
    print("Sauvegarde trouvée. Les données sont en cours de chargement.")
else:
    donnees = {"historique": [], "conversation": []}
    print("Aucune sauvegarde trouvée. Des données vides ont été initialisées.")

class hashtable_user:
    def __init__(self, bucket_size):
        self.buckets = []
        for i in range(bucket_size):
            self.buckets.append([])

    def add(self, key, value):
        hashed_key = hash(key)
        indice_bucket = hashed_key % len(self.buckets)
        self.buckets[indice_bucket].append((key, value))

    def get(self, key):
        hashed_key = hash(key)
        indice_bucket = hashed_key % len(self.buckets)
        for bucket_key, bucket_value in self.buckets[indice_bucket]:
            if bucket_key == key:
                return bucket_value
        return None

    def get_list(self):
        return self.buckets


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
        
    def save_history(self):
        self.locked_queue.lock()
        historique = donnees["historique"]
        for x in range(len(historique)):
            a = historique[x]
            try:
                new_node = Node(a, None)
                if self.head is None:
                    self.head = new_node
                    self.tail = new_node
                else:
                    self.tail.next_node = new_node
                    self.tail = new_node
                self.current = self.tail
            finally:
                self.locked_queue.unlock()
        print("Les données ont été chargées.")

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
        
class NodeTree:
    def __init__(self, question, reponses):
        self.question = question
        self.reponses = reponses
        self.next_nodes = []
        self.back_nodes = []

    def append(self, question, reponses, previous_question):
        if self.question == previous_question:
            new_node = NodeTree(question, reponses,back_nodes=[previous_question])
            self.next_nodes.append(new_node)
            return new_node
        else:
            for node in self.next_nodes:
                result = node.append(question, reponses,back_nodes=[previous_question])
            if result is not None:
                return result

    def delete(self, question):
        for node in self.next_nodes:
            if node.question == question:
                self.next_nodes.remove(node)
                return True
            elif node.delete(question):
                return True
        return False

class Tree:
    def __init__(self,first_question,reponse):
        self.first_node = NodeTree(first_question,reponse)
        self.current_node = self.first_node
        
    async def start_conversation(self, ctx):
        is_start = True
        while True:
            if is_start:
                await ctx.send(self.get_question())
                is_start = False
            else:
                response = await bot.wait_for('message', check=lambda message: message.channel == ctx.channel and message.author == ctx.author)
                await ctx.send(self.send_answer(response.content))
            if self.current_node is None:
                break
                
    def append_question(self,question,reponses,previous_question):
        result = self.find_node(self.first_node, previous_question)
        if result is not None:
            new_node = NodeTree(question, reponses)
            new_node.back_nodes = [previous_question]
            result.next_nodes.append(new_node)
            return True
        else:
            for n in self.current_node.next_nodes:
                result = self.find_node(n, previous_question)
                if result is not None:
                    new_node = NodeTree(question, reponses)
                    new_node.back_nodes = [previous_question]
                    result.next_nodes.append(new_node)
                    return True
            return False

    def find_node(self,current_node,previous_question):
        if current_node.question == previous_question:
            return current_node
        else:
            for n in current_node.next_nodes:
                result = self.find_node(n, previous_question)
                if result is not None:
                    return result
            return None

    def delete_question(self, question):
        if self.first_node.question == question:
            self.first_node = None
            return True
        else:
            return self.first_node.delete(question)

    def get_question(self):
        return self.current_node.question

    def send_answer(self, reponse):
        if self.current_node.reponses is not None:
            for node in self.current_node.reponses:
                if reponse == node:
                    print("1",self.current_node.next_nodes)
                    print("2",self.current_node.question)
                    self.current_node = self.current_node.next_nodes[0]
                    return self.current_node.question
            return "Je ne comprends pas votre réponse. Veuillez réessayer."
        else:
            if len(self.current_node.next_nodes) > 0:
                self.current_node = self.current_node.next_nodes[0]
                return self.current_node.question
            else:
                self.current_node = None
                return "Fin de l'arbre"
            
class MyBot(commands.Bot):
    def __init__(self):
        global intents
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents)
        # Initialisation de la hashtable pour stocker l'historique
        self.history = {}

        # Initialisation de l'objet Tree pour gérer la discussion
        self.conversation = Tree("Bonjour, bienvenue dans ce questionnaire. Êtes-vous prêt à commencer ? (Dites nan, oui, ouais, ok, let's go)",["nan","oui", "ouais", "ok", "let's go"])
        self.conversation.append_question("Quel est votre nom ?", None, "Bonjour, bienvenue dans ce questionnaire. Êtes-vous prêt à commencer ?")
        self.conversation.append_question("Quel est votre âge ?", None, "Quel est votre nom ?")
        self.conversation.append_question("Quelle est votre profession ?", None, "Quel est votre âge ?")
        self.conversation.append_question("Dans quelle ville vivez-vous ?", None, "Quelle est votre profession ?")
        self.conversation.append_question("Merci d'avoir répondu à ces questions. Nous avons tout ce dont nous avons besoin.", None, "Dans quelle ville vivez-vous ?")
        self.conversation.delete_question("Merci d'avoir répondu à ces questions. Nous avons tout ce dont nous avons besoin.")
        
        # Initialisation de l'objet CommandHistory pour gérer l'historique de toutes les commandes
        self.command_history = CommandHistory()
        
    # Définition de la fonction d'ajout d'une commande à l'historique
    def add_to_history(self, user_id, command):
        if user_id not in self.history:
            self.history[user_id] = []
        self.history[user_id].append(command)
        # Ajout de la commande à l'historique global
        self.command_history.add_command({'user_id': user_id, 'command': command})
        donnees["historique"].append({'user_id': user_id, 'command': command})
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

# Lancer la conversation de l'arbre
@bot.command()
async def start(ctx):
    await bot.conversation.start_conversation(ctx)

@bot.command()
async def ban(ctx, user : discord.User, reason):
    reason = " ".join(reason)
    await ctx.guild.ban(user, reason = reason)
    await ctx.send(f"{user} à été ban pour la raison suivante : {reason}.")

@bot.command()
async def unban(ctx, user,reason):
    reason = " ".join(reason)
    userName, userId = user.split("#")
    bannedUsers = await ctx.guild.bans()
    for i in bannedUsers:
        if i.user.name == userName and i.user.discriminator == userId:
            await ctx.guild.unban(i.user, reason = reason)
            await ctx.send(f"{user} à été unban.")
            return
    #Ici on sait que lutilisateur na pas ete trouvé
    await ctx.send(f"L'utilisateur {user} n'est pas dans la liste des bans")

@bot.command()
async def kick(ctx, user : discord.User, *reason):
    reason = " ".join(reason)
    await ctx.guild.kick(user, reason = reason)
    await ctx.send(f"{user} à été kick.")

@bot.command()
async def clears(ctx, nombre : int):
    messages = await ctx.channel.history(limit = nombre + 1).flatten()
    for message in messages:
        await message.delete()


# Lancement du bot
@bot.event
async def on_ready():
    print("Bot is ready")
    
bot.run("MTA5MTI2MDIxNzEwMDA4NzMwOA.GtRyxC.9kKhdB95eL6zOBXJCPrhyfGsUro2pZCg73pVhg")

# faire la sauvegarde
sauvegarder_donnees(donnees, fichier)
print("La sauvegarde à été éffectuer")