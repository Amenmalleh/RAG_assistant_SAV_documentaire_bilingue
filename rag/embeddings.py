"""Génération d'embeddings multilingues arabe/français (Module 3)."""
from sentence_transformers import SentenceTransformer

MODELE_NOM = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

_modele = None  # chargé une seule fois, à la demande


def get_modele():
    """Charge le modèle la première fois, puis le réutilise (singleton)."""
    global _modele
    if _modele is None:
        print(f"Chargement du modèle {MODELE_NOM} (une seule fois)...")
        _modele = SentenceTransformer(MODELE_NOM)
    return _modele


def vectoriser(textes):
    """Transforme un texte OU une liste de textes en vecteur(s).

    - Reçoit une str   -> renvoie un vecteur (liste de floats).
    - Reçoit une liste -> renvoie une liste de vecteurs.
    """
    modele = get_modele()
    un_seul = isinstance(textes, str)
    if un_seul:
        textes = [textes]

    vecteurs = modele.encode(textes)
    vecteurs = [v.tolist() for v in vecteurs]  # NumPy -> liste Python
    return vecteurs[0] if un_seul else vecteurs


def dimension():
    """Renvoie la dimension des vecteurs du modèle (384 ici)."""
    return get_modele().get_sentence_embedding_dimension()


if __name__ == "__main__":
    v = vectoriser("Comment annuler ma commande ?")
    print("Dimension :", len(v))
    print("5 premières valeurs :", [round(x, 4) for x in v[:5]])