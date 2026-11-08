import pandas as pd
import numpy as np
from Corpus import Corpus

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
        query_nettoye = self.corpus.nettoyer_texte(query)
        mots_requete = query_nettoye.split()
        
        if not mots_requete:
            return pd.DataFrame(columns=['id_doc', 'titre', 'score'])

        nb_mots = len(self.corpus.vocab)
        vec_requete = np.zeros(nb_mots)
        
        for mot in mots_requete:
            if mot in self.corpus.vocab:
                j = self.corpus.vocab[mot]['id']
                vec_requete[j] += 1.0  # TF de la requête

        mat_docs = self.corpus.mat_TFxIDF.toarray()
        norme_requete = np.linalg.norm(vec_requete)
        normes_docs = np.linalg.norm(mat_docs, axis=1)
        
        scores = np.zeros(len(mat_docs))
        if norme_requete > 0:
            produit_scalaire = np.dot(mat_docs, vec_requete)
            denominateur = normes_docs * norme_requete
            scores = np.divide(produit_scalaire, denominateur, out=np.zeros_like(produit_scalaire), where=denominateur!=0)

        indices_tries = np.argsort(scores)[::-1][:n]
        doc_ids = list(self.corpus.documents.keys())
        
        resultats = []
        for idx in indices_tries:
            if scores[idx] > 0:
                doc_id = doc_ids[idx]
                doc = self.corpus.documents[doc_id]
                resultats.append({
                    'id_doc': doc_id,
                    'titre': getattr(doc, 'titre', 'Sans titre'),
                    'score': scores[idx]
                })

        return pd.DataFrame(resultats)