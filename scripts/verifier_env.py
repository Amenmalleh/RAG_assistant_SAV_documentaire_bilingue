"""Vérifie que l'environnement du projet RAG est complet et fonctionnel."""
import sys
import importlib
import subprocess

OK = "[ OK ]"
KO = "[MANQUE]"


def check_python():
    v = sys.version_info
    ok = v >= (3, 10)
    print(f"{OK if ok else KO} Python {v.major}.{v.minor}.{v.micro} (requis >= 3.10)")
    return ok


def check_package(nom_affichage, import_nom, pip_nom=None):
    try:
        mod = importlib.import_module(import_nom)
        version = getattr(mod, "__version__", "?")
        print(f"{OK} {nom_affichage} ({version})")
        return True
    except ImportError:
        print(f"{KO} {nom_affichage} — lancez : pip install {pip_nom or nom_affichage}")
        return False


def check_docker():
    try:
        r = subprocess.run(
            ["docker", "ps", "--filter", "name=rag-postgres", "--format", "{{.Status}}"],
            capture_output=True, text=True, timeout=10,
        )
        statut = r.stdout.strip()
        ok = statut.startswith("Up")
        print(f"{OK if ok else KO} Conteneur rag-postgres : {statut or 'absent'}")
        return ok
    except Exception as e:
        print(f"{KO} Docker introuvable ou arrêté ({e})")
        return False


def check_env():
    import os
    from dotenv import load_dotenv
    load_dotenv()
    ok = True
    for cle in ["ANTHROPIC_API_KEY", "DB_NAME", "DB_USER", "DB_PASSWORD"]:
        present = bool(os.getenv(cle))
        print(f"{OK if present else KO} Variable {cle} {'définie' if present else 'absente dans .env'}")
        ok = ok and present
    return ok


def check_db():
    try:
        from rag.base import get_connection
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
            row = cur.fetchone()
        conn.close()
        if row:
            print(f"{OK} PostgreSQL joignable, pgvector v{row[0]} actif")
            return True
        print(f"{KO} Connecté mais extension pgvector absente")
        return False
    except Exception as e:
        print(f"{KO} Connexion PostgreSQL impossible ({e})")
        return False


if __name__ == "__main__":
    print("=== Vérification de l'environnement RAG ===\n")
    resultats = [
        check_python(),
        check_package("numpy", "numpy"),
        check_package("anthropic", "anthropic"),
        check_package("sentence-transformers", "sentence_transformers"),
        check_package("psycopg2", "psycopg2", "psycopg2-binary"),
        check_package("python-dotenv", "dotenv", "python-dotenv"),
        check_docker(),
        check_env(),
        check_db(),
    ]
    print()
    if all(resultats):
        print("Tout est prêt. On peut démarrer la Partie 1.")
    else:
        print("Des éléments manquent — corrigez les lignes [MANQUE] ci-dessus.")