import time as time_module
import uuid
import json
from fastapi import APIRouter, Body, Request, Form, HTTPException, File, UploadFile, Query
from fastapi.responses import StreamingResponse
from typing import Optional, Dict, Union, Any, List
import base64
from logging_config import get_logger
import service as service
from service import (
    get_facebook_stats, 
    get_instagram_stats, 
    get_post_insights,
    fetch_youtube_video_analytics,
    fetch_youtube_channel_info,
    get_all_social_urls,
    analyze_youtube_video_with_llm,
    get_youtube_video_insights,
    get_all_social_stats,
    get_all_platform_stats,
    get_youtube_stats,
    generate_caption,
    generate_image,
    generate_video,
)
from service import MusicSearchService
from schemas import ChatInput, MusicSearchInput, MusicSearchResponse, UrlRequest, UnifiedChatInput, MusicSearchUrlResponse
from exceptions import MusicSearchException, YouTubeSearchException
from pydantic import BaseModel
from pathlib import Path

logger = get_logger()
import os
import glob
from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles

logger = get_logger(__name__)

router = APIRouter()

@router.get("/social/facebook")
async def get_facebook_data():
    """Get Facebook page statistics"""
    try:
        result = await get_facebook_stats()
        return {
            "success": result.get("connected", False),
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching Facebook stats: {str(e)}"
        )

@router.get("/social/instagram")
async def get_instagram_data():
    """Get Instagram business account statistics"""
    try:
        result = await get_instagram_stats()
        return {
            "success": result.get("connected", False),
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching Instagram stats: {str(e)}"
        )

class InstagramPostRequest(BaseModel):
    caption: str
    image_url: str

@router.post("/social/instagram/post")
async def create_instagram_post(request: InstagramPostRequest):
    """Post an image with caption to Instagram"""
    try:
        result = await service.post_to_instagram(
            caption=request.caption,
            image_url=request.image_url
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error posting to Instagram: {str(e)}"
        )
    
@router.get("/social/instagram/post/{post_id}")
async def get_instagram_post(post_id: str):
    """Fetch Instagram post details by post ID"""
    try:
        result = service.get_instagram_post(post_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching post: {str(e)}"
        )

@router.get("/social/stats")
async def get_all_stats():
    """Get statistics from all social media platforms"""
    try:
        result = await get_all_social_stats()
        return {
            "success": result.get("summary", {}).get("platforms_connected", 0) > 0,
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching social media stats: {str(e)}"
        )

@router.get("/social/post-insights")
async def fetch_post_insights(
    platform: str, post_id: str
) -> Dict[str, Any]:
    """
    API endpoint to fetch insights for a specific post
    """
    result = await get_post_insights(platform, post_id)
    return result


@router.get("/social/get_youtube_insights")
def get_youtube_insights(max_videos: Optional[int] = 5, max_comments: Optional[int] = 50):
    """
    API endpoint to fetch YouTube video analytics + top comments.
    Query parameters:
    - max_videos: number of videos to fetch (default 5)
    - max_comments: top comments per video (default 50)
    """
    try:
        videos = fetch_youtube_video_analytics(max_videos=max_videos, max_comments=max_comments)
        return {"success": True, "videos": videos}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/social/get_youtube_channel")
def get_youtube_channel():
    """
    Get basic information about the authenticated user's YouTube channel.
    """
    try:
        channel_info = fetch_youtube_channel_info()
        return channel_info
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/social/urls")
async def get_all_social_urls_endpoint(
    instagram_limit: Optional[int] = 10,
    youtube_limit: Optional[int] = 10
):
    """Get URLs from all social media platforms"""
    try:
        result = await get_all_social_urls(
            instagram_limit=instagram_limit, 
            youtube_limit=youtube_limit
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching social media URLs: {str(e)}"
        )
    
@router.get("/social/video_insights")
async def youtube_video_insights(video_id: str, max_comments: int = 50):
    return await get_youtube_video_insights(video_id=video_id, max_comments=max_comments)

class YouTubeAnalyzeRequest(BaseModel):
    video_id: str
    prompt: str
    max_comments: int = 50

@router.post("/social/youtube-analyze-llm")
async def youtube_analyze_llm(request: YouTubeAnalyzeRequest):
    return await analyze_youtube_video_with_llm(
        video_id=request.video_id,
        max_comments=request.max_comments,
        prompt=request.prompt,
    )

@router.get("/social/views", response_model=Dict[str, Any])
async def all_platform_stats():
    stats = await get_all_platform_stats()
    return stats

@router.get("/social/youtube", response_model=Dict[str, Any])
async def youtube_stats():
    yay = await get_youtube_stats()
    return yay


@router.get("/health")
async def health_check():
    logger.info("Health check endpoint called")
    return {
        "status": "success",
        "message": "Service is healthy"
    }

@router.post(
        path="/generate/caption",
        response_class=StreamingResponse,
        response_model_exclude_none=True,
        summary="Generate localized content (Legacy)",
        description="Legacy endpoint for generating localized content based on form data.",        
)
async def generate(
    request:Request, 
    data: ChatInput = Form(..., media_type="multipart/form-data"),
)-> StreamingResponse:
    session_id = data.session_id if data.session_id else str(uuid.uuid4())
   
    return await service.generate_caption(session_id=session_id, data=data)

@router.post(
        path="/generate/image",
        response_class=StreamingResponse,
        response_model_exclude_none=True,
        summary="Generate localized content",
        description="Generate localized content (text/image/video) based on user prompt.",        
)
async def generate(
    request:Request, 
    data: ChatInput = Form(..., media_type="multipart/form-data"),
)-> StreamingResponse:
    session_id = data.session_id if data.session_id else str(uuid.uuid4())

    return await service.generate_image(session_id=session_id, data=data)


@router.post(
        path="/generate/video",
        response_class=StreamingResponse,
        response_model_exclude_none=True,
        summary="Generate localized content",
        description="Generate localized content (text/image/video) based on user prompt.",        
)
async def generate(
    request:Request, 
    data: ChatInput = Form(..., media_type="multipart/form-data"),
)-> StreamingResponse:
    session_id = data.session_id if data.session_id else str(uuid.uuid4())
    return await service.generate_video(session_id=session_id, data=data)
    

# Pending - need to edit after database implemented
@router.get("/get_caption/{session_id}")
async def get_caption(session_id: str):
    """Get stored caption by session ID"""
    try:
        caption_data = await service.get_caption(session_id)
        if not caption_data:
            raise HTTPException(status_code=404, detail="No caption found for this session ID")
        
        return {
            "session_id": session_id,
            "caption": caption_data["caption"],
            "configuration": caption_data["configuration"],
            "prompt": caption_data["prompt"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving caption: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve caption")

@router.get("/list_captions")
async def list_all_captions():
    """List all stored captions (for debugging/admin purposes)"""
    try:
        all_captions = await service.get_all_captions()
        return {
            "total_count": len(all_captions),
            "captions": {
                request_id: {
                    "caption": data["caption"][:100] + "..." if len(data["caption"]) > 100 else data["caption"],
                    "prompt": data["prompt"][:50] + "..." if len(data["prompt"]) > 50 else data["prompt"]
                }
                for request_id, data in all_captions.items()
            }
        }
    except Exception as e:
        logger.error(f"Error listing captions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list captions")

@router.post(
    path="/search/music",
    response_model=MusicSearchUrlResponse,
    response_model_exclude_none=True,
    summary="Search for Malaysian music",
    description="Search for suitable Malaysian music based on marketing content analysis using AI and YouTube integration.",
)
async def search_music(
    request: Request,
    content: str = Form(..., description="Text content or image description for music matching"),
    file: Union[UploadFile, str, None] = File(None, description="Optional image file for multimodal analysis"),
    configuration: Optional[str] = Form(None, description="Search preferences and constraints as JSON string"),
    mood: Optional[str] = Form(None, description="Target mood/genre"),
    language: Optional[str] = Form("malay", description="Preferred language context"),
    target_audience: Optional[str] = Form("general", description="Target audience demographic"),
    platform: Optional[str] = Form("instagram", description="Social media platform for optimization"),
    session_id: Optional[str] = Form(None, description="The session ID to maintain conversation history")
) -> MusicSearchUrlResponse:
    session_id = session_id if session_id else str(uuid.uuid4())

    # Handle file parameter - convert empty string to None
    processed_file = None
    if file and isinstance(file, UploadFile) and file.filename:
        processed_file = file

    # Parse configuration from JSON string if provided
    parsed_configuration = None
    if configuration and configuration.strip():
        try:
            parsed_configuration = json.loads(configuration)
        except json.JSONDecodeError:
            logger.warning(f"[{session_id}] Invalid JSON in configuration, using None")
            parsed_configuration = None

    # Create MusicSearchInput object
    music_input = MusicSearchInput(
        content=content,
        file=processed_file,
        configuration=parsed_configuration,
        mood=mood,
        language=language,
        target_audience=target_audience,
        platform=platform,
        session_id=session_id,
    )

    try:
        # Create service instance
        music_service = MusicSearchService()

        # Perform the search -> returns a single YouTube URL string
        youtube_url = await music_service.search_music(session_id, music_input)

        return MusicSearchUrlResponse(session_id=session_id, youtube_url=youtube_url)

    except MusicSearchException as e:
        logger.error(f"[{session_id}] Music search error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[{session_id}] Unexpected error in music search: {str(e)}")
        raise HTTPException(status_code=500, detail="Music search service unavailable")
    
@router.post("/video/url")
async def get_video_presigned_url(request: UrlRequest):
    """Generate presigned URLs for S3 video - Both download and view versions"""
    try:
        logger.info(f"Generating presigned URLs for: {request.s3_uri}")
        
        result = await service.generate_presigned_url(request.s3_uri)
        
        if result is None:
            raise HTTPException(status_code=400, detail="Failed to generate presigned URLs")
        
        return {
            "success": True,
            "data": result,
            "urls": {
                "download": result["download_url"],
                "view": result["view_url"]
            },
            "metadata": {
                "expires_in_seconds": result["expire_time"],
                "bucket": result["bucket"],
                "key": result["key"],
                "s3_uri": result["s3_uri"]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating presigned URLs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate video URLs")

@router.post("/object/url/download")
async def get_object_direct_url(request: UrlRequest):
    """Generate direct S3 object URL - PUBLIC access only (bucket must be public)"""
    try:
        logger.info(f"Generating direct object URL for: {request.s3_uri}")

        result = await service.generate_download_object_url(request.s3_uri)

        if result is None:
            raise HTTPException(status_code=400, detail="Invalid S3 URI or failed to generate URL")
        
        return {
            "success": True,
            "object_url": result,
            "s3_uri": request.s3_uri,
            "url_type": "direct",
            "note": "This URL only works if the S3 bucket/object is publicly accessible"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating direct object URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate direct object URL")
        logger.error(f"Error generating presigned URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate video URL")

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@router.get("/api/latest-image")
async def get_latest_image():
    """Get the filename of the latest generated image from the output directory"""
    try:
        output_dir = "output"
        if not os.path.exists(output_dir):
            raise HTTPException(status_code=404, detail="Output directory not found")
        
        # Get all image files from output directory
        image_patterns = ["*.png", "*.jpg", "*.jpeg", "*.gif", "*.webp"]
        image_files = []
        
        for pattern in image_patterns:
            image_files.extend(glob.glob(os.path.join(output_dir, pattern)))
        
        if not image_files:
            raise HTTPException(status_code=404, detail="No images found in output directory")
        
        # Get the latest image based on modification time
        latest_image = max(image_files, key=os.path.getmtime)
        filename = os.path.basename(latest_image)
        
        return {"filename": filename, "path": f"/output/{filename}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving latest image: {str(e)}")

@router.post("/object/url/view")
async def get_object_direct_url(request: UrlRequest):
    """Generate direct S3 object URL - PUBLIC access only (bucket must be public)"""
    try:
        logger.info(f"Generating direct object URL for: {request.s3_uri}")

        result = await service.generate_view_object_url(request.s3_uri, type=request.type)

        if result is None:
            raise HTTPException(status_code=400, detail="Invalid S3 URI or failed to generate URL")
        
        return {
            "success": True,
            "object_url": result,
            "s3_uri": request.s3_uri,
            "url_type": "direct",
            "note": "This URL only works if the S3 bucket/object is publicly accessible"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating direct object URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate direct object URL")