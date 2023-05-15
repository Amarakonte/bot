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


list_de_prenom = hashtable_user(3)
list_de_prenom.add("Prenom","Coincey")
list_de_prenom.add("Nom","Mah")
print(list_de_prenom.get_list())
print(list_de_prenom.get("Nom"))
print(list_de_prenom.get("Prenom"))