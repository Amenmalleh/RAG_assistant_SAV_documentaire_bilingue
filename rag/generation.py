"""Génération de la réponse à partir des chunks récupérés — via Ollama (local)."""
import ollama

MODELE = "qwen2.5:3b"   # modèle local multilingue (arabe/français)

INSTRUCTIONS = """Tu es un assistant du service après-vente. Tu réponds \
UNIQUEMENT à partir du CONTEXTE fourni.
Règles strictes :
- N'utilise que les informations du contexte, jamais tes connaissances générales.
- Si le contexte ne permet pas de répondre, réponds exactement :
  "Je n'ai pas cette information dans mes documents."
- Cite la source entre crochets après chaque information, ex. [faq_ar.txt].
- Réponds dans la langue de la question (français ou arabe)."""


def generer(question, chunks):
    """Construit le prompt augmenté et renvoie la réponse du modèle local."""
    contexte = "\n\n".join(
        f"[Source : {c['source']}]\n{c['contenu']}" for c in chunks
    )
    reponse = ollama.chat(
        model=MODELE,
        messages=[
            {"role": "system", "content": INSTRUCTIONS},
            {"role": "user",
             "content": f"CONTEXTE :\n{contexte}\n\nQUESTION : {question}"},
        ],
    )
    return reponse["message"]["content"]


if __name__ == "__main__":
    from rag.recuperation import recuperer

    question = "Sous combien de temps suis-je remboursé ?"
    chunks = recuperer(question, k=5)
    print(f"Question : {question}\n")
    print("Réponse :\n")
    print(generer(question, chunks))