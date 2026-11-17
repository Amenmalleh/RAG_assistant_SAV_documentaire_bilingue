"""Ingestion : lit les documents, les découpe, les vectorise, remplit pgvector."""
import os
import glob

from rag.base import get_connection, preparer_schema
from rag.decoupage import decouper
from rag.embeddings import vectoriser

DOSSIER = "documents"


def detecter_langue(texte):
    """Détecte grossièrement la langue : 'ar' si caractères arabes, sinon 'fr'."""
    for c in texte:
        if "\u0600" <= c <= "\u06ff":   # plage Unicode de l'arabe
            return "ar"
    return "fr"


def vider_base():
    """Supprime tous les chunks (pour réingérer proprement, sans doublons)."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("TRUNCATE chunks RESTART IDENTITY")
    conn.commit()
    conn.close()


def ingerer_fichier(chemin):
    """Découpe, vectorise et stocke un fichier texte. Renvoie (nb_chunks, langue)."""
    with open(chemin, encoding="utf-8") as f:
        texte = f.read()

    source = os.path.basename(chemin)
    langue = detecter_langue(texte)
    chunks = decouper(texte, taille_max=500, chevauchement=80)
    vecteurs = vectoriser(chunks)

    conn = get_connection()
    with conn.cursor() as cur:
        for chunk, vec in zip(chunks, vecteurs):
            cur.execute(
                "INSERT INTO chunks (contenu, source, langue, embedding) "
                "VALUES (%s, %s, %s, %s)",
                (chunk, source, langue, str(vec)),
            )
    conn.commit()
    conn.close()
    return len(chunks), langue


def main():
    preparer_schema()   # s'assure que la table existe
    vider_base()        # repart d'une base propre

    fichiers = glob.glob(os.path.join(DOSSIER, "*.txt"))
    if not fichiers:
        print(f"Aucun fichier .txt dans '{DOSSIER}/'. Ajoutez vos documents.")
        return

    total = 0
    for chemin in fichiers:
        n, langue = ingerer_fichier(chemin)
        print(f"  {os.path.basename(chemin)} [{langue}] -> {n} chunks")
        total += n
    print(f"\nTerminé : {total} chunks insérés dans la base.")


if __name__ == "__main__":
    main()