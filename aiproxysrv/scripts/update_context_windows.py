#!/usr/bin/env python3
"""
Update existing conversations with correct context window sizes.
Run this once after adding token tracking.
"""

import sys


sys.path.insert(0, "src")

from config.model_context_windows import get_context_window_size
from db.database import SessionLocal
from db.models import Conversation
from utils.logger import logger


def update_context_windows():
    """Update all conversations with correct context window sizes."""
    db = SessionLocal()

    try:
        conversations = db.query(Conversation).all()
        updated_count = 0

        for conv in conversations:
            correct_size = get_context_window_size(conv.model)

            if conv.context_window_size != correct_size:
                old_size = conv.context_window_size
                conv.context_window_size = correct_size
                updated_count += 1

                logger.info(
                    f"Updated conversation {conv.id}", model=conv.model, old_size=old_size, new_size=correct_size
                )

        db.commit()

        print(f"\n✓ Updated {updated_count} conversations")
        print(f"  Total conversations: {len(conversations)}")

        # Show summary
        print("\nContext window sizes by model:")
        model_sizes = {}
        for conv in conversations:
            if conv.model not in model_sizes:
                model_sizes[conv.model] = get_context_window_size(conv.model)

        for model, size in sorted(model_sizes.items()):
            print(f"  {model}: {size:,} tokens")

    except Exception as e:
        db.rollback()
        logger.error(f"Error updating context windows: {e}")
        print(f"\n✗ Error: {e}")
        return False
    finally:
        db.close()

    return True


if __name__ == "__main__":
    print("Updating conversation context window sizes...")
    success = update_context_windows()
    sys.exit(0 if success else 1)
