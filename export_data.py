import os
import re
import urllib.request
import xmltodict
from dotenv import load_dotenv
import pandas as pd
import praw
import ssl

load_dotenv()

TAILLE_REDDIT = 5000
TAILLE_ARXIV = 5000
THEMATIQUE_ARXIV = "climbing"
SUBREDDIT_NOM = "Climbing"
FICHIER_SAUVEGARDE = "corpus_arxiv_reddit.csv"

tous_les_textes = []
toutes_les_origines = []

# 1.1 Acquisition Reddit
try:
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT")
    )
    subr = reddit.subreddit(SUBREDDIT_NOM)
    posts = list(subr.hot(limit=TAILLE_REDDIT))

    for post in posts:
        titre = post.title or ""
        corps = post.selftext if post.selftext else (post.url or "")
        texte_brut = f"{titre}. {corps}"
        texte_propre = re.sub(r'\s+', ' ', texte_brut).strip()
        
        tous_les_textes.append(texte_propre)
        toutes_les_origines.append("reddit")

    print(f"Reddit : {len([o for o in toutes_les_origines if o == 'reddit'])} posts récupérés.")
except Exception as e:
    print(f"Erreur Reddit : {e}")

# 1.2 Acquisition Arxiv
try:
    url_arxiv = f"http://export.arxiv.org/api/query?search_query=all:{THEMATIQUE_ARXIV}&start=0&max_results={TAILLE_ARXIV}"
    contexte_ssl = ssl._create_unverified_context()
    
    with urllib.request.urlopen(url_arxiv, context=contexte_ssl) as response:
        xml_data = response.read().decode('utf-8')
        
    data_dict = xmltodict.parse(xml_data)
    entries = data_dict.get('feed', {}).get('entry', [])
    if isinstance(entries, dict):
        entries = [entries]

    nb_arxiv = 0
    for entry in entries:
        titre_art = entry.get('title', '')
        if isinstance(titre_art, dict):
            titre_art = titre_art.get('#text', '')
            
        resume_art = entry.get('summary', '')
        if isinstance(resume_art, dict):
            resume_art = resume_art.get('#text', '')
            
        texte_brut_arxiv = f"{titre_art}. {resume_art}"
        texte_propre_arxiv = re.sub(r'\s+', ' ', texte_brut_arxiv).strip()
        
        tous_les_textes.append(texte_propre_arxiv)
        toutes_les_origines.append("arxiv")
        nb_arxiv += 1

    print(f"Arxiv : {nb_arxiv} articles récupérés.")
except Exception as e:
    print(f"Erreur Arxiv : {e}")

# 2. Sauvegarde et rechargement (Pandas)
df_corpus = pd.DataFrame({
    'id': range(len(tous_les_textes)),
    'texte': tous_les_textes,
    'origine': toutes_les_origines
})

df_corpus.to_csv(FICHIER_SAUVEGARDE, sep='\t', index=False, encoding='utf-8')
print(f"Corpus sauvegardé dans '{FICHIER_SAUVEGARDE}'.")

df_recharge = pd.read_csv(FICHIER_SAUVEGARDE, sep='\t', encoding='utf-8')
print(f"Corpus rechargé : {len(df_recharge)} lignes en mémoire.")