"""Conversation Controller - Handles business logic for AI chat conversations."""
import traceback
import uuid
from datetime import datetime
from typing import Tuple, Dict, Any, List
import requests
from sqlalchemy.orm import Session
from sqlalchemy import func

from db.models import Conversation, Message
from schemas.conversation_schemas import (
    ConversationCreate,
    ConversationResponse,
    MessageResponse,
)
from utils.logger import logger
from config.settings import OLLAMA_URL, OLLAMA_TIMEOUT
from config.model_context_windows import get_context_window_size


class ConversationController:
    """Controller for managing AI chat conversations."""

    def list_conversations(
        self, db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 20
    ) -> Tuple[Dict[str, Any], int]:
        """
        List all conversations for a user.

        Args:
            db: Database session
            user_id: User UUID
            skip: Pagination offset
            limit: Pagination limit

        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get conversations with message count
            query = (
                db.query(
                    Conversation,
                    func.count(Message.id).label("message_count")
                )
                .outerjoin(Message, Conversation.id == Message.conversation_id)
                .filter(Conversation.user_id == user_id)
                .group_by(Conversation.id)
                .order_by(Conversation.updated_at.desc())
            )

            total = query.count()
            conversations_with_count = query.offset(skip).limit(limit).all()

            # Build response
            conversations = []
            for conv, msg_count in conversations_with_count:
                conv_dict = ConversationResponse.from_orm(conv).dict()
                conv_dict["message_count"] = msg_count
                conversations.append(conv_dict)

            return {
                "conversations": conversations,
                "total": total,
                "skip": skip,
                "limit": limit,
            }, 200

        except Exception as e:
            logger.error(
                "Error listing conversations",
                error_type=type(e).__name__,
                error=str(e),
                stacktrace=traceback.format_exc(),
            )
            return {"error": f"Failed to list conversations: {e}"}, 500

    def get_conversation(
        self, db: Session, conversation_id: uuid.UUID, user_id: uuid.UUID
    ) -> Tuple[Dict[str, Any], int]:
        """
        Get conversation with messages.

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

            # Get messages
            messages = (
                db.query(Message)
                .filter(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.asc())
                .all()
            )

            return {
                "conversation": ConversationResponse.from_orm(conversation).dict(),
                "messages": [MessageResponse.from_orm(msg).dict() for msg in messages],
            }, 200

        except Exception as e:
            logger.error(
                "Error getting conversation",
                conversation_id=str(conversation_id),
                error_type=type(e).__name__,
                error=str(e),
                stacktrace=traceback.format_exc(),
            )
            return {"error": f"Failed to get conversation: {e}"}, 500

    def create_conversation(
        self, db: Session, user_id: uuid.UUID, data: ConversationCreate
    ) -> Tuple[Dict[str, Any], int]:
        """
        Create a new conversation.

        Args:
            db: Database session
            user_id: User UUID
            data: Conversation creation data

        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get context window size for the model
            context_window_size = get_context_window_size(data.model)

            # Create conversation
            conversation = Conversation(
                id=uuid.uuid4(),
                user_id=user_id,
                title=data.title,
                model=data.model,
                system_context=data.system_context,
                context_window_size=context_window_size,
                current_token_count=0,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            db.add(conversation)

            # Add system context as first message if provided
            if data.system_context:
                system_message = Message(
                    id=uuid.uuid4(),
                    conversation_id=conversation.id,
                    role="system",
                    content=data.system_context,
                    token_count=len(data.system_context.split()),  # Rough approximation
                    created_at=datetime.utcnow(),
                )
                db.add(system_message)

            db.commit()
            db.refresh(conversation)

            logger.info(
                "Conversation created",
                conversation_id=str(conversation.id),
                user_id=str(user_id),
            )

            return ConversationResponse.from_orm(conversation).dict(), 201

        except Exception as e:
            db.rollback()
            logger.error(
                "Error creating conversation",
                user_id=str(user_id),
                error_type=type(e).__name__,
                error=str(e),
                stacktrace=traceback.format_exc(),
            )
            return {"error": f"Failed to create conversation: {e}"}, 500

    def delete_conversation(
        self, db: Session, conversation_id: uuid.UUID, user_id: uuid.UUID
    ) -> Tuple[Dict[str, Any], int]:
        """
        Delete a conversation.

        Args:
            db: Database session
            conversation_id: Conversation UUID
            user_id: User UUID

        Returns:
            Tuple of (response_data, status_code)
        """
        try:
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

            db.delete(conversation)
            db.commit()

            logger.info(
                "Conversation deleted",
                conversation_id=str(conversation_id),
                user_id=str(user_id),
            )

            return {"message": "Conversation deleted successfully"}, 200

        except Exception as e:
            db.rollback()
            logger.error(
                "Error deleting conversation",
                conversation_id=str(conversation_id),
                error_type=type(e).__name__,
                error=str(e),
                stacktrace=traceback.format_exc(),
            )
            return {"error": f"Failed to delete conversation: {e}"}, 500

    def send_message(
        self, db: Session, conversation_id: uuid.UUID, user_id: uuid.UUID, content: str
    ) -> Tuple[Dict[str, Any], int]:
        """
        Send a message and get AI response.

        Args:
            db: Database session
            conversation_id: Conversation UUID
            user_id: User UUID
            content: Message content

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

            # Create user message
            user_message = Message(
                id=uuid.uuid4(),
                conversation_id=conversation_id,
                role="user",
                content=content,
                created_at=datetime.utcnow(),
            )
            db.add(user_message)
            db.flush()  # Get user_message.id

            # Get conversation history for context
            messages = (
                db.query(Message)
                .filter(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.asc())
                .all()
            )

            # Build messages for Ollama chat API
            chat_messages = []
            for msg in messages:
                chat_messages.append({"role": msg.role, "content": msg.content})

            # Call Ollama chat API
            try:
                assistant_content, prompt_eval_count, eval_count = self._call_ollama_chat_api(
                    conversation.model, chat_messages
                )
            except OllamaAPIError as e:
                db.rollback()
                logger.error("Ollama API Error", error=str(e))
                return {"error": f"Ollama API Error: {e}"}, 500

            # Calculate user message token count (part of prompt_eval_count)
            # Note: prompt_eval_count includes system context + all previous messages + new user message
            # For simplicity, we use eval_count for assistant and store prompt_eval_count
            user_message.token_count = len(content.split())  # Rough approximation

            # Create assistant message
            assistant_message = Message(
                id=uuid.uuid4(),
                conversation_id=conversation_id,
                role="assistant",
                content=assistant_content,
                token_count=eval_count,
                created_at=datetime.utcnow(),
            )
            db.add(assistant_message)

            # Update conversation token count
            conversation.current_token_count = prompt_eval_count + eval_count

            # Update conversation timestamp
            conversation.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(user_message)
            db.refresh(assistant_message)

            logger.info(
                "Message sent and response received",
                conversation_id=str(conversation_id),
            )

            return {
                "user_message": MessageResponse.from_orm(user_message).dict(),
                "assistant_message": MessageResponse.from_orm(assistant_message).dict(),
            }, 200

        except Exception as e:
            db.rollback()
            logger.error(
                "Error sending message",
                conversation_id=str(conversation_id),
                error_type=type(e).__name__,
                error=str(e),
                stacktrace=traceback.format_exc(),
            )
            return {"error": f"Failed to send message: {e}"}, 500

    def _call_ollama_chat_api(self, model: str, messages: List[Dict[str, str]]) -> Tuple[str, int, int]:
        """
        Call Ollama chat API.

        Args:
            model: Model name
            messages: List of messages with role and content

        Returns:
            Tuple of (assistant_content, prompt_eval_count, eval_count)

        Raises:
            OllamaAPIError: If API call fails
        """
        api_url = f"{OLLAMA_URL}/api/chat"
        logger.debug("Calling Ollama chat API", api_url=api_url, model=model)

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
        }

        try:
            resp = requests.post(
                api_url,
                json=payload,
                timeout=OLLAMA_TIMEOUT,
            )
            resp.raise_for_status()

            resp_json = resp.json()
            logger.debug("Ollama chat API response received")

            # Extract assistant message
            if "message" in resp_json and "content" in resp_json["message"]:
                content = resp_json["message"]["content"]
                prompt_eval_count = resp_json.get("prompt_eval_count", 0)
                eval_count = resp_json.get("eval_count", 0)

                logger.debug(
                    "Token counts extracted",
                    prompt_tokens=prompt_eval_count,
                    response_tokens=eval_count
                )

                return content, prompt_eval_count, eval_count
            else:
                raise OllamaAPIError("Invalid API response format")

        except requests.exceptions.RequestException as e:
            logger.error("Ollama API Network Error", error=str(e))
            raise OllamaAPIError(f"Network Error: {e}")
        except Exception as e:
            logger.error(
                "Unexpected Ollama API error",
                error_type=type(e).__name__,
                error=str(e),
            )
            raise OllamaAPIError(f"Unexpected Error: {e}")


class OllamaAPIError(Exception):
    """Custom exception for Ollama API errors."""

    pass
