"""Database models"""

import uuid
from enum import Enum

from sqlalchemy import ARRAY, Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSON, JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from db.database import Base


class SongStatus(str, Enum):
    """Enum for song generation status"""

    PENDING = "PENDING"
    PROGRESS = "PROGRESS"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    CANCELLED = "CANCELLED"


class RuleType(str, Enum):
    """Enum for lyric parsing rule types"""

    CLEANUP = "cleanup"
    SECTION = "section"


class SongSketch(Base):
    """Model for storing song concepts/drafts before generation"""

    __tablename__ = "song_sketches"
    __table_args__ = {"extend_existing": True}

    # Primary identifier
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Core song data
    title = Column(String(500), nullable=True)
    lyrics = Column(Text, nullable=True)
    prompt = Column(Text, nullable=False)

    # Metadata
    tags = Column(String(1000), nullable=True)

    # Release descriptions (for publishing to platforms)
    description_long = Column(Text, nullable=True)
    description_short = Column(String(150), nullable=True)
    description_tags = Column(String(1000), nullable=True)
    info = Column(Text, nullable=True)

    # Workflow status
    workflow = Column(String(50), nullable=False, default="draft", index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship: Ein Sketch kann mehrere Songs haben
    songs = relationship("Song", back_populates="sketch")

    def __repr__(self):
        return f"<SongSketch(id={self.id}, title='{self.title}', workflow='{self.workflow}')>"


class Song(Base):
    """Model for storing song generation data and results"""

    __tablename__ = "songs"
    __table_args__ = {"extend_existing": True}

    # Primary identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    task_id = Column(String(255), nullable=False, unique=True, index=True)  # Celery Task ID
    job_id = Column(String(255), nullable=True, index=True)  # MUREKA Job ID

    # Input parameters
    lyrics = Column(Text, nullable=False)
    prompt = Column(Text, nullable=False)  # Style prompt
    model = Column(String(100), nullable=True, default="auto")

    # User editable metadata
    title = Column(String(500), nullable=True)
    tags = Column(String(1000), nullable=True)
    workflow = Column(String(50), nullable=True)  # onWork, inUse, notUsed, or NULL
    is_instrumental = Column(Boolean, nullable=True, default=False)  # True for instrumental songs

    # Sketch relationship (optional - song can be created from sketch or directly)
    sketch_id = Column(UUID(as_uuid=True), ForeignKey("song_sketches.id"), nullable=True, index=True)

    # Status tracking
    status = Column(String(50), nullable=False, default="PENDING")  # PENDING, PROGRESS, SUCCESS, FAILURE, CANCELLED
    progress_info = Column(Text, nullable=True)  # JSON string for progress details
    error_message = Column(Text, nullable=True)

    # Relation to song choices (1:n)
    choices = relationship(
        "SongChoice", back_populates="song", cascade="all, delete-orphan", order_by="SongChoice.choice_index"
    )

    # Relation to sketch (n:1)
    sketch = relationship("SongSketch", back_populates="songs")

    # MUREKA response data
    mureka_response = Column(Text, nullable=True)  # JSON string der kompletten MUREKA Response
    mureka_status = Column(String(100), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<Song(id={self.id}, task_id='{self.task_id}', status='{self.status}', choices={len(self.choices) if self.choices else 0})>"


class SongChoice(Base):
    """Model for storing individual song choice results from MUREKA"""

    __tablename__ = "song_choices"
    __table_args__ = {"extend_existing": True}

    # Primary identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    song_id = Column(UUID(as_uuid=True), ForeignKey("songs.id"), nullable=False, index=True)

    # MUREKA choice data
    mureka_choice_id = Column(String(255), nullable=True)  # MUREKA's choice ID
    choice_index = Column(Integer, nullable=True)  # Index in choices array

    # URLs and files
    mp3_url = Column(String(1000), nullable=True)
    flac_url = Column(String(1000), nullable=True)
    video_url = Column(String(1000), nullable=True)  # Falls verfügbar
    image_url = Column(String(1000), nullable=True)  # Cover image
    stem_url = Column(String(1000), nullable=True)  # Stems ZIP file URL

    # Metadata
    duration = Column(Float, nullable=True)  # Duration in milliseconds (as returned by MUREKA)
    title = Column(String(500), nullable=True)
    tags = Column(String(1000), nullable=True)  # Comma-separated
    rating = Column(Integer, nullable=True)  # User rating: NULL=not set, 0=thumbs down, 1=thumbs up

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    stem_generated_at = Column(DateTime(timezone=True), nullable=True)  # When stems were generated

    # Relation back to song
    song = relationship("Song", back_populates="choices")

    def __repr__(self):
        return f"<SongChoice(id={self.id}, song_id={self.song_id}, choice_index={self.choice_index}, duration={self.duration})>"


class GeneratedImage(Base):
    """Model for storing generated image metadata"""

    __tablename__ = "generated_images"
    __table_args__ = {"extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_prompt = Column(Text, nullable=True)  # Original user input (before AI enhancement)
    prompt = Column(Text, nullable=False)  # AI-enhanced prompt (Ollama)
    enhanced_prompt = Column(Text, nullable=True)  # Final prompt sent to DALL-E (Ollama + Styles)
    size = Column(String(20), nullable=False)
    filename = Column(String(255), nullable=False, unique=True)
    file_path = Column(String(500), nullable=False)
    local_url = Column(String(500), nullable=False)
    model_used = Column(String(100), nullable=True)
    prompt_hash = Column(String(32), nullable=True)
    title = Column(String(255), nullable=True)  # Custom user title
    tags = Column(Text, nullable=True)  # Comma-separated tags

    # Style preferences (guided mode)
    artistic_style = Column(String(50), nullable=True)  # photorealistic, digital-art, oil-painting, etc.
    composition = Column(String(50), nullable=True)  # portrait, landscape, wide-angle, etc.
    lighting = Column(String(50), nullable=True)  # natural, studio, dramatic, etc.
    color_palette = Column(String(50), nullable=True)  # vibrant, muted, monochrome, etc.
    detail_level = Column(String(50), nullable=True)  # minimal, moderate, highly-detailed
    text_overlay_metadata = Column(JSON, nullable=True)  # Metadata for text overlays (title, artist, font_style, etc.)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<GeneratedImage(id={self.id}, filename='{self.filename}', prompt='{self.prompt[:50]}...')>"


class PromptTemplate(Base):
    """Model for storing AI prompt templates for different categories and actions"""

    __tablename__ = "prompt_templates"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False)
    pre_condition = Column(Text, nullable=False)
    post_condition = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(10), nullable=True)
    model = Column(String(50), nullable=True)  # Renamed from model_hint
    temperature = Column(Float, nullable=True)  # For Ollama Chat API (0.0-2.0)
    max_tokens = Column(Integer, nullable=True)  # Maximum tokens to generate
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return (
            f"<PromptTemplate(id={self.id}, category='{self.category}', action='{self.action}', active={self.active})>"
        )


class User(Base):
    """Model for user authentication and management with OAuth2 preparation"""

    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    # Primary identifier
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Authentication fields
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth2 users

    # User profile
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    artist_name = Column(String(100), nullable=True)  # For album cover generation (e.g., "thWelly")

    # OAuth2 preparation (for future use)
    oauth_provider = Column(String(50), nullable=True)  # 'google', 'github', etc.
    oauth_id = Column(String(255), nullable=True)  # OAuth provider user ID

    # Status and security
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    equipment = relationship("Equipment", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', active={self.is_active})>"


class Conversation(Base):
    """Model for storing AI chat conversations"""

    __tablename__ = "conversations"
    __table_args__ = {"extend_existing": True}

    # Primary identifier
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Conversation metadata
    title = Column(String(255), nullable=False)
    model = Column(String(100), nullable=False)  # Model name (Ollama or OpenAI)
    provider = Column(
        String(50), nullable=False, server_default="internal", index=True
    )  # 'internal' (Ollama) or 'external' (OpenAI, DeepSeek)
    system_context = Column(Text, nullable=True)  # System prompt/context
    archived = Column(Boolean, nullable=False, server_default="false")  # Archive status

    # Token tracking
    context_window_size = Column(Integer, nullable=False, server_default="2048")  # Max tokens for this model
    current_token_count = Column(Integer, nullable=False, server_default="0")  # Current total tokens used

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at"
    )

    def __repr__(self):
        return f"<Conversation(id={self.id}, title='{self.title}', model='{self.model}', provider='{self.provider}', messages={len(self.messages) if self.messages else 0})>"


class Message(Base):
    """Model for storing individual messages in a conversation"""

    __tablename__ = "messages"
    __table_args__ = {"extend_existing": True}

    # Primary identifier
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False, index=True)

    # Message content
    role = Column(String(50), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)

    # Compression tracking
    is_summary = Column(Boolean, nullable=True, default=False)  # True if this is a compressed summary

    # Token tracking
    token_count = Column(Integer, nullable=True)  # Token count for this message

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, role='{self.role}', conversation_id={self.conversation_id})>"


class MessageArchive(Base):
    """Model for storing archived messages - used for compression without data loss"""

    __tablename__ = "messages_archive"
    __table_args__ = {"extend_existing": True}

    # Primary identifier
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Original message reference
    original_message_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False, index=True)

    # Message content (copied from original)
    role = Column(String(50), nullable=False)  # 'user', 'assistant'
    content = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=True)

    # Original timestamp
    original_created_at = Column(DateTime(timezone=True), nullable=False)

    # Archive metadata
    archived_at = Column(DateTime(timezone=True), server_default=func.now())
    summary_message_id = Column(UUID(as_uuid=True), nullable=True)  # Reference to summary that replaced these messages

    # Relationship
    conversation = relationship("Conversation")

    def __repr__(self):
        return f"<MessageArchive(id={self.id}, original_id={self.original_message_id}, role='{self.role}')>"


class LyricParsingRule(Base):
    """Model for storing configurable lyric parsing rules (cleanup and section detection)"""

    __tablename__ = "lyric_parsing_rules"
    __table_args__ = {"extend_existing": True}

    # Primary identifier
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Rule metadata
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Rule logic
    pattern = Column(Text, nullable=False)  # Regex pattern (JSON-escaped)
    replacement = Column(Text, nullable=False)  # Replacement string
    rule_type = Column(String(50), nullable=False, index=True)  # cleanup, section

    # Control
    active = Column(Boolean, default=True, nullable=False, index=True)
    order = Column(Integer, nullable=False, default=0, index=True)  # Execution order

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<LyricParsingRule(id={self.id}, name='{self.name}', type='{self.rule_type}', active={self.active}, order={self.order})>"


class ApiCostMonthly(Base):
    """Model for monthly API cost caching with TTL support"""

    __tablename__ = "api_costs_monthly"
    __table_args__ = {"extend_existing": True}

    # Primary identifier
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Provider and organization
    provider = Column(String(50), nullable=False, index=True)  # 'openai', 'mureka'
    organization_id = Column(String(100), nullable=True, index=True)  # User-specific keys (optional)

    # Time period
    year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=False, index=True)  # 1-12

    # Aggregated costs
    total_cost = Column(Numeric(12, 6), nullable=False)
    image_cost = Column(Numeric(12, 6), default=0)  # DALL-E costs
    chat_cost = Column(Numeric(12, 6), default=0)  # GPT costs
    currency = Column(String(3), default="usd")

    # Details
    line_items = Column(JSONB, nullable=True)  # Full breakdown by line_item
    bucket_count = Column(Integer, nullable=True)  # Debug: Number of days/buckets
    project_ids = Column(ARRAY(Text), nullable=True)  # Filtered projects (optional)

    # Caching metadata (for Hybrid-Caching with TTL)
    is_finalized = Column(Boolean, default=False, nullable=False, index=True)  # TRUE = Past month (never reload)
    last_updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)  # Last API update

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ApiCostMonthly(provider='{self.provider}', year={self.year}, month={self.month}, total={self.total_cost}, finalized={self.is_finalized})>"


class Equipment(Base):
    """Model for storing software and plugin licenses with encrypted sensitive data"""

    __tablename__ = "equipment"
    __table_args__ = {"extend_existing": True}

    # Primary identifier
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Core fields
    type = Column(String(50), nullable=False, index=True)  # 'Software' | 'Plugin'
    name = Column(String(200), nullable=False)
    version = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)

    # Tags (comma-separated)
    software_tags = Column(String(1000), nullable=True)
    plugin_tags = Column(String(1000), nullable=True)

    # Manufacturer info
    manufacturer = Column(String(200), nullable=True)
    url = Column(String(500), nullable=True)

    # Credentials (encrypted with Fernet)
    username = Column(String(200), nullable=True)
    password_encrypted = Column(Text, nullable=True)

    # License management
    license_management = Column(String(100), nullable=True)  # 'online' | 'ilok' | 'license_key' | 'other'
    license_key_encrypted = Column(Text, nullable=True)
    license_description = Column(Text, nullable=True)

    # Purchase information
    purchase_date = Column(Date, nullable=True)
    price_encrypted = Column(Text, nullable=True)  # Format: "299.99 EUR" (encrypted)

    # System requirements
    system_requirements = Column(Text, nullable=True)

    # Status (multi-state workflow like Sketch)
    status = Column(
        String(50), nullable=False, default="active", index=True
    )  # 'active' | 'trial' | 'expired' | 'archived'

    # User ownership (JWT-based access control)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    user = relationship("User", back_populates="equipment")

    def __repr__(self):
        return f"<Equipment(id={self.id}, type='{self.type}', name='{self.name}', status='{self.status}')>"
