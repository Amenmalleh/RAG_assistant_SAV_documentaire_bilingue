"""Découpage d'un texte en chunks, en respectant les paragraphes (Module 4)."""


def decouper(texte, taille_max=500, chevauchement=80):
    """Découpe `texte` en chunks d'au plus `taille_max` caractères.

    - On coupe d'abord sur les paragraphes (double saut de ligne).
    - Quand un chunk est plein, le suivant reprend les `chevauchement`
      derniers caractères du précédent, coupés sur une frontière de mot,
      pour ne pas trancher une idée en deux.
    """
    paragraphes = [p.strip() for p in texte.split("\n\n") if p.strip()]

    chunks = []
    courant = ""
    for para in paragraphes:
        if len(courant) + len(para) + 2 > taille_max and courant:
            chunks.append(courant.strip())
            courant = _queue(courant, chevauchement)
        courant = (courant + "\n\n" + para).strip()

    if courant.strip():
        chunks.append(courant.strip())
    return chunks


def _queue(texte, n):
    """Renvoie les ~n derniers caractères de `texte`, coupés sur un espace."""
    if len(texte) <= n:
        return texte
    morceau = texte[-n:]
    espace = morceau.find(" ")
    return morceau[espace + 1:] if espace != -1 else morceau


if __name__ == "__main__":
    exemple = """Politique de retour.

Tout article peut être retourné sous 14 jours après réception.
Le produit doit être dans son emballage d'origine.

Remboursement.

Le remboursement est effectué sous 5 jours ouvrés sur le moyen de paiement initial."""

    for i, c in enumerate(decouper(exemple, taille_max=120, chevauchement=20)):
        print(f"--- chunk {i} ({len(c)} car.) ---\n{c}\n")