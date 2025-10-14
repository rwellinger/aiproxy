"""
Celery App Package
Exportiert die wichtigsten Objekte für einfachen Import
"""

from .celery_config import celery_app
from .slot_manager import get_slot_status
from .tasks import generate_instrumental_task, generate_song_task


__all__ = ["celery_app", "generate_song_task", "generate_instrumental_task", "get_slot_status"]
