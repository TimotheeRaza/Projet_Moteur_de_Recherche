import streamlit as st
import pandas as pd
from Corpus import Corpus
from SearchEngine import SearchEngine

st.set_page_config(
    page_title="Gogole Climb",
    page_icon="🔍",
    layout="centered"
)

st.markdown("""
    <style>
        .main {
            background-color: #ffffff;
        }
        .gogole-title {
            font-family: 'Product Sans', Arial, sans-serif;
            font-size: 4rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 0px;
            letter-spacing: -2px;
        }
        /* Couleurs inspirées du logo Google */
        .lettre-g1 { color: #4285F4; }
        .lettre-o1 { color: #EA4335; }
        .lettre-g2 { color: #FBBC05; }
        .lettre-o2 { color: #4285F4; }
        .lettre-l  { color: #34A853; }
        .lettre-e  { color: #EA4335; }
        
        .sub-title {
            color: #5f6368;
            text-align: center;
            font-size: 1.1rem;
            margin-bottom: 30px;
        }
        .result-title {
            color: #1a0dab;
            font-size: 1.2rem;
            text-decoration: none;
            font-weight: 500;
        }
        .result-snippet {
            color: #4d5156;
            font-size: 0.95rem;
        }
        .result-url {
            color: #006621;
            font-size: 0.85rem;
        }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialiser_moteur():
    corpus = Corpus("Corpus M1 Arxiv & Reddit")
    corpus.load_from_csv("corpus_arxiv_reddit.csv")
    moteur = SearchEngine(corpus)
    return moteur

with st.spinner("Chargement de Gogole Climb..."):
    moteur = initialiser_moteur()

st.markdown("""
    <div class="gogole-title">
        <span class="lettre-g1">G</span><span class="lettre-o1">o</span><span class="lettre-g2">g</span><span class="lettre-o2">o</span><span class="lettre-l">l</span><span class="lettre-e">e</span> Climb
    </div>
    <div class="sub-title">Le moteur de recherche conçu pour l'escalade</div>
""", unsafe_allow_html=True)

col_search_1, col_search_2 = st.columns([5, 1])

with col_search_1:
    requete = st.text_input("Recherche Gogole", placeholder="Rechercher des articles ou des posts...", label_visibility="collapsed")

with col_search_2:
    bouton_recherche = st.button("Rechercher", type="primary", use_container_width=True)

with st.expander("🛠️ Outils de recherche (Filtres)"):
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        source_filtre = st.selectbox("Source :", options=["Tous", "reddit", "arxiv"])
    with col_f2:
        nb_resultats = st.slider("Nombre de résultats max :", min_value=1, max_value=20, value=5)

if bouton_recherche or requete:
    if not requete.strip():
        st.warning("Veuillez saisir un terme de recherche.")
    else:
        try:
            resultats = moteur.search(requete)
        except AttributeError:
            resultats = moteur.rechercher(requete)

        if isinstance(resultats, pd.DataFrame):
            df_res = resultats.copy()
        else:
            df_res = pd.DataFrame(resultats)

        if source_filtre != "Tous" and not df_res.empty:
            if 'origine' in df_res.columns:
                df_res = df_res[df_res['origine'] == source_filtre]
            else:
                ids_filtres = [
                    doc_id for doc_id, doc in moteur.corpus.documents.items() 
                    if doc.origine == source_filtre
                ]
                df_res = df_res[df_res['id_doc'].isin(ids_filtres)]

        st.markdown(f"<p style='color: #70757a; font-size: 0.9rem;'>Environ {len(df_res)} résultats trouvés</p>", unsafe_allow_html=True)
        st.markdown("<hr style='border: 0; border-top: 1px solid #dfe1e5; margin-bottom: 20px;'>", unsafe_allow_html=True)

        if df_res.empty:
            st.info("Aucun document ne correspond à votre recherche sur Gogole Climb.")
        else:
            for index, row in df_res.head(nb_resultats).iterrows():
                doc_id = row.get('id_doc', index)
                score = row.get('score', 0.0)
                titre = row.get('titre', 'Sans titre')
                
                origine_doc = "inconnu"
                texte_complet = ""
                if doc_id in moteur.corpus.documents:
                    doc_obj = moteur.corpus.documents[doc_id]
                    origine_doc = doc_obj.origine.upper()
                    texte_complet = doc_obj.texte

                st.markdown(f"<div class='result-url'>gogole-climb.local › {origine_doc.lower()} › doc_{doc_id} (Score TF-IDF : {score:.4f})</div>", unsafe_allow_html=True)
                st.markdown(f"<a class='result-title' href='#'>{titre}</a>", unsafe_allow_html=True)
                
                snippet = texte_complet[:200] + "..." if len(texte_complet) > 200 else texte_complet
                st.markdown(f"<div class='result-snippet'>{snippet}</div>", unsafe_allow_html=True)
                
                with st.expander("📄 Lire le document complet"):
                    st.write(texte_complet)
                
                st.markdown("<br>", unsafe_allow_html=True)