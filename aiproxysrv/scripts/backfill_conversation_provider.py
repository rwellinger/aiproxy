#!/usr/bin/env python3
"""
Backfill provider field for existing conversations.
Sets all existing conversations to 'internal' (Ollama).
Run this once after adding the provider field to conversations table.
"""
import sys
sys.path.insert(0, 'src')

from db.database import SessionLocal
from db.models import Conversation
from utils.logger import logger


def backfill_provider():
    """Set provider='internal' for all existing conversations."""
    db = SessionLocal()

    try:
        # Get all conversations without provider set (or with default)
        conversations = db.query(Conversation).all()
        updated_count = 0

        for conv in conversations:
            # Set provider to 'internal' if not already set or if default
            if not conv.provider or conv.provider == 'internal':
                conv.provider = 'internal'
                updated_count += 1

                logger.info(
                    f"Updated conversation {conv.id}",
                    title=conv.title,
                    model=conv.model,
                    provider='internal'
                )

        db.commit()

        print(f"\n✓ Updated {updated_count} conversations to provider='internal'")
        print(f"  Total conversations: {len(conversations)}")

        # Show summary by model
        print("\nConversations by model:")
        model_counts = {}
        for conv in conversations:
            if conv.model not in model_counts:
                model_counts[conv.model] = 0
            model_counts[conv.model] += 1

        for model, count in sorted(model_counts.items()):
            print(f"  {model}: {count} conversations")

    except Exception as e:
        db.rollback()
        logger.error(f"Error backfilling provider field: {e}")
        print(f"\n✗ Error: {e}")
        return False
    finally:
        db.close()

    return True


if __name__ == "__main__":
    print("Backfilling provider field for existing conversations...")
    success = backfill_provider()
    sys.exit(0 if success else 1)
