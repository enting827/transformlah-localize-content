from pydantic import BaseModel, Field, field_validator, HttpUrl
from typing import Optional, Dict, Union, Any, List, Literal
from fastapi import UploadFile, File
from logging_config import get_logger
from enum import Enum
import json
from enum import Enum

logger = get_logger(__name__)

class ChatInput(BaseModel):
    prompt: str = Field(
        ..., description="The user prompt for content generation"
    )
    session_id: Optional[str] = Field(
        None, description="The session ID to maintain conversation history"
    )
    configuration: Optional[Union[Dict, str]] = Field(
        None, description="Configuration settings (JSON) for content generation, e.g., Campaign name, Language, Tone"
    )
    file: Optional[UploadFile] = Field(
        None, description="Optional file input (image/video)"
    )
    
    @field_validator('configuration', mode='before')
    @classmethod
    def parse_configuration(cls, v):
        if v is None or v == "":
            return None
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in configuration: {e}")
                raise ValueError('configuration must be valid JSON')
        return v

class MusicSearchInput(BaseModel):
    content: str = Field(..., description="Text content or image description for music matching")
    file: Optional[UploadFile] = Field(None, description="Optional image file for multimodal analysis")
    configuration: Optional[Dict] = Field(None, description="Search preferences and constraints")
    mood: Optional[str] = Field(None, description="Target mood/genre (e.g., 'upbeat', 'emotional', 'traditional')")
    language: Optional[str] = Field("malay", description="Preferred language context")
    target_audience: Optional[str] = Field("general", description="Target audience demographic")
    platform: Optional[str] = Field("instagram", description="Social media platform for optimization")
    session_id: Optional[str] = Field(None, description="The session ID to maintain conversation history")
    session_id: Optional[str] = Field(None, description="The session ID to maintain conversation history")

class MusicSearchResult(BaseModel):
    song_title: str = Field(..., description="Title of the recommended song")
    artist: str = Field(..., description="Malaysian artist name")
    youtube_url: str = Field(..., description="YouTube URL for the full song")
    snippet_start: int = Field(..., description="Start time of popular snippet (seconds)")
    snippet_end: int = Field(..., description="End time of popular snippet (seconds)")
    popularity_score: float = Field(..., description="Popularity score 0.0-1.0")
    genre: str = Field(..., description="Music genre/style")
    malaysian_context: str = Field(..., description="Why this song fits Malaysian marketing")
    duration: int = Field(..., description="Total song duration in seconds")
    view_count: int = Field(..., description="YouTube view count")
    like_count: int = Field(..., description="YouTube like count")

class MusicSearchResponse(BaseModel):
    request_id: str = Field(..., description="Unique request identifier")
    results: List[MusicSearchResult] = Field(..., description="List of music search results")
    total_results: int = Field(..., description="Total number of results found")
    search_metadata: Dict = Field(..., description="Search parameters and context")
    processing_time: float = Field(..., description="Time taken to process request (seconds)")

class Song(BaseModel):
    song_name: str
    artists: List[str]
    youtube_url: HttpUrl
    reasoning: str

class SongsPayload(BaseModel):
    song: List[Song]

# Define the Song model as it is currently being returned by the Bedrock Agent
class AgentOutputSong(BaseModel):
    title: str
    artist: str # The agent returns a single string artist, not a list
    reasoning: str
    youtube_url: HttpUrl

# Define the SongsPayload to match the agent's current top-level structure
class AgentOutputSongsPayload(BaseModel):
    # This now correctly expects a single 'song' object, not a list
    song: AgentOutputSong
    
class UrlRequest(BaseModel):
    s3_uri: str
    type: Optional[Literal["video/mp4", "image/png", "image/jpeg"]] = "video/mp4"  # Only allowed types

class ImageSize(str, Enum):
    SQUARE_1080 = "square_1080"  # Instagram Square (1080x1080)
    PORTRAIT_1080 = "portrait_1080"  # Instagram Portrait (1080x1350)
    STORY_1080 = "story_1080"  # Instagram Story (1080x1920)
    FB_COVER = "fb_cover"  # Facebook Cover (820x312)
    FB_POST = "fb_post"  # Facebook Post (1200x630)
    TWITTER_POST = "twitter_post"  # Twitter Post (1200x675)
    LINKEDIN_POST = "linkedin_post"  # LinkedIn Post (1200x627)
    TIKTOK_VIDEO = "tiktok_video"  # TikTok Cover (1080x1920)

class ImageQuality(str, Enum):
    STANDARD = "standard"
    HD = "hd"
    PREMIUM = "premium"

class BackgroundStyle(str, Enum):
    SOLID = "solid"
    GRADIENT = "gradient"
    PATTERN = "pattern"
    TRANSPARENT = "transparent"
    SCENE = "scene"

class ImageDimensions(BaseModel):
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")

class ImageConfiguration(BaseModel):
    image_size: ImageSize = Field(..., description="Predefined image size for social media platforms")
    image_quality: ImageQuality = Field(default=ImageQuality.STANDARD, description="Image quality level")
    background_style: Optional[BackgroundStyle] = Field(None, description="Background style preference")
    image_aspect_ratio: str = Field(..., description="Image aspect ratio (e.g. '1:1', '4:5')")
    image_dimensions: ImageDimensions = Field(..., description="Specific pixel dimensions")

class GenerationType(str, Enum):
    CAPTION = "caption"
    IMAGE = "image" 
    VIDEO = "video"

class UserIntent(BaseModel):
    """Analyzed user intent from prompt"""
    generate_types: List[GenerationType] = Field(..., description="What types of content to generate")
    reasoning: str = Field(..., description="Why these types were selected")
    priority_order: List[GenerationType] = Field(..., description="Order of generation priority")
    dependencies: Dict[str, List[str]] = Field(default={}, description="Dependencies between generation types")

class UnifiedChatInput(BaseModel):
    """Unified input for the orchestrator endpoint"""
    prompt: str = Field(..., description="User's request prompt")
    configuration: Optional[Dict[str, Any]] = Field(default={}, description="Generation configuration")
    force_types: Optional[List[GenerationType]] = Field(default=None, description="Force specific generation types (bypass AI analysis)")
    max_concurrent: Optional[int] = Field(default=2, description="Maximum concurrent generations")

class GenerationResult(BaseModel):
    """Result from a single generation"""
    type: GenerationType
    status: str  # "success", "error", "skipped"
    session_id: str
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None

class OrchestratorResponse(BaseModel):
    """Response from the orchestrator"""
    session_id: str
    analyzed_intent: UserIntent
    results: List[GenerationResult]
    total_execution_time: float
    status: str  # "completed", "partial", "failed"

class MusicSearchUrlResponse(BaseModel):
    session_id: str
    youtube_url: str
