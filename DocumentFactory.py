from Document import RedditDocument, ArxivDocument, Document

class DocumentFactory:
    @staticmethod
    def create_document(origine, **kwargs):
        origine_lower = str(origine).lower()
        if origine_lower == 'reddit':
            return RedditDocument(
                titre=kwargs.get('titre', ''),
                auteur=kwargs.get('auteur', ''),
                date=kwargs.get('date', ''),
                url=kwargs.get('url', ''),
                texte=kwargs.get('texte', ''),
                nb_commentaires=kwargs.get('nb_commentaires', 0),
                subreddit=kwargs.get('subreddit', '')
            )
        elif origine_lower == 'arxiv':
            return ArxivDocument(
                titre=kwargs.get('titre', ''),
                auteur=kwargs.get('auteur', ''),
                date=kwargs.get('date', ''),
                url=kwargs.get('url', ''),
                texte=kwargs.get('texte', ''),
                co_auteurs=kwargs.get('co_auteurs', []),
                categories=kwargs.get('categories', [])
            )
        else:
            return Document(
                titre=kwargs.get('titre', ''),
                auteur=kwargs.get('auteur', ''),
                date=kwargs.get('date', ''),
                url=kwargs.get('url', ''),
                texte=kwargs.get('texte', '')
            )