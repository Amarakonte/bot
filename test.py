import discord, json
from discord.ext import commands 

class MyBot(commands.Bot):
    def __init__(self):
        global intents
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents)


bot = MyBot()


class Node:
    def __init__(self, question, reponses):
        self.question = question
        self.reponses = reponses
        self.next_nodes = []
        self.back_nodes = []

    def append(self, question, reponses, previous_question):
        if self.question == previous_question:
            new_node = Node(question, reponses,back_nodes=[previous_question])
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
        self.first_node = Node(first_question,reponse)
        self.current_node = self.first_node
        
    async def start_tree(self, ctx):
        is_start = True
        while True:
            if is_start:
                await ctx.send(t.get_question())
                is_start = False
            else:
                response = await bot.wait_for('message', check=lambda message: message.channel == ctx.channel and message.author == ctx.author)
                await ctx.send(t.send_answer(response.content))
            if self.current_node is None:
                break
                
    def append_question(self,question,reponses,previous_question):
        result = self.find_node(self.first_node, previous_question)
        if result is not None:
            new_node = Node(question, reponses)
            new_node.back_nodes = [previous_question]
            result.next_nodes.append(new_node)
            return True
        else:
            for n in self.current_node.next_nodes:
                result = self.find_node(n, previous_question)
                if result is not None:
                    new_node = Node(question, reponses)
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
            
        
t = Tree("Bonjour, bienvenue dans ce questionnaire. Êtes-vous prêt à commencer ?",["nan","oui", "ouais", "ok", "let's go"])
t.append_question("Quel est votre nom ?", None, "Bonjour, bienvenue dans ce questionnaire. Êtes-vous prêt à commencer ?")
t.append_question("Quel est votre âge ?", None, "Quel est votre nom ?")
t.append_question("Quelle est votre profession ?", None, "Quel est votre âge ?")
t.append_question("Dans quelle ville vivez-vous ?", None, "Quelle est votre profession ?")
t.append_question("Merci d'avoir répondu à ces questions. Nous avons tout ce dont nous avons besoin.", None, "Dans quelle ville vivez-vous ?")
t.delete_question("Merci d'avoir répondu à ces questions. Nous avons tout ce dont nous avons besoin.")
# print("Merci d'avoir répondu à ces questions. Nous avons tout ce dont nous avons besoin.")

@bot.command()
async def start(ctx):
    await t.start_tree(ctx)


@bot.event
async def on_ready():
    print("Bot is ready")
    
bot.run("MTA5MTI2MDIxNzEwMDA4NzMwOA.GtRyxC.9kKhdB95eL6zOBXJCPrhyfGsUro2pZCg73pVhg")