"""Récupération des chunks les plus proches d'une question (Module 6)."""
from rag.base import get_connection
from rag.embeddings import vectoriser


def recuperer(question, k=5, seuil=1.0, langue=None):
    """Renvoie les k chunks les plus proches de la question.

    - seuil  : distance cosinus maximale acceptée (0 = identique, 2 = opposé).
    - langue : 'fr', 'ar' ou None (toutes langues) -> filtrage par métadonnée.
    """
    vec = vectoriser(question)

    sql = """
        SELECT contenu, source, langue, embedding <=> %(q)s AS distance
        FROM chunks
    """
    params = {"q": str(vec), "k": k}
    if langue:
        sql += " WHERE langue = %(langue)s"
        params["langue"] = langue
    sql += " ORDER BY embedding <=> %(q)s LIMIT %(k)s"

    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(sql, params)
        lignes = cur.fetchall()
    conn.close()

    return [
        {"contenu": c, "source": s, "langue": lg, "distance": float(d)}
        for (c, s, lg, d) in lignes
        #if d < seuil
    ]


if __name__ == "__main__":
    question = "Quand serai-je remboursé ?"
    print(f"Question : {question}\n")
    for c in recuperer(question, k=3):
        print(f"[distance {c['distance']:.3f}] ({c['source']}, {c['langue']})")
        print(f"  {c['contenu'][:90]}...\n")