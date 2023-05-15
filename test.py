class Node:
    def __init__(self, question, reponses):
        self.question = question
        self.reponses = reponses
        self.next_nodes = []

    def append(self, question, reponses, previous_question):
        if self.question == previous_question:
            new_node = Node(question, reponses)
            self.next_nodes.append(new_node)
            return new_node
        else:
            for node in self.next_nodes:
                result = node.append(question, reponses, previous_question)
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
    def __init__(self,first_question):
        self.first_node = Node(first_question,["oui", "ouais", "ok", "let's go"])
        self.current_node = self.first_node
    
    def append_question(self,question,reponses,previous_question):
        result = self.find_node(self.first_node, previous_question)
        if result is not None:
            new_node = Node(question,reponses)
            result.next_nodes.append(new_node)
            return True
        else:
            # Recherche du dernier noeud existant
            last_node = self.first_node
            while last_node.next_nodes:
                last_node = last_node.next_nodes[-1]

            # Ajout du nouveau noeud au dernier noeud existant
            if last_node.question == previous_question:
                new_node = Node(question,reponses)
                last_node.next_nodes.append(new_node)
                return True
            else:
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
        else:
            self.first_node.delete(question)

    def get_question(self):
        return self.current_node.question

    def send_answer(self, reponse):
        print("1",self.current_node.next_nodes)
        for node in self.first_node.reponses:
            print("2",node)
            if reponse.lower() in [r.lower() for r in node.reponses]:
                self.current_node = node
                return self.current_node.question
        return "Je ne comprends pas votre réponse. Veuillez réessayer."




t = Tree("Bonjour, bienvenue dans ce questionnaire. Êtes-vous prêt à commencer ?")
t.append_question("Quel est votre nom ?", ["oui", "ouais", "ok", "let's go"], "Êtes-vous prêt à commencer ?")
t.append_question("Quel est votre âge ?", [], "Quel est votre nom ?")
t.append_question("Quelle est votre profession ?", [], "Quel est votre nom ?")
t.append_question("Dans quelle ville vivez-vous ?", [], "Quelle est votre profession ?")
t.append_question("Merci d'avoir répondu à ces questions. Nous avons tout ce dont nous avons besoin.", [], "Dans quelle ville vivez-vous ?")

is_start = True
while True:
  if is_start:
    print(t.get_question())
    is_start = False
  else:
    response = input("> ")
    print(t.send_answer(response))
  if t.current_node is None:
    break

print("Merci d'avoir répondu à ces questions. Nous avons tout ce dont nous avons besoin.")
