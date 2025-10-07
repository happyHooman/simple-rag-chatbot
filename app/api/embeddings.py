import os
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import psycopg2
from openai import OpenAI

from ..config import settings
from ..config.logging_config import get_logger
from ..data.faq_database import faq_database
from ..sql_queries import (
    CREATE_FAQ_EMBEDDINGS_TABLE,
    DELETE_ALL_EMBEDDINGS,
    DELETE_EMBEDDINGS_BY_IDS,
    GET_ALL_EMBEDDINGS,
    GET_EMBEDDINGS_COUNT,
    INSERT_EMBEDDING,
    UPDATE_EMBEDDING,
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
logger = get_logger(__name__)


@contextmanager
def get_db_cursor(commit: bool = True) -> Generator[Any]:
    """Context manager for database operations."""
    conn = psycopg2.connect(settings.DATABASE_URL)
    cursor = conn.cursor()
    try:
        yield cursor
        if commit:
            conn.commit()
    finally:
        cursor.close()
        conn.close()


def create_embeddings(questions: list[str]) -> list[list[float]]:
    """Create embeddings for a list of questions."""
    response = client.embeddings.create(model="text-embedding-3-small", input=questions)
    return [embedding.embedding for embedding in response.data]


def get_embeddings_count() -> int:
    """Get the count of stored embeddings from the database."""
    try:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(GET_EMBEDDINGS_COUNT)
            result = cursor.fetchone()
            if result is not None:
                return int(result[0])
            return 0
    except Exception as e:
        logger.error(f"Failed to get embeddings count: {str(e)}")
        return 0


def generate_embeddings() -> dict[str, Any]:
    """Generate embeddings and store them in the database."""
    try:
        questions = [item["question"] for item in faq_database]
        logger.info(f"Generating embeddings for {len(questions)} questions")

        embeddings = create_embeddings(questions)
        logger.info(f"Generated {len(embeddings)} embeddings")

        with get_db_cursor() as cursor:
            cursor.execute(CREATE_FAQ_EMBEDDINGS_TABLE)
            cursor.execute(DELETE_ALL_EMBEDDINGS)
            logger.info("Cleared existing embeddings")

            for item, embedding in zip(faq_database, embeddings, strict=False):
                cursor.execute(INSERT_EMBEDDING, (item["question"], item["answer"], embedding))

        logger.info(f"Successfully stored {len(embeddings)} embeddings")
        return {"status": "success", "message": f"Stored {len(embeddings)} embeddings", "count": len(embeddings)}

    except Exception as e:
        logger.error(f"Failed to generate embeddings: {str(e)}")
        return {"status": "error", "message": f"Failed to generate embeddings: {str(e)}"}


def update_embeddings() -> dict[str, Any]:
    """Update embeddings by comparing with existing data."""
    try:
        with get_db_cursor() as cursor:
            # Get existing data from database
            cursor.execute(GET_ALL_EMBEDDINGS)
            existing_data = cursor.fetchall()

            # Convert to dict for easy lookup
            existing_items = {(row[1], row[2]): row[0] for row in existing_data}

            # Get current FAQ data
            current_items = {(item["question"], item["answer"]): item for item in faq_database}

            # Find items to add, update, or remove
            items_to_add = []
            items_to_update = []
            items_to_remove = []

            # Check for new items
            for key, item in current_items.items():
                if key not in existing_items:
                    items_to_add.append(item)

            # Check for removed items
            for key, db_id in existing_items.items():
                if key not in current_items:
                    items_to_remove.append(db_id)

            # Check for updated items (same question but different answer)
            for key, item in current_items.items():
                question, answer = key
                if question in [row[1] for row in existing_data]:
                    existing_item = next(row for row in existing_data if row[1] == question)
                    if existing_item[2] != answer:
                        items_to_update.append({
                            "id": existing_item[0],
                            "question": question,
                            "answer": answer,
                            "item": item
                        })

            logger.info(f"Update analysis: {len(items_to_add)} to add, {len(items_to_update)} to update, {len(items_to_remove)} to remove")

            # Process removals
            if items_to_remove:
                cursor.execute(DELETE_EMBEDDINGS_BY_IDS, (items_to_remove,))
                logger.info(f"Removed {len(items_to_remove)} obsolete embeddings")

            # Process updates
            if items_to_update:
                for update_item in items_to_update:
                    new_embedding = create_embeddings([update_item["question"]])[0]
                    cursor.execute(UPDATE_EMBEDDING, (update_item["answer"], new_embedding, update_item["id"]))
                logger.info(f"Updated {len(items_to_update)} embeddings")

            # Process additions
            if items_to_add:
                questions = [item["question"] for item in items_to_add]
                embeddings = create_embeddings(questions)
                for item, embedding in zip(items_to_add, embeddings, strict=False):
                    cursor.execute(INSERT_EMBEDDING, (item["question"], item["answer"], embedding))
                logger.info(f"Added {len(items_to_add)} new embeddings")

        total_changes = len(items_to_add) + len(items_to_update) + len(items_to_remove)

        return {
            "status": "success",
            "message": f"Updated embeddings: {len(items_to_add)} added, {len(items_to_update)} updated, {len(items_to_remove)} removed",
            "changes": {
                "added": len(items_to_add),
                "updated": len(items_to_update),
                "removed": len(items_to_remove),
                "total": total_changes
            }
        }

    except Exception as e:
        logger.error(f"Failed to update embeddings: {str(e)}")
        return {"status": "error", "message": f"Failed to update embeddings: {str(e)}"}
