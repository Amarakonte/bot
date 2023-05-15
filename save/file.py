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

queue = LockedQueue()

queue.put("element1")  # Ajoute "element1" à la file
queue.lock()  # Verrouille la file
queue.put("element2")  # Échoue car la file est verrouillée
queue.unlock()  # Déverrouille la file
queue.put("element3")  # Ajoute "element3" à la file
print(queue.get())  # Retourne "element1" car c'est le premier élément de la file
print(queue.get())  # Retourne "element3" car c'est le seul élément restant dans la file
print(queue.get())  # Retourne None car la file est vide
