"""Compression Controller - Handles chat compression with archival."""
import traceback
import uuid
from datetime import datetime
from typing import Tuple, Dict, Any, List
from sqlalchemy.orm import Session

from db.models import Conversation, Message, MessageArchive
from utils.logger import logger
from api.controllers.openai_chat_controller import OpenAIChatController, OpenAIAPIError as OpenAIError
from config.settings import OLLAMA_URL, OLLAMA_TIMEOUT
import requests


class CompressionController:
    """Controller for compressing conversations by archiving old messages and creating AI summaries."""

    def compress_conversation(
        self, db: Session, conversation_id: uuid.UUID, user_id: uuid.UUID, keep_recent: int = 10
    ) -> Tuple[Dict[str, Any], int]:
        """
        Compress a conversation by archiving old messages and creating an AI summary.

        Strategy:
        1. Keep all system messages (never compress)
        2. Keep last N recent user/assistant messages
        3. Archive older messages
        4. Create AI summary of archived messages
        5. Insert summary as new system message
        6. Recalculate token count

        Args:
            db: Database session
            conversation_id: Conversation UUID
            user_id: User UUID
            keep_recent: Number of recent messages to keep (default: 10)

        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get conversation
            conversation = (
                db.query(Conversation)
                .filter(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id,
                )
                .first()
            )

            if not conversation:
                return {"error": "Conversation not found"}, 404

            # Get all messages
            all_messages = (
                db.query(Message)
                .filter(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.asc())
                .all()
            )

            # Separate protected (system) from compressible (user/assistant)
            protected_messages = [m for m in all_messages if m.role == "system"]
            compressible_messages = [m for m in all_messages if m.role in ["user", "assistant"]]

            # Check if compression is needed
            if len(compressible_messages) <= keep_recent:
                return {
                    "message": "No compression needed",
                    "details": f"Only {len(compressible_messages)} compressible messages"
                }, 200

            # Split into old (to archive) and recent (to keep)
            old_messages = compressible_messages[:-keep_recent]
            recent_messages = compressible_messages[-keep_recent:]

            logger.info(
                "Compression analysis",
                conversation_id=str(conversation_id),
                total_messages=len(all_messages),
                protected=len(protected_messages),
                old=len(old_messages),
                recent=len(recent_messages),
            )

            # Create AI summary of old messages
            summary_content, summary_token_count = self._create_ai_summary(
                old_messages,
                conversation.model,
                conversation.provider
            )

            # Create summary message as 'assistant' (not 'system') so it can be compressed later
            # Keep prefix very short to minimize tokens
            summary_message = Message(
                id=uuid.uuid4(),
                conversation_id=conversation_id,
                role="assistant",  # Changed from 'system' to allow future compression
                content=f"[Summary: {len(old_messages)} msgs archived]\n{summary_content}",
                is_summary=True,
                token_count=summary_token_count,  # Use actual token count from AI
                created_at=datetime.utcnow(),
            )
            db.add(summary_message)
            db.flush()  # Get summary_message.id

            # Archive old messages
            archived_count = self._archive_messages(db, old_messages, summary_message.id)

            # Recalculate token count
            remaining_messages = (
                db.query(Message)
                .filter(Message.conversation_id == conversation_id)
                .all()
            )
            total_tokens = sum([m.token_count or 0 for m in remaining_messages])
            conversation.current_token_count = total_tokens
            conversation.updated_at = datetime.utcnow()

            db.commit()

            logger.info(
                "Conversation compressed successfully",
                conversation_id=str(conversation_id),
                archived_count=archived_count,
                new_token_count=total_tokens,
            )

            return {
                "message": "Conversation compressed successfully",
                "archived_messages": archived_count,
                "summary_created": True,
                "new_token_count": total_tokens,
                "token_percentage": (total_tokens / conversation.context_window_size) * 100
            }, 200

        except Exception as e:
            db.rollback()
            logger.error(
                "Error compressing conversation",
                conversation_id=str(conversation_id),
                error_type=type(e).__name__,
                error=str(e),
                stacktrace=traceback.format_exc(),
            )
            return {"error": f"Failed to compress conversation: {e}"}, 500

    def _create_ai_summary(
        self, messages: List[Message], model: str, provider: str
    ) -> Tuple[str, int]:
        """
        Create AI summary of messages using the conversation's model.

        Args:
            messages: List of messages to summarize
            model: Model name
            provider: Provider ('internal' or 'external')

        Returns:
            Tuple of (summary_text, token_count)

        Raises:
            Exception: If AI summary creation fails
        """
        # Build prompt for summarization (keep it very brief to reduce tokens)
        conversation_text = "\n".join([
            f"{msg.role}: {msg.content[:200]}"  # Limit each message to 200 chars
            for msg in messages[:10]  # Only include first 10 messages
        ])

        summary_prompt = f"""Summarize this conversation in MAX 5 bullet points (max 50 words total):

{conversation_text}

Brief summary:"""

        summary_messages = [
            {"role": "system", "content": "You are a helpful assistant that creates concise conversation summaries."},
            {"role": "user", "content": summary_prompt}
        ]

        try:
            if provider == "external":
                # Use OpenAI
                openai_controller = OpenAIChatController()
                content, prompt_tokens, completion_tokens = openai_controller.send_chat_message(
                    model=model,
                    messages=summary_messages
                )
                # For OpenAI, we only care about completion tokens (the summary itself)
                token_count = completion_tokens
            else:
                # Use Ollama
                api_url = f"{OLLAMA_URL}/api/chat"
                payload = {
                    "model": model,
                    "messages": summary_messages,
                    "stream": False,
                }

                resp = requests.post(api_url, json=payload, timeout=OLLAMA_TIMEOUT)
                resp.raise_for_status()
                resp_json = resp.json()

                if "message" in resp_json and "content" in resp_json["message"]:
                    content = resp_json["message"]["content"]
                    # Get token count from Ollama response (eval_count = completion tokens)
                    token_count = resp_json.get("eval_count", len(content.split()))
                else:
                    raise Exception("Invalid Ollama API response")

            logger.info("AI summary created successfully", provider=provider, token_count=token_count)
            return content, token_count

        except Exception as e:
            logger.error(
                "Failed to create AI summary",
                error=str(e),
                provider=provider
            )
            # Fallback: Create simple text summary
            fallback_summary = f"Summary of {len(messages)} messages:\n" + "\n".join([
                f"- {msg.role}: {msg.content[:100]}..."
                for msg in messages[:5]
            ])
            # Rough token estimate for fallback
            fallback_token_count = len(fallback_summary.split())
            return fallback_summary, fallback_token_count

    def _archive_messages(
        self, db: Session, messages: List[Message], summary_id: uuid.UUID
    ) -> int:
        """
        Archive messages by moving them to messages_archive table.

        Args:
            db: Database session
            messages: List of messages to archive
            summary_id: ID of the summary message

        Returns:
            Number of archived messages
        """
        archived_count = 0

        for msg in messages:
            # Create archive entry
            archive = MessageArchive(
                id=uuid.uuid4(),
                original_message_id=msg.id,
                conversation_id=msg.conversation_id,
                role=msg.role,
                content=msg.content,
                token_count=msg.token_count,
                original_created_at=msg.created_at,
                summary_message_id=summary_id,
            )
            db.add(archive)

            # Delete original message
            db.delete(msg)
            archived_count += 1

        return archived_count

    def restore_archive(
        self, db: Session, conversation_id: uuid.UUID, user_id: uuid.UUID
    ) -> Tuple[Dict[str, Any], int]:
        """
        Restore archived messages for a conversation (optional feature).

        Args:
            db: Database session
            conversation_id: Conversation UUID
            user_id: User UUID

        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get conversation
            conversation = (
                db.query(Conversation)
                .filter(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id,
                )
                .first()
            )

            if not conversation:
                return {"error": "Conversation not found"}, 404

            # Get archived messages
            archived_messages = (
                db.query(MessageArchive)
                .filter(MessageArchive.conversation_id == conversation_id)
                .order_by(MessageArchive.original_created_at.asc())
                .all()
            )

            if not archived_messages:
                return {"message": "No archived messages found"}, 200

            # Get summary message to delete
            summary_id = archived_messages[0].summary_message_id if archived_messages else None
            restored_count = 0

            # Restore archived messages
            for archive in archived_messages:
                # Create message from archive
                msg = Message(
                    id=archive.original_message_id,
                    conversation_id=archive.conversation_id,
                    role=archive.role,
                    content=archive.content,
                    token_count=archive.token_count,
                    is_summary=False,
                    created_at=archive.original_created_at,
                )
                db.add(msg)

                # Delete archive entry
                db.delete(archive)
                restored_count += 1

            # Delete summary message
            if summary_id:
                summary_msg = db.query(Message).filter(Message.id == summary_id).first()
                if summary_msg:
                    db.delete(summary_msg)

            # Recalculate token count
            all_messages = (
                db.query(Message)
                .filter(Message.conversation_id == conversation_id)
                .all()
            )
            total_tokens = sum([m.token_count or 0 for m in all_messages])
            conversation.current_token_count = total_tokens
            conversation.updated_at = datetime.utcnow()

            db.commit()

            logger.info(
                "Archive restored successfully",
                conversation_id=str(conversation_id),
                restored_count=restored_count,
            )

            return {
                "message": "Archive restored successfully",
                "restored_messages": restored_count,
                "new_token_count": total_tokens,
            }, 200

        except Exception as e:
            db.rollback()
            logger.error(
                "Error restoring archive",
                conversation_id=str(conversation_id),
                error_type=type(e).__name__,
                error=str(e),
                stacktrace=traceback.format_exc(),
            )
            return {"error": f"Failed to restore archive: {e}"}, 500
