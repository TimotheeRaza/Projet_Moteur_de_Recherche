class Author:
    """Représente un auteur et ses productions."""
    def __init__(self, name=""):
        self.name = name
        self.nb_docs = 0
        self.production = {}

    def add(self, doc_id, document):
        if doc_id not in self.production:
            self.production[doc_id] = document
            self.nb_docs += 1

    def __str__(self):
        return f"Auteur : {self.name} | Documents publiés : {self.nb_docs}"