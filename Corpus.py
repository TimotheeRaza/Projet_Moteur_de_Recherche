import pandas as pd
from DocumentFactory import DocumentFactory
from Author import Author

class Corpus:
    _instance = None

    def __new__(cls, nom="Corpus Unique"):
        if cls._instance is None:
            cls._instance = super(Corpus, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, nom="Corpus Unique"):
        if self._initialized:
            return
        self.nom = nom
        self.documents = {}
        self.id_document = 0
        self.authors = {}
        self._initialized = True

    def add_document(self, origine="", **kwargs):
        doc = DocumentFactory.create_document(origine, **kwargs)
        doc_id = self.id_document
        self.documents[doc_id] = doc
        self.id_document += 1

        nom_auteur = doc.auteur if doc.auteur and doc.auteur.strip() else "Auteur Inconnu"
        if nom_auteur not in self.authors:
            self.authors[nom_auteur] = Author(name=nom_auteur)
        self.authors[nom_auteur].add(doc_id, doc)

    def __repr__(self):
        return f"Corpus '{self.nom}' | Documents : {len(self.documents)} | Auteurs : {len(self.authors)}"

    def afficher_documents_tries(self, n=5, critere="date"):
        docs_list = list(self.documents.items())
        if critere == "date":
            docs_list.sort(key=lambda x: str(x[1].date) if x[1].date else "")
        elif critere == "titre":
            docs_list.sort(key=lambda x: str(x[1].titre).lower() if x[1].titre else "")

        print(f"\n--- Top {n} documents triés par {critere} ---")
        for doc_id, doc in docs_list[:n]:
            print(f"ID {doc_id} [{doc.getType()}] | Titre : {doc.titre} | Date : {doc.date}")

    def load_from_csv(self, filename="corpus_arxiv_reddit.csv"):
        try:
            df_source = pd.read_csv(filename, sep='\t', encoding='utf-8')
            for _, row in df_source.iterrows():
                self.add_document(
                    origine=row.get('origine', ''),
                    titre=row.get('titre', ''),
                    auteur=row.get('auteur', ''),
                    date=row.get('date', ''),
                    url=row.get('url', ''),
                    texte=row.get('texte', '')
                )
            print(f"Chargement réussi depuis '{filename}'.")
        except Exception as e:
            print(f"Erreur lors du chargement : {e}")

    def save(self, filename="corpus_sauvegarde.csv"):
        data = []
        for doc_id, doc in self.documents.items():
            data.append({
                "id": doc_id,
                "titre": doc.titre,
                "auteur": doc.auteur,
                "date": doc.date,
                "url": doc.url,
                "texte": doc.texte,
                "origine": doc.getType().lower()
            })
        df = pd.DataFrame(data)
        df.to_csv(filename, sep='\t', index=False, encoding='utf-8')
        print(f"Sauvegarde réussie dans '{filename}'.")

    def load(self, filename="corpus_sauvegarde.csv"):
        try:
            df = pd.read_csv(filename, sep='\t', encoding='utf-8')
            self.documents = {}
            self.authors = {}
            self.id_document = 0
            for _, row in df.iterrows():
                self.add_document(
                    origine=row.get('origine', ''),
                    titre=row.get('titre', ''),
                    auteur=row.get('auteur', ''),
                    date=row.get('date', ''),
                    url=row.get('url', ''),
                    texte=row.get('texte', '')
                )
            print(f"Rechargement réussi depuis '{filename}'.")
        except Exception as e:
            print(f"Erreur lors du rechargement : {e}")