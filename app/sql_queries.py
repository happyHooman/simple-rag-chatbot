"""SQL queries for the application."""

# Table creation
CREATE_FAQ_EMBEDDINGS_TABLE = """
CREATE TABLE IF NOT EXISTS faq_embeddings (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

# Read operations
GET_EMBEDDINGS_COUNT = "SELECT COUNT(*) FROM faq_embeddings"

GET_ALL_EMBEDDINGS = "SELECT id, question, answer FROM faq_embeddings ORDER BY id"

SIMILARITY_SEARCH = """
SELECT id, question, answer,
       (embedding <=> %s::vector) as distance,
       (1 - (embedding <=> %s::vector)) as similarity
FROM faq_embeddings
WHERE (1 - (embedding <=> %s::vector)) >= %s
ORDER BY embedding <=> %s::vector
LIMIT 1
"""

# Write operations
INSERT_EMBEDDING = (
    "INSERT INTO faq_embeddings (question, answer, embedding) "
    "VALUES (%s, %s, %s)"
)

UPDATE_EMBEDDING = (
    "UPDATE faq_embeddings SET answer = %s, embedding = %s WHERE id = %s"
)

DELETE_EMBEDDINGS_BY_IDS = "DELETE FROM faq_embeddings WHERE id = ANY(%s)"

DELETE_ALL_EMBEDDINGS = "DELETE FROM faq_embeddings"

# Health check queries
HEALTH_CHECK_PING = "SELECT 1"

HEALTH_CHECK_PGVECTOR = "SELECT 1 FROM pg_extension WHERE extname = 'vector'"

