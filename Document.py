class Document:
    """Classe de base représentant un document."""
    def __init__(self, titre="", auteur="", date="", url="", texte=""):
        self.titre = titre
        self.auteur = auteur
        self.date = date
        self.url = url
        self.texte = texte
        self.type = "Document"

    def getType(self):
        return self.type

    def afficher_infos(self):
        print(f"--- Informations du Document ---")
        print(f"Titre : {self.titre}\nAuteur : {self.auteur}\nDate : {self.date}\nURL : {self.url}\nTexte : {self.texte}")

    def __str__(self):
        return f"{self.titre} (Auteur: {self.auteur})"

    def __repr__(self):
        return f"Document(titre='{self.titre}')"


class RedditDocument(Document):
    """Représente un document Reddit."""
    def __init__(self, titre="", auteur="", date="", url="", texte="", nb_commentaires=0, subreddit=""):
        super().__init__(titre, auteur, date, url, texte)
        self.type = "Reddit"
        self._nb_commentaires = nb_commentaires
        self.subreddit = subreddit

    def getType(self):
        return self.type

    @property
    def nb_commentaires(self):
        return self._nb_commentaires

    @nb_commentaires.setter
    def nb_commentaires(self, value):
        self._nb_commentaires = value

    def __str__(self):
        return f"[Reddit r/{self.subreddit}] {super().__str__()} | Commentaires : {self._nb_commentaires}"


class ArxivDocument(Document):
    """Représente un article Arxiv."""
    def __init__(self, titre="", auteur="", date="", url="", texte="", co_auteurs=None, categories=None):
        super().__init__(titre, auteur, date, url, texte)
        self.type = "Arxiv"
        self._co_auteurs = co_auteurs if co_auteurs is not None else []
        self.categories = categories if categories is not None else []

    def getType(self):
        return self.type

    @property
    def co_auteurs(self):
        return self._co_auteurs

    @co_auteurs.setter
    def co_auteurs(self, value):
        self._co_auteurs = value

    def __str__(self):
        coauteurs_str = ', '.join(self._co_auteurs) if self._co_auteurs else "Aucun"
        return f"[Arxiv] {super().__str__()} | Co-auteurs : {coauteurs_str}"