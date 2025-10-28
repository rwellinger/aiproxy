"""Compression Orchestrator - Coordinates conversation compression (NOT testable, orchestration only)."""

import traceback
import uuid
from typing import Any

import requests
from sqlalchemy.orm import Session

from business.compression_transformer import (
    build_summary_messages,
    build_summary_prompt,
    calculate_token_estimate,
    create_fallback_summary,
    filter_compressible_messages,
    format_summary_message,
)
from business.openai_chat_orchestrator import OpenAIChatOrchestrator
from config.settings import OLLAMA_TIMEOUT, OLLAMA_URL
from db.conversation_service import ConversationService
from db.message_service import MessageService
from utils.logger import logger


class CompressionOrchestrator:
    """Orchestrator for compressing conversations (coordinates services, NO business logic)."""

    def __init__(self):
        self.message_service = MessageService()
        self.conversation_service = ConversationService()
        self.openai_orchestrator = OpenAIChatOrchestrator()

    def compress_conversation(
        self, db: Session, conversation_id: uuid.UUID, user_id: uuid.UUID, keep_recent: int = 2
    ) -> tuple[dict[str, Any], int]:
        """
        Compress a conversation by archiving old messages and creating AI summary.

        Strategy:
        1. Keep all system messages (never compress)
        2. Keep last N recent user/assistant messages
        3. Archive older messages
        4. Create AI summary of archived messages
        5. Insert summary as new assistant message
        6. Recalculate token count

        Args:
            db: Database session
            conversation_id: Conversation UUID
            user_id: User UUID
            keep_recent: Number of recent messages to keep (default: 2)

        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get conversation
            conversation = self.conversation_service.get_conversation(db, conversation_id, user_id)

            if not conversation:
                return {"error": "Conversation not found"}, 404

            # Get all messages
            all_messages = self.message_service.get_conversation_messages(db, conversation_id)

            # Filter messages using transformer
            protected_messages, old_messages, recent_messages = filter_compressible_messages(all_messages, keep_recent)

            # Check if compression is needed
            if not old_messages:
                return {
                    "message": "No compression needed",
                    "details": f"Only {len(all_messages) - len(protected_messages)} compressible messages",
                }, 200

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
                old_messages, conversation.model, conversation.provider
            )

            # Format summary message using transformer
            formatted_message, prefix_token_count = format_summary_message(summary_content, len(old_messages))

            # Create summary message
            summary_message = self.message_service.create_message(
                db=db,
                conversation_id=conversation_id,
                role="assistant",  # Changed from 'system' to allow future compression
                content=formatted_message,
                token_count=summary_token_count + prefix_token_count,
                is_summary=True,
            )

            if not summary_message:
                raise Exception("Failed to create summary message")

            # Archive old messages
            archived_count = self.message_service.archive_messages(db, old_messages, summary_message.id)

            # Recalculate actual token count
            remaining_messages = self.message_service.get_conversation_messages(db, conversation_id)
            verification_messages = [{"role": msg.role, "content": msg.content} for msg in remaining_messages]

            actual_token_count = self._get_actual_token_count(
                verification_messages, conversation.model, conversation.provider
            )

            # Update conversation token count
            self.conversation_service.update_token_count(db, conversation_id, actual_token_count)

            db.commit()

            logger.info(
                "Conversation compressed successfully",
                conversation_id=str(conversation_id),
                archived_count=archived_count,
                new_token_count=actual_token_count,
            )

            return {
                "message": "Conversation compressed successfully",
                "archived_messages": archived_count,
                "summary_created": True,
                "new_token_count": actual_token_count,
                "token_percentage": (actual_token_count / conversation.context_window_size) * 100,
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

    def _create_ai_summary(self, messages: list, model: str, provider: str) -> tuple[str, int]:
        """
        Create AI summary of messages using the conversation's model.

        Args:
            messages: List of message objects to summarize
            model: Model name
            provider: Provider ('internal' or 'external')

        Returns:
            Tuple of (summary_text, token_count)
        """
        # Build prompt using transformer
        summary_prompt = build_summary_prompt(messages, max_messages=20)
        summary_messages = build_summary_messages(summary_prompt)

        try:
            if provider == "external":
                # Use OpenAI via orchestrator
                content, prompt_tokens, completion_tokens = self.openai_orchestrator.send_chat_message(
                    model=model, messages=summary_messages
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
                provider=provider,
                stacktrace=traceback.format_exc(),
            )
            # Fallback: Create simple text summary using transformer
            return create_fallback_summary(messages)

    def _get_actual_token_count(self, messages: list[dict[str, str]], model: str, provider: str) -> int:
        """
        Get actual token count by making a test call to the model.

        Args:
            messages: List of messages with role and content
            model: Model name
            provider: Provider ('internal' or 'external')

        Returns:
            Actual token count from the model
        """
        try:
            if provider == "external":
                # Use OpenAI - estimate based on message lengths using transformer
                estimated_tokens = calculate_token_estimate(
                    "".join([msg.get("content", "") for msg in messages]), chars_per_token=4
                )
                logger.info("Token count estimated for OpenAI", estimated_tokens=estimated_tokens, provider=provider)
                return estimated_tokens
            else:
                # Use Ollama - get prompt_eval_count
                api_url = f"{OLLAMA_URL}/api/chat"

                # Add minimal user message to trigger eval
                test_messages = messages + [{"role": "user", "content": "."}]

                payload = {
                    "model": model,
                    "messages": test_messages,
                    "stream": False,
                }

                resp = requests.post(api_url, json=payload, timeout=OLLAMA_TIMEOUT)
                resp.raise_for_status()
                resp_json = resp.json()

                prompt_eval_count = resp_json.get("prompt_eval_count", 0)

                logger.info(
                    "Actual token count retrieved from Ollama", prompt_eval_count=prompt_eval_count, provider=provider
                )

                return prompt_eval_count

        except Exception as e:
            logger.warning(
                "Failed to get actual token count, using fallback",
                error=str(e),
                provider=provider,
                stacktrace=traceback.format_exc(),
            )
            # Fallback: estimate using transformer
            return calculate_token_estimate("".join([msg.get("content", "") for msg in messages]), chars_per_token=4)

    def restore_archive(
        self, db: Session, conversation_id: uuid.UUID, user_id: uuid.UUID
    ) -> tuple[dict[str, Any], int]:
        """
        Restore archived messages for a conversation.

        Args:
            db: Database session
            conversation_id: Conversation UUID
            user_id: User UUID

        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get conversation
            conversation = self.conversation_service.get_conversation(db, conversation_id, user_id)

            if not conversation:
                return {"error": "Conversation not found"}, 404

            # Get archived messages
            archived_messages = self.message_service.get_archived_messages(db, conversation_id)

            if not archived_messages:
                return {"message": "No archived messages found"}, 200

            # Get summary message ID to delete
            summary_id = archived_messages[0].summary_message_id if archived_messages else None

            # Restore archived messages
            restored_count = self.message_service.restore_archived_messages(db, conversation_id)

            # Delete summary message if exists
            if summary_id:
                self.message_service.delete_message(db, summary_id)

            # Recalculate token count
            all_messages = self.message_service.get_conversation_messages(db, conversation_id)
            total_tokens = sum([m.token_count or 0 for m in all_messages])

            self.conversation_service.update_token_count(db, conversation_id, total_tokens)

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
