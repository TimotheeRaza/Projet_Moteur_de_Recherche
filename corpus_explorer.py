from Corpus import Corpus

# 1. Test du Singleton
mon_corpus = Corpus("Mon Corpus Escalade")
print(mon_corpus)

autre_tentative = Corpus("Corpus en double")
print("Vérification Singleton (c1 is c2) :", mon_corpus is autre_tentative)

# 2. Chargement des données
mon_corpus.load_from_csv("corpus_arxiv_reddit.csv")
print(mon_corpus)

# 3. Test des statistiques d'un auteur
nom_recherche = input("\nEntrez le nom d'un auteur pour voir ses statistiques : ").strip()

if nom_recherche in mon_corpus.authors:
    auteur_obj = mon_corpus.authors[nom_recherche]
    print(f"\n--- Statistiques pour {auteur_obj.name} ---")
    print(f"Nombre de documents produits : {auteur_obj.nb_docs}")
    
    total_caracteres = sum(len(doc.texte) for doc in auteur_obj.production.values())
    taille_moyenne = total_caracteres / auteur_obj.nb_docs if auteur_obj.nb_docs > 0 else 0
    
    print(f"Taille moyenne des documents : {taille_moyenne:.2f} caractères")
else:
    print(f"Aucun auteur trouvé sous le nom de '{nom_recherche}'.")

# 4. Test des tris
mon_corpus.afficher_documents_tries(n=5, critere="date")
mon_corpus.afficher_documents_tries(n=5, critere="titre")

# 5. Test de la sauvegarde
mon_corpus.save("mon_corpus_sauvegarde.csv")