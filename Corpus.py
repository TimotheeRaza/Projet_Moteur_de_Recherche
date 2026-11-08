import re
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from Document import Document
from Author import Author

class Corpus:
    _instance = None

    def __new__(cls, nom=""):
        if cls._instance is None:
            cls._instance = super(Corpus, cls).__new__(cls)
            cls._instance.nom = nom
            cls._instance.documents = {}
            cls._instance.authors = {}
            cls._instance._texte_global = None
            cls._instance.df_stats = None
            cls._instance.vocab = {}
            cls._instance.mat_TF = None
            cls._instance.mat_TFxIDF = None
        return cls._instance

    def __init__(self, nom=""):
        if nom and not self.nom:
            self.nom = nom

    def __repr__(self):
        return f"Corpus(nom='{self.nom}', nb_documents={len(self.documents)}, nb_auteurs={len(self.authors)})"

    def add_document(self, doc: Document):
        if doc.id_doc not in self.documents:
            self.documents[doc.id_doc] = doc
            self._texte_global = None
            
            auteur_nom = doc.auteur
            if auteur_nom not in self.authors:
                self.authors[auteur_nom] = Author(auteur_nom)
            self.authors[auteur_nom].add(doc)

    def load_from_csv(self, filename):
        df = pd.read_csv(filename, sep='\t', encoding='utf-8')
        for _, row in df.iterrows():
            from DocumentFactory import DocumentFactory
            doc = DocumentFactory.create_document(
                id_doc=row['id'],
                titre=row.get('titre', 'Sans titre'),
                auteur=row.get('origine', 'Inconnu'),
                date=row.get('date', '2026'),
                texte=row['texte'],
                type_doc=row.get('origine', 'document')
            )
            self.add_document(doc)

    def save(self, filename):
        data = [{
            'id': doc.id_doc,
            'titre': getattr(doc, 'titre', ''),
            'origine': doc.auteur,
            'date': getattr(doc, 'date', ''),
            'texte': doc.texte
        } for doc in self.documents.values()]
        pd.DataFrame(data).to_csv(filename, sep='\t', index=False, encoding='utf-8')

    def _get_texte_global(self):
        if self._texte_global is None:
            self._texte_global = " ".join(str(doc.texte) for doc in self.documents.values() if doc.texte)
        return self._texte_global

    def search_regex(self, motif):
        texte_global = self._get_texte_global()
        return re.findall(motif, texte_global, re.IGNORECASE)

    def concorde(self, motif, taille_contexte=30):
        texte_global = self._get_texte_global()
        pattern = re.compile(rf"(.{{0,{taille_contexte}}})({motif})(.{{0,{taille_contexte}}})", re.IGNORECASE)
        gauche, motif_trouve, droit = [], [], []
        for match in pattern.finditer(texte_global):
            gauche.append(match.group(1))
            motif_trouve.append(match.group(2))
            droit.append(match.group(3))
        return pd.DataFrame({'contexte gauche': gauche, 'motif trouvé': motif_trouve, 'contexte droit': droit})

    def nettoyer_texte(self, texte):
        if not isinstance(texte, str):
            return ""
        texte = texte.lower()
        texte = re.sub(r'[\n\t]+', ' ', texte)
        texte = re.sub(r'[^a-zà-ÿ\s]', ' ', texte)
        return re.sub(r'\s+', ' ', texte).strip()

    def calculer_statistiques(self):
        vocabulaire_dict = {}
        df_docs_contenant_mot = {}

        for doc in self.documents.values():
            mots = self.nettoyer_texte(doc.texte).split()
            mots_uniques = set(mots)
            for mot in mots:
                vocabulaire_dict[mot] = vocabulaire_dict.get(mot, 0) + 1
            for mot in mots_uniques:
                df_docs_contenant_mot[mot] = df_docs_contenant_mot.get(mot, 0) + 1

        data_stats = [{
            'mot': mot, 
            'frequence_totale': freq, 
            'doc_frequency': df_docs_contenant_mot.get(mot, 0)
        } for mot, freq in vocabulaire_dict.items()]
        self.df_stats = pd.DataFrame(data_stats).set_index('mot')

    def construire_vocabulaire_et_matrices(self):
        if self.df_stats is None or self.df_stats.empty:
            self.calculer_statistiques()

        mots_tries = sorted(self.df_stats.index.tolist())
        self.vocab = {
            mot: {
                'id': idx,
                'frequence_totale': self.df_stats.loc[mot, 'frequence_totale'],
                'doc_frequency': self.df_stats.loc[mot, 'doc_frequency']
            }
            for idx, mot in enumerate(mots_tries)
        }

        doc_ids = list(self.documents.keys())
        nb_docs = len(doc_ids)
        nb_mots = len(self.vocab)

        rows, cols, data = [], [], []
        for i, doc_id in enumerate(doc_ids):
            doc = self.documents[doc_id]
            mots = self.nettoyer_texte(doc.texte).split()
            freqs_doc = {}
            for mot in mots:
                if mot in self.vocab:
                    freqs_doc[mot] = freqs_doc.get(mot, 0) + 1
            for mot, tf in freqs_doc.items():
                j = self.vocab[mot]['id']
                rows.append(i)
                cols.append(j)
                data.append(tf)

        self.mat_TF = csr_matrix((data, (rows, cols)), shape=(nb_docs, nb_mots), dtype=float)

        idf = np.zeros(nb_mots)
        for mot, info in self.vocab.items():
            j = info['id']
            df = info['doc_frequency']
            idf[j] = np.log(nb_docs / df) if df > 0 else 0.0

        self.mat_TFxIDF = self.mat_TF.multiply(idf)


class SearchEngine:
    """
    Moteur de recherche basé sur le corpus, la matrice TF-IDF 
    et la mesure de similarité cosinus.
    """
    def __init__(self, corpus: Corpus):
        self.corpus = corpus
        if self.corpus.mat_TFxIDF is None:
            self.corpus.construire_vocabulaire_et_matrices()

    def search(self, query: str, n=5) -> pd.DataFrame:
        """
        Prend une requête textuelle, calcule la similarité cosinus avec les documents,
        et retourne un DataFrame pandas des n meilleurs résultats.
        """
        # 1. Nettoyer et découper la requête
        query_nettoye = self.corpus.nettoyer_texte(query)
        mots_requete = query_nettoye.split()
        
        if not mots_requete:
            print("Requête vide ou invalide.")
            return pd.DataFrame(columns=['id_doc', 'titre', 'score'])

        # 2. Construire le vecteur de la requête sur le vocabulaire
        nb_mots = len(self.corpus.vocab)
        vec_requete = np.zeros(nb_mots)
        
        for mot in mots_requete:
            if mot in self.corpus.vocab:
                j = self.corpus.vocab[mot]['id']
                vec_requete[j] += 1.0  # TF de la requête

        # 3. Calculer la similarité cosinus entre le vecteur requête et la matrice TF-IDF des documents
        mat_docs = self.corpus.mat_TFxIDF.toarray()
        
        # Normes L2 pour la similarité cosinus
        norme_requete = np.linalg.norm(vec_requete)
        normes_docs = np.linalg.norm(mat_docs, axis=1)
        
        scores = np.zeros(len(mat_docs))
        if norme_requete > 0:
            produit_scalaire = np.dot(mat_docs, vec_requete)
            denominateur = normes_docs * norme_requete
            # Éviter la division par zéro
            scores = np.divide(produit_scalaire, denominateur, out=np.zeros_like(produit_scalaire), where=denominateur!=0)

        # 4. Trier les documents par score décroissant et récupérer les top n
        indices_tries = np.argsort(scores)[::-1][:n]
        
        doc_ids = list(self.corpus.documents.keys())
        resultats = []
        for idx in indices_tries:
            if scores[idx] > 0:  # Ne garder que les documents pertinents
                doc_id = doc_ids[idx]
                doc = self.corpus.documents[doc_id]
                resultats.append({
                    'id_doc': doc_id,
                    'titre': getattr(doc, 'titre', 'Sans titre'),
                    'score': scores[idx]
                })

        return pd.DataFrame(resultats)