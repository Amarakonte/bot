class NodeTree:
    def __init__(self, question, options, parent=None):
        self.question = question
        self.options = options
        self.parent = parent
        self.children = []

    def add_child(self, child):
        self.children.append(child)

class Tree:
    def __init__(self):
        self.root = None
        self.current_node = None
        self.topics = ["python", "javascript", "java", "ruby"]

    def create_tree(self):
        self.root = NodeTree("Bonjour, comment puis-je vous aider ?", ["Aide sur un langage de programmation", "Autre"])
        self.current_node = self.root

        # Adding nodes for programming language topics
        lang_node = NodeTree("Sur quel langage souhaitez-vous obtenir de l'aide ?", self.topics, self.current_node)
        self.current_node.add_child(lang_node)

        python_node = NodeTree("Que souhaitez-vous savoir sur Python ?", ["Introduction", "Fonctions", "Classes"], lang_node)
        lang_node.add_child(python_node)

        java_node = NodeTree("Que souhaitez-vous savoir sur Java ?", ["Introduction", "OOP", "Collections"], lang_node)
        lang_node.add_child(java_node)

        # Adding nodes for other topics
        other_node = NodeTree("D'autres questions ?", ["Oui", "Non"], self.root)
        self.root.add_child(other_node)

    def reset(self):
        self.current_node = self.root

    def speak_about(self, topic):
        if topic in self.topics:
            return True
        else:
            return False

    def ask_question(self):
        return self.current_node.question

    def get_options(self):
        return self.current_node.options

    def select_option(self, option):
        for child in self.current_node.children:
            if child.question == option:
                self.current_node = child
                return True
        return False