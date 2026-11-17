import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """Ouvre une connexion PostgreSQL à partir du .env."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "ragdb"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
    )

def preparer_schema(dimension=384):
    """Active pgvector, crée la table chunks + l'index HNSW (idempotent)."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS chunks (
                id        BIGSERIAL PRIMARY KEY,
                contenu   TEXT NOT NULL,
                source    TEXT,
                langue    TEXT,
                embedding vector({dimension}) NOT NULL
            )
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_chunks_emb ON chunks
            USING hnsw (embedding vector_cosine_ops)
        """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    preparer_schema()
    print("Base prête : table chunks + index HNSW créés.")