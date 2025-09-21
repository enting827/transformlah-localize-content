import asyncio
import base64
import os
import json
import re
import time
from typing import Dict, Optional, List, Any
import random
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import ValidationError
import requests

from dotenv import load_dotenv
import httpx
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from fastapi.responses import StreamingResponse
from pydantic import ValidationError
from logging_config import get_logger
from repository import Repository
from schemas import (
    ChatInput, MusicSearchInput, MusicSearchResult, MusicSearchResponse, 
    SongsPayload, AgentOutputSong, AgentOutputSongsPayload, Song,
    ImageConfiguration, ImageQuality, BackgroundStyle
)
from prompts import text_gen_prompt, img_gen_prompt, music_search_prompt, video_gen_prompt
from exceptions import (
    SmartAILocalizerException
)
import logging
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from logging_config import get_logger
from schemas import ChatInput
from prompts import text_gen_prompt, img_gen_prompt, video_gen_prompt

# Custom exceptions for music search
class BedrockMusicAnalysisException(SmartAILocalizerException):
    """Exception raised during Bedrock music analysis operations"""
    pass

class YouTubeSearchException(SmartAILocalizerException):
    """Exception raised during YouTube search operations"""
    pass

class MusicRecommendationException(SmartAILocalizerException):
    """Exception raised during music recommendation operations"""
    pass

class InvalidMusicInputException(SmartAILocalizerException):
    """Exception raised during input validation"""
    pass

logger = get_logger(__name__, logging.DEBUG)

load_dotenv()

FACEBOOK_GRAPH_URL = os.getenv("FACEBOOK_GRAPH_URL")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_ACCOUNT_ID")
TEXT_LLM_MODEL = os.getenv("TEXT_LLM_MODEL", "amazon.nova-lite-v1:0")
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-1")
aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_session_token = os.getenv("AWS_SESSION_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_API_KEY")

TOKEN_PATH = "token.json"  

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

repository = Repository()

bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",  
)

bedrock_ren = boto3.client(
    "bedrock-runtime",
    region_name=BEDROCK_REGION,
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    aws_session_token=aws_session_token,
)

caption_store: Dict[str, Dict] = {}

async def generate_caption(session_id: str, data: ChatInput) -> StreamingResponse:
    try:
        prompt = data.prompt
        configuration = data.configuration
        model_id = os.getenv("TEXT_LLM_MODEL")
        region = os.getenv("BEDROCK_REGION", "us-east-1")

        # Create an Amazon Bedrock client
        client = boto3.client(
            service_name="bedrock-runtime",
            region_name=region
        )

        # Get conversation history
        history = await repository.get_conversation_history(session_id)

        # Create conversation from history
        conversation = []
        for entry in history:
            role = entry.get('user_id')
            content = entry.get('content')
            if role and content:
                conversation.append({
                    "role": "user" if role == "user" else "assistant",
                    "content": [{"text": content}]
                })

        # Add the current user's prompt to the conversation for the API call
        conversation.append({
            "role": "user",
            "content": [{"text": prompt}]
        })

        # Save user prompt to history
        await repository.save_conversation_entry(session_id, 'user', prompt, 'text')

        logger.info(f"[{session_id}] Starting streaming conversation with model: {model_id}")

        logger.debug(f"[{session_id}] System Prompt: "+text_gen_prompt(configuration))

        # Streaming response function
        async def event_stream():
            try:
                # Send the message to the model with streaming
                streaming_response = client.converse_stream(
                    modelId=model_id,
                    messages=conversation,
                    system=[{"text": text_gen_prompt(configuration)}],
                    inferenceConfig={"temperature": 1, "topP": 0.9},
                )

                # Enhanced variables for caption detection
                full_text = ""
                first_content = True
                caption_buffer = ""
                inside_caption = False
                pending_buffer = ""  # Buffer to hold potentially incomplete tags
                
                def process_text_with_buffer(new_text):
                    """Process text with buffering to handle split tags"""
                    nonlocal pending_buffer, inside_caption, caption_buffer
                    
                    # Combine pending buffer with new text
                    combined_text = pending_buffer + new_text
                    processed_text = ""
                    new_pending = ""
                    
                    i = 0
                    while i < len(combined_text):
                        char = combined_text[i]
                        
                        if char == '<' and not inside_caption:
                            # Potential start of opening tag
                            tag_end = combined_text.find('>', i)
                            if tag_end != -1:
                                potential_tag = combined_text[i:tag_end + 1]
                                if potential_tag == '<caption>':
                                    # Found complete opening tag - don't add tag to output
                                    inside_caption = True
                                    i = tag_end + 1
                                    continue
                                else:
                                    # Not a caption tag, add to processed text
                                    processed_text += char
                                    i += 1
                            else:
                                # Incomplete tag, might be split
                                remaining_text = combined_text[i:]
                                if any(remaining_text.startswith(prefix) for prefix in ['<', '<c', '<ca', '<cap', '<capt', '<capti', '<captio']):
                                    # Potentially incomplete opening tag
                                    new_pending = remaining_text
                                    break
                                else:
                                    processed_text += char
                                    i += 1
                        
                        elif char == '<' and inside_caption:
                            # Potential start of closing tag
                            tag_end = combined_text.find('>', i)
                            if tag_end != -1:
                                potential_tag = combined_text[i:tag_end + 1]
                                if potential_tag == '</caption>':
                                    # Found complete closing tag
                                    inside_caption = False
                                    
                                    # Store the caption
                                    if caption_buffer.strip():
                                        asyncio.create_task(repository.save_conversation_entry(
                                            session_id=session_id,
                                            user_id='assistant',  # The model is the assistant
                                            content=caption_buffer.strip(),
                                            content_type='text'
                                        ))
                                        logger.info(f"[{session_id}] Caption stored: {caption_buffer.strip()[:50]}...")
                                        logger.debug(f"[{session_id}] Caption stored: {caption_buffer.strip()}")
                                    
                                    # Reset caption buffer
                                    caption_buffer = ""
                                    i = tag_end + 1
                                    continue
                                else:
                                    # Not a closing caption tag, add to caption buffer AND processed text
                                    caption_buffer += char
                                    processed_text += char
                                    i += 1
                            else:
                                # Incomplete closing tag, might be split
                                remaining_text = combined_text[i:]
                                if any(remaining_text.startswith(prefix) for prefix in ['<', '</', '</c', '</ca', '</cap', '</capt', '</capti', '</captio']):
                                    # Potentially incomplete closing tag
                                    new_pending = remaining_text
                                    break
                                else:
                                    # Add to both caption buffer and display
                                    caption_buffer += char
                                    processed_text += char
                                    i += 1
                        
                        else:
                            if inside_caption:
                                # Inside caption: add to both caption buffer AND display
                                caption_buffer += char
                                processed_text += char
                            else:
                                # Outside caption: just add to display
                                processed_text += char
                            i += 1
                    
                    # Update pending buffer
                    pending_buffer = new_pending
                    
                    return processed_text
                
                for chunk in streaming_response["stream"]:
                    if "contentBlockDelta" in chunk:
                        text = chunk["contentBlockDelta"]["delta"]["text"]
                        
                        # Skip initial whitespace/newlines for the first chunk
                        if first_content and text.strip() == "":
                            continue
                        
                        # After first non-empty content, set flag to False
                        if first_content and text.strip():
                            first_content = False
                        
                        full_text += text
                        
                        # Process text with buffer handling
                        processed_text = process_text_with_buffer(text)
                        
                        # Send processed text (includes caption content, but not the tags)
                        if processed_text:
                            yield f"data: {json.dumps({'text': processed_text, 'type': 'chunk'})}\n\n"
                    
                    elif "messageStop" in chunk:
                        # Process any remaining pending buffer
                        if pending_buffer:
                            if inside_caption:
                                # Add to both caption buffer and display
                                caption_buffer += pending_buffer
                                yield f"data: {json.dumps({'text': pending_buffer, 'type': 'chunk'})}\n\n"
                            else:
                                # Send remaining non-caption text
                                yield f"data: {json.dumps({'text': pending_buffer, 'type': 'chunk'})}\n\n"
                        
                        # End of message, send final metadata
                        stop_reason = chunk["messageStop"].get("stopReason", "end_turn")

                        # Check if full_text contains a <caption>...</caption> block
                        has_caption = bool(re.search(r"<caption>.*?</caption>", full_text, re.DOTALL))

                        yield f"data: {json.dumps({'stopReason': stop_reason, 'type': 'stop', 'has_caption': has_caption, 'session_id': session_id})}\n\n"
                    
                    elif "metadata" in chunk:
                        # Send usage metadata if available
                        metadata = chunk["metadata"]
                        if "usage" in metadata:
                            usage = metadata["usage"]
                            yield f"data: {json.dumps({'usage': usage, 'type': 'metadata'})}\n\n"
                
                logger.info(f"[{session_id}] Completed streaming. Total text length: {len(full_text)}")
                logger.debug(f"[{session_id}] Completed streaming. Full Text: {full_text.strip()}")

                yield f"data: [DONE]\n\n"

            except Exception as e:
                logger.error(f"[{session_id}] Error in streaming: {str(e)}")
                yield f"data: {json.dumps({'error': str(e), 'type': 'error'})}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    
    except Exception as e:
        error_message = str(e)

        async def error_stream():
            yield f"data: {json.dumps({'error': error_message, 'type': 'error'})}\n\n"

        return StreamingResponse(error_stream(), media_type="text/event-stream")


async def get_caption(session_id: str) -> Optional[Dict]:
    """Retrieve stored caption by session ID"""
    history = await repository.get_conversation_history(session_id)
    # Find the latest text content in the history
    for item in reversed(history):
        if item.get('type') == 'text':
            return {
                'session_id': session_id,
                'caption': item.get('text'),
                'configuration': {},
                'prompt': ''
            }
    return None

async def get_all_captions() -> Dict[str, Dict]:
    """Get all stored captions (for debugging) - NOTE: This is not implemented with DynamoDB to avoid expensive scan operations."""
    return caption_store


async def generate_image(session_id: str, data: ChatInput) -> StreamingResponse:
    try:
        # Input validation
        if not data or not data.prompt:
            logger.error(f"[{session_id}] Missing or empty prompt")
            async def error_stream():
                yield f"data: {json.dumps({'error': 'Prompt is required for image generation', 'type': 'error', 'session_id': session_id})}\n\n"
            return StreamingResponse(error_stream(), media_type="text/event-stream")

        prompt = data.prompt.strip()
        configuration = data.configuration or {}
        
        # Handle uploaded image file conversion to base64
        img_uploaded_base64 = None
        if data.file:
            try:
                # Read the uploaded file content
                file_content = await data.file.read()
                file_size = len(file_content)
                
                # Check file size (max 5MB)
                max_file_size = 20 * 1024 * 1024  # 20MB
                if file_size > max_file_size:
                    logger.error(f"[{session_id}] File too large: {file_size} bytes (max: {max_file_size} bytes)")
                    async def error_stream():
                        yield f"data: {json.dumps({'error': f'File size too large ({file_size/1024/1024:.1f}MB). Maximum allowed is 5MB.', 'type': 'error', 'session_id': session_id})}\n\n"
                    return StreamingResponse(error_stream(), media_type="text/event-stream")
                
                # Check if it's an image file
                content_type = data.file.content_type
                if content_type and content_type.startswith('image/'):
                    # Validate image dimensions using PIL
                    try:
                        from PIL import Image
                        import io
                        
                        # Create image object to check dimensions
                        image = Image.open(io.BytesIO(file_content))
                        width, height = image.size
                        pixel_count = width * height
                        
                        # AWS Bedrock limit: maximum 4,194,304 pixels
                        max_pixels = 4194304
                        
                        logger.info(f"[{session_id}] Image dimensions: {width}x{height} ({pixel_count} pixels)")
                        
                        if pixel_count > max_pixels:
                            logger.error(f"[{session_id}] Image too large: {pixel_count} pixels (max: {max_pixels} pixels)")
                            async def error_stream():
                                yield f"data: {json.dumps({'error': f'Image resolution too high ({width}x{height} = {pixel_count:,} pixels). Maximum allowed is {max_pixels:,} pixels. Please resize your image.', 'type': 'error', 'session_id': session_id})}\n\n"
                            return StreamingResponse(error_stream(), media_type="text/event-stream")
                        
                        # Convert to base64 string
                        img_uploaded_base64 = base64.b64encode(file_content).decode('utf-8')
                        logger.info(f"[{session_id}] Image file validated and converted to base64 (size: {file_size} bytes, dimensions: {width}x{height}, type: {content_type})")
                        
                    except Exception as pil_error:
                        logger.error(f"[{session_id}] Error validating image: {str(pil_error)}")
                        async def error_stream():
                            yield f"data: {json.dumps({'error': 'Invalid image file or unsupported format', 'type': 'error', 'session_id': session_id})}\n\n"
                        return StreamingResponse(error_stream(), media_type="text/event-stream")
                else:
                    logger.warning(f"[{session_id}] Uploaded file is not an image (type: {content_type}), ignoring")
                    img_uploaded_base64 = None
                    
                # Reset file pointer for potential future use
                data.file.seek(0)
                
            except Exception as file_error:
                logger.error(f"[{session_id}] Error processing uploaded file: {str(file_error)}")
                async def error_stream():
                    yield f"data: {json.dumps({'error': 'File Uploaded must be an image (jpg, jpeg, png)', 'type': 'error', 'session_id': session_id})}\n\n"
                return StreamingResponse(error_stream(), media_type="text/event-stream")
        
        # Environment variable validation
        model_id = os.getenv("IMAGE_LLM_MODEL")
        region = os.getenv("BEDROCK_REGION", "us-east-1")

        logger.info(f"[{session_id}] Starting image generation with Amazon Nova Canvas: {model_id}")
        logger.debug(f"[{session_id}] Prompt: {prompt}")
        logger.debug(f"[{session_id}] Configuration: {configuration}")

        # Create an Amazon Bedrock client
        try:
            client = boto3.client(
                service_name="bedrock-runtime",
                region_name=region,
                config=Config(
                    retries={
                        'max_attempts': 3,
                        'mode': 'standard'
                    },
                    read_timeout=120,  # Increased timeout for image generation
                    connect_timeout=30
                )
            )
        except Exception as client_error:
            logger.error(f"[{session_id}] Failed to create Bedrock client: {str(client_error)}")
            async def error_stream():
                yield f"data: {json.dumps({'error': 'Failed to initialize AWS client', 'type': 'error', 'session_id': session_id})}\n\n"
            return StreamingResponse(error_stream(), media_type="text/event-stream")
        
        # Get conversation history
        history = await repository.get_conversation_history(session_id)
        
        # Save user prompt to history
        await repository.save_conversation_entry(session_id, 'user', prompt, 'text')

        # Append the current prompt to the in-memory history for immediate use
        history.append({'type': 'text', 'text': prompt, 'user_id': 'user', 'content': prompt})


        # Streaming response function for Amazon Nova Canvas
        async def image_event_stream():
            try:
                logger.info(f"[{session_id}] Calling Amazon Nova Canvas for image generation...")
                
                # Parse configuration as ImageConfiguration
                try:
                    image_config = ImageConfiguration.model_validate(configuration)
                except ValidationError as e:
                    logger.error(f"[{session_id}] Invalid image configuration: {e}")
                    yield f"data: {json.dumps({'error': 'Invalid image configuration', 'details': str(e), 'type': 'error', 'session_id': session_id})}\n\n"
                    return
                
                # Extract configuration parameters for image generation
                platform = configuration.get("platform", "instagram").lower()
                content_type = configuration.get("content_type", "post").lower()
                quality = configuration.get("quality", "standard")  # standard or premium
                num_images = configuration.get("numberOfImages", 1)
                
                # Get platform-specific dimensions
                image_specs = get_image_specifications(image_config)

                # No more parsing needed - directly get width and height
                width = image_specs["width"]
                height = image_specs["height"]

                logger.info(f"[{session_id}] Using dimensions: {width}x{height} for {platform} {content_type}")
                
                # Generate a random seed
                seed = random.randint(0, 858993460)
                
                # Enhanced prompt with Malaysian localization context from img_gen_prompt
                # enhanced_prompt = f"{img_gen_prompt(configuration)}\n\nUser Request: {prompt}"
                enhanced_prompt = f"Always create Malaysia style image. Strictly follow user request\n\nUser Request: {prompt}"
                
                
                
                last_image_s3 = None
                for item in reversed(history):
                    if item.get('type') == 'image':
                        last_image_s3 = item.get('source').get('s3Location')
                        break

                native_request = {}
                if last_image_s3:
                    native_request = {
                        "imageGenerationConfig": {
                            "numberOfImages": 1,
                            "height": 1024,
                            "width": 1024,
                            "cfgScale": 8.0
                        }
                    }
                    # Fetch the image from S3
                    s3_client = boto3.client('s3', region_name=region)
                    s3_object = s3_client.get_object(Bucket=last_image_s3.get('bucket'), Key=last_image_s3.get('key'))
                    last_image_bytes = s3_object['Body'].read()

                    native_request["taskType"] = "IMAGE_VARIATION"
                    native_request["imageVariationParams"] = {
                        "images": [base64.b64encode(last_image_bytes).decode('utf-8')],
                        "text": prompt
                    }
                
                # Only add conditionImage if we have a valid base64 image
                elif img_uploaded_base64:
                    text_to_image_params = {
                        "text": enhanced_prompt
                    }
                    text_to_image_params["conditionImage"] = img_uploaded_base64
                    text_to_image_params["controlMode"] = "CANNY_EDGE" #CANNY_EDGE or SEGMENTATION
                    text_to_image_params["controlStrength"] = 0.7 # 0 to 1
                    
                    logger.info(f"[{session_id}] Including condition image in request")
                
                    native_request = {
                        "taskType": "TEXT_IMAGE",
                        "textToImageParams": text_to_image_params,
                        "imageGenerationConfig": {
                            "cfgScale": 10,  # Prompt Strength
                            "seed": seed,
                            "quality": quality,  # "standard" or "premium"
                            "height": height,
                            "width": width,
                            "numberOfImages": min(num_images, 5),  # Nova Canvas supports up to 5 images
                        },
                    }
                else:
                    # Format the request payload using Nova Canvas native structure
                    text_to_image_params = {
                        "text": enhanced_prompt
                    }

                    native_request = {
                        "taskType": "TEXT_IMAGE",
                        "textToImageParams": text_to_image_params,
                        "imageGenerationConfig": {
                            "cfgScale": 10,  # Prompt Strength
                            "seed": seed,
                            "quality": quality,  # "standard" or "premium"
                            "height": height,
                            "width": width,
                            "numberOfImages": min(num_images, 5),  # Nova Canvas supports up to 5 images
                        },
                    }

                # Log the request details
                logger.debug(f"[{session_id}] Nova Canvas request: {json.dumps(native_request, indent=2)}")
                
                # Convert the native request to JSON
                request_body = json.dumps(native_request)
                
                # Invoke the model with the request
                response = client.invoke_model(modelId=model_id, body=request_body)
                
                # Decode the response body
                model_response = json.loads(response["body"].read())
                
                logger.debug(f"[{session_id}] Nova Canvas response received")
                
                # Validate response structure
                if "images" not in model_response or not model_response["images"]:
                    logger.error(f"[{session_id}] No images in Nova Canvas response")
                    yield f"data: {json.dumps({'error': 'No images generated by Nova Canvas', 'type': 'error', 'session_id': session_id})}\n\n"
                    return
                
                # Process generated images
                images = model_response["images"]
                logger.info(f"[{session_id}] Nova Canvas generated {len(images)} image(s)")
                
                # Send each generated image
                for idx, base64_image_data in enumerate(images):
                    try:
                        # Validate base64 image data
                        if not base64_image_data:
                            logger.warning(f"[{session_id}] Empty image data for image {idx + 1}")
                            continue
                        
                        # Prepare image data for saving
                        save_data = {
                            'source': {
                                'bytes': base64_image_data,
                                'format': 'png'  # Nova Canvas generates PNG images
                            }
                        }
                        
                        # Save the image
                        save_result = await save_generated_image(save_data, session_id)

                        # Save image to repository
                        image_data = base64.b64decode(base64_image_data)
                        s3_url = await repository.save_conversation_entry(session_id, 'assistant', 'Image', 'image', image_data)

                        
                        # Build response according to your specified format
                        image_response = {
                            'image': {
                                'format': 'png',  # Nova Canvas generates PNG images
                                'source': {
                                    'bytes': base64_image_data  # Already base64 encoded
                                },
                                's3_url': s3_url
                            },
                            'type': 'image',
                            'session_id': session_id,
                            'image_index': idx + 1,
                            'total_images': len(images),
                            'metadata': {
                                'model': model_id,
                                'dimensions': f"{width}x{height}",
                                'quality': quality,
                                'seed': seed,
                                'image_size': image_config.image_size,
                                'background_style': image_config.background_style
                            },
                            'save_result': save_result  # Add save result to response
                        }
                        
                        # Send the image response
                        yield f"data: {json.dumps(image_response)}\n\n"
                        
                        logger.info(f"[{session_id}] Image {idx + 1}/{len(images)} sent successfully ({width}x{height}, {quality} quality)")
                        
                    except Exception as image_error:
                        logger.error(f"[{session_id}] Error processing image {idx + 1}: {str(image_error)}")
                        yield f"data: {json.dumps({'error': f'Failed to process image {idx + 1}', 'type': 'error', 'session_id': session_id})}\n\n"
                
                # Send completion metadata
                yield f"data: {json.dumps({'type': 'stop', 'stopReason': 'end_turn', 'session_id': session_id, 'has_image': len(images) > 0, 'image_count': len(images), 'model': model_id, 'generation_config': {'dimensions': f'{width}x{height}', 'quality': quality, 'seed': seed}})}\n\n"

                logger.info(f"[{session_id}] Amazon Nova Canvas image generation completed successfully")
                yield f"data: [DONE]\n\n"

            except json.JSONDecodeError as json_error:
                logger.error(f"[{session_id}] JSON error in Nova Canvas response: {str(json_error)}")
                yield f"data: {json.dumps({'error': 'Invalid response format from Nova Canvas', 'type': 'error', 'session_id': session_id})}\n\n"
            except Exception as stream_error:
                logger.error(f"[{session_id}] Unexpected error in Nova Canvas stream: {str(stream_error)}")
                yield f"data: {json.dumps({'error': f'Nova Canvas generation failed: {str(stream_error)}', 'type': 'error', 'session_id': session_id})}\n\n"

        return StreamingResponse(image_event_stream(), media_type="text/event-stream")

    except Exception as e:
        error_message = str(e)
        logger.error(f"[{session_id}] Critical error in generate_image: {str(e)}")
        async def error_stream():
            yield f"data: {json.dumps({'error': f'Image generation service unavailable: {error_message}', 'type': 'error', 'session_id': session_id})}\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")


def get_image_specifications(image_config: ImageConfiguration) -> dict:
    """
    Get image specifications based on the ImageConfiguration schema.
    Ensures dimensions are compatible with Amazon Nova Canvas limits (64x64 to 2048x2048).
    
    Args:
        image_config (ImageConfiguration): Image configuration from request
    
    Returns:
        dict: Image specifications including width, height, ratio, and format
    """
    try:
        # Get dimensions directly from image_dimensions
        width = image_config.image_dimensions.width
        height = image_config.image_dimensions.height
        
        # Ensure dimensions are within Nova Canvas limits
        width = max(64, min(2048, width))
        height = max(64, min(2048, height))
        
        return {
            "width": width,
            "height": height,
            "ratio": image_config.image_aspect_ratio,
            "quality": image_config.image_quality,
            "background_style": image_config.background_style,
            "format": "PNG"  # Nova Canvas generates PNGs
        }
        
    except AttributeError:
        # Fallback to default specification if configuration is incomplete
        logger.warning("Invalid image configuration. Using default 1024x1024 square format.")
        return {
            "width": 1024,
            "height": 1024,
            "ratio": "1:1",
            "quality": ImageQuality.STANDARD,
            "background_style": BackgroundStyle.SOLID,
            "format": "PNG"
        }


class MusicSearchService:
    """Service for Malaysian music search and recommendation using a Bedrock Agent."""
    
    def __init__(self):
        """Initializes the MusicSearchService."""
        # Bedrock Agent details
        self.agent_id = os.getenv("MUSIC_AGENT_ID")
        self.agent_alias_id = os.getenv("MUSIC_AGENT_ALIAS_ID")
        self.bedrock_region = os.getenv("BEDROCK_REGION", "us-east-1")
        
        if not self.agent_id or not self.agent_alias_id:
            logger.warning("MUSIC_AGENT_ID or MUSIC_AGENT_ALIAS_ID not set - Bedrock Agent integration will be disabled")
        
        self.bedrock_agent_client = None
        
    async def initialize_clients(self):
        """Initialize AWS Bedrock Agent client."""
        try:
            if self.agent_id and self.agent_alias_id:
                self.bedrock_agent_client = boto3.client(
                    service_name="bedrock-agent-runtime",
                    region_name=self.bedrock_region,
                    config=Config(
                        retries={'max_attempts': 3, 'mode': 'standard'},
                        read_timeout=120,
                        connect_timeout=30
                    )
                )
                logger.info("MusicSearchService client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MusicSearchService client: {str(e)}")
            raise BedrockMusicAnalysisException(f"Client initialization failed: {str(e)}")
    
    async def analyze_content(self, session_id: str, data: MusicSearchInput) -> str:
        """
        Analyze content using an AWS Bedrock Agent and return a YouTube embed URL directly.
        """
        try:
            if not self.bedrock_agent_client:
                await self.initialize_clients()

            if not self.bedrock_agent_client:
                raise BedrockMusicAnalysisException(
                    "Bedrock Agent client not initialized. "
                    "Check MUSIC_AGENT_ID and MUSIC_AGENT_ALIAS_ID."
                )

            start_time = time.time()
            content_description = data.content
            if data.file:
                content_description += f" [Image file provided: {data.file.filename}]"

            agent_session_id = f"music-search-{session_id}"
            logger.info(
                f"[{session_id}] Starting Bedrock Agent ({self.agent_id}) analysis "
                f"with session ID: {agent_session_id}"
            )

            response = self.bedrock_agent_client.invoke_agent(
                agentId=self.agent_id,
                agentAliasId=self.agent_alias_id,
                sessionId=agent_session_id,
                inputText=content_description,
                enableTrace=True
            )

            response_content = ""
            for event in response.get("completion"):
                chunk = event.get("chunk")
                if chunk:
                    response_content += chunk.get("bytes").decode("utf-8")

            processing_time = time.time() - start_time
            logger.info(f"[{session_id}] Bedrock Agent analysis completed in {processing_time:.2f}s")
            logger.debug(f"[{session_id}] Raw Agent Response: {response_content}")

            # Clean up potential formatting (markdown, whitespace, etc.)
            match = re.search(r"(https:\/\/www\.youtube\.com\/embed\/[a-zA-Z0-9_-]+)", response_content)
            if not match:
                raise BedrockMusicAnalysisException(
                    f"No valid YouTube embed URL found in agent response: {response_content}"
                )

            youtube_url = match.group(1)
            return youtube_url

        except Exception as e:
            logger.error(f"[{session_id}] Error in Bedrock Agent content analysis: {str(e)}")
            raise BedrockMusicAnalysisException(f"Content analysis failed: {str(e)}")


    async def search_music(self, session_id: str, data: MusicSearchInput) -> str:
        """
        Main method to search for Malaysian music using a Bedrock Agent.
        Returns a single YouTube embed URL string.
        """
        try:
            start_time = time.time()

            # Get the embed URL directly
            youtube_url = await self.analyze_content(session_id, data)

            processing_time = time.time() - start_time
            logger.info(f"[{session_id}] Music search completed in {processing_time:.2f}s")
            logger.debug(f"[{session_id}] Final YouTube URL: {youtube_url}")

            # Save conversation
            await repository.save_conversation_entry(
                session_id=session_id,
                user_id="user",
                content=data.content,
                content_type="text"
            )
            await repository.save_conversation_entry(
                session_id=session_id,
                user_id="assistant",
                content=youtube_url,
                content_type="music_search_result"
            )

            return youtube_url

        except Exception as e:
            logger.error(f"[{session_id}] Error in music search: {str(e)}")
            raise BedrockMusicAnalysisException(f"Music search failed: {str(e)}")


async def generate_video(session_id: str, data: ChatInput) -> StreamingResponse:
    try:
        prompt = data.prompt.strip()
        configuration = data.configuration or {}
        uploaded_img_file = data.file or None

        # Convert uploaded image file to base64 string if present
        img_uploaded_base64 = None
        if uploaded_img_file:
            try:
                # Read the uploaded file content
                file_content = await uploaded_img_file.read()
                file_size = len(file_content)
                
                # Check file size (max 20MB)
                max_file_size = 20 * 1024 * 1024  # 20MB
                if file_size > max_file_size:
                    logger.error(f"[{session_id}] File too large: {file_size} bytes (max: {max_file_size} bytes)")
                    async def error_stream():
                        yield f"data: {json.dumps({'error': f'File size too large ({file_size/1024/1024:.1f}MB). Maximum allowed is 20MB.', 'type': 'error', 'session_id': session_id})}\n\n"
                    return StreamingResponse(error_stream(), media_type="text/event-stream")
                
                # Check if it's an image file
                content_type = uploaded_img_file.content_type
                if content_type and content_type.startswith('image/'):
                    # Validate image format and dimensions using PIL
                    try:
                        from PIL import Image
                        import io
                        
                        # Create image object to check dimensions and format
                        image = Image.open(io.BytesIO(file_content))
                        
                        # Check format (only PNG and JPEG allowed for video generation)
                        if image.format not in ['PNG', 'JPEG', 'JPG']:
                            logger.error(f"[{session_id}] Invalid image format: {image.format}. Only PNG and JPEG are supported for video generation.")
                            async def error_stream():
                                yield f"data: {json.dumps({'error': f'Invalid image format: {image.format}. Only PNG and JPEG are supported for video generation.', 'type': 'error', 'session_id': session_id})}\n\n"
                            return StreamingResponse(error_stream(), media_type="text/event-stream")
                        
                        # Check dimensions (must be exactly 1280x720 for video generation)
                        width, height = image.size
                        required_width, required_height = 1280, 720
                        
                        if width != required_width or height != required_height:
                            logger.error(f"[{session_id}] Invalid image dimensions: {width}x{height}. Required: {required_width}x{required_height} for video generation.")
                            async def error_stream():
                                yield f"data: {json.dumps({'error': f'Invalid image dimensions: {width}x{height}. Video generation requires exactly {required_width}x{required_height} pixels.', 'type': 'error', 'session_id': session_id})}\n\n"
                            return StreamingResponse(error_stream(), media_type="text/event-stream")
                        
                        # Convert to base64 if all validations pass
                        img_uploaded_base64 = base64.b64encode(file_content).decode('utf-8')
                        logger.info(f"[{session_id}] Image validated successfully: {image.format} format, {width}x{height} dimensions")
                        
                    except Exception as pil_error:
                        logger.error(f"[{session_id}] Error validating image with PIL: {str(pil_error)}")
                        async def error_stream():
                            yield f"data: {json.dumps({'error': 'Invalid or corrupted image file. Please upload a valid PNG or JPEG image.', 'type': 'error', 'session_id': session_id})}\n\n"
                        return StreamingResponse(error_stream(), media_type="text/event-stream")
                        
                else:
                    logger.warning(f"[{session_id}] Uploaded file is not an image (type: {content_type}), ignoring")
                    img_uploaded_base64 = None
                    
                # Reset file pointer for potential future use
                await uploaded_img_file.seek(0)
                
            except Exception as e:
                logger.error(f"[{session_id}] Error processing uploaded image: {str(e)}")
                async def error_stream():
                    yield f"data: {json.dumps({'error': 'Error processing uploaded image. Please upload a valid PNG or JPEG image with 1280x720 dimensions.', 'type': 'error', 'session_id': session_id})}\n\n"
                return StreamingResponse(error_stream(), media_type="text/event-stream")
        
        # Environment variable validation
        model_id = os.getenv("VIDEO_LLM_MODEL", "amazon.nova-reel-v1:0")
        region = os.getenv("BEDROCK_REGION", "us-east-1")
        output_s3_uri = os.getenv("OUTPUT_S3_URI")
        
        if not output_s3_uri or "REPLACE-WITH-YOUR-S3-BUCKET-NAME" in output_s3_uri:
            logger.error(f"[{session_id}] OUTPUT_S3_URI environment variable not properly configured")
            async def error_stream():
                yield f"data: {json.dumps({'error': 'S3 output bucket not configured. Please set OUTPUT_S3_URI environment variable.', 'type': 'error', 'session_id': session_id})}\n\n"
            return StreamingResponse(error_stream(), media_type="text/event-stream")

        logger.info(f"[{session_id}] Starting video generation with Amazon Nova Reel: {model_id}")
        logger.debug(f"[{session_id}] Prompt: {prompt}")
        logger.debug(f"[{session_id}] Configuration: {configuration}")
        logger.debug(f"[{session_id}] output_s3_uri: {output_s3_uri}")

        # Create an Amazon Bedrock client
        try:
            client = boto3.client(
                service_name="bedrock-runtime",
                region_name=region,
                config=Config(
                    retries={
                        'max_attempts': 3,
                        'mode': 'standard'
                    },
                    read_timeout=300,  # 5 minutes for video generation
                    connect_timeout=30
                )
            )
        except Exception as client_error:
            logger.error(f"[{session_id}] Failed to create Bedrock client: {str(client_error)}")
            async def error_stream():
                yield f"data: {json.dumps({'error': 'Failed to initialize AWS client', 'type': 'error', 'session_id': session_id})}\n\n"
            return StreamingResponse(error_stream(), media_type="text/event-stream")

        # Streaming response function for Amazon Nova Reel
        async def video_event_stream():
            try:
                logger.info(f"[{session_id}] Starting video generation job...")
                
                # Extract configuration parameters for video generation
                platform = configuration.get("platform", "instagram").lower()
                content_type = configuration.get("content_type", "post").lower()
                duration = configuration.get("duration", 6)  # Default 6 seconds
                fps = configuration.get("fps", 24)  # Default 24 fps
                
                # Get platform-specific video dimensions
                video_specs = get_video_specifications(platform, content_type)
                dimension = f"{video_specs['width']}x{video_specs['height']}"
                
                # Generate a random seed
                seed = random.randint(0, 2147483646)
                
                # Enhanced prompt with Malaysian localization context
                # enhanced_prompt = f"{video_gen_prompt(configuration)}\n\nUser Request: {prompt}"
                
                # Ensure prompt length is within limits (Nova Reel might have limits)
                # if len(enhanced_prompt) > 1024:
                    # Use shorter prompt if too long
                enhanced_prompt = f"Malaysian {content_type} video for {platform}: {prompt}"
                
                data = {
                    'type': 'status',
                    'status': 'initializing',
                    'message': 'Starting video generation job...',
                    'session_id': session_id,
                    'metadata': {
                        'platform': platform,
                        'content_type': content_type,
                        'duration': duration,
                        'dimension': dimension,
                        'fps': fps
                    }
                }
                # Send initial status
                yield f"data: {json.dumps(data)}\n\n"
                
                # Configure the video generation request
                model_input = {
                    "taskType": "TEXT_VIDEO",
                    "textToVideoParams": {
                        "text": enhanced_prompt
                    },
                    "videoGenerationConfig": {
                        "fps": fps,
                        "durationSeconds": min(duration, 6),  # Nova Reel max is 6 seconds
                        "dimension": dimension,
                        "seed": seed,
                    }
                }
                
                # Only add images if we have a valid base64 image
                if img_uploaded_base64:
                    model_input["textToVideoParams"]["images"] = [{
                        "format": "jpeg",  # Nova Reel accepts both jpeg and png
                        "source": {"bytes": img_uploaded_base64}
                    }]
                    logger.info(f"[{session_id}] Including input image in video generation request")
                
                # Create unique S3 path for this request
                output_config = {"s3OutputDataConfig": {"s3Uri": output_s3_uri}}
                
                logger.debug(f"[{session_id}] Nova Reel request: {json.dumps(model_input, indent=2)}")
                
                # Start the async video generation job
                response = client.start_async_invoke(
                    modelId=model_id, 
                    modelInput=model_input, 
                    outputDataConfig=output_config,
                    tags=[
                        {
                            'key': 'session_id',
                            'value': session_id
                        }
                    ]
                )
                
                invocation_arn = response["invocationArn"]
                logger.info(f"[{session_id}] Video generation job started with ARN: {invocation_arn}")
                
                data = {
                    'type': 'status',
                    'status': 'job_started',
                    'message': f'Video generation job started. Estimated completion: {duration * 10} seconds',
                    'session_id': session_id,
                    'invocation_arn': invocation_arn,
                    'metadata': {
                        'estimated_duration': f'{duration * 10} seconds',
                        'output_location': output_s3_uri
                    }
                }
                # Send job started confirmation
                yield f"data: {json.dumps(data)}\n\n"
                
                # Poll for job completion
                max_attempts = 120  # 30 minutes max (15 sec intervals)
                attempt = 0
                
                while attempt < max_attempts:
                    await asyncio.sleep(15)  # Wait 15 seconds between checks
                    attempt += 1
                    
                    try:
                        job_status = client.get_async_invoke(invocationArn=invocation_arn)
                        status = job_status["status"]
                        
                        data = {
                            'type': 'status',
                            'status': status.lower(),
                            'message': f'Video generation status: {status} (Check {attempt}/{max_attempts})',
                            'session_id': session_id,
                            'progress': min(90, (attempt / max_attempts) * 100)
                        }
                        # Send status update
                        yield f"data: {json.dumps(data)}\n\n"
                        
                        if status == "Completed":
                            bucket_uri = job_status["outputDataConfig"]["s3OutputDataConfig"]["s3Uri"]
                            final_video_uri = f"{bucket_uri}/output.mp4"

                            presigned_result = await generate_presigned_url(final_video_uri)
                            download_url = presigned_result["download_url"] if presigned_result else None
                            view_url = presigned_result["view_url"] if presigned_result else None
                            presigned_expires = presigned_result["expire_time"] if presigned_result else None

                            # Send successful video response
                            video_response = {
                                'video': {
                                    'format': 'mp4',
                                    'source': {
                                        's3Location': {
                                            'uri': final_video_uri,
                                            'bucketOwner': 'your-account'  # You may want to get this from config
                                        },
                                        'download_url': download_url,  # URL for downloading
                                        'view_url': view_url,  # URL for inline viewing (plays in browser)
                                        'presigned_expires': presigned_expires
                                        
                                    }
                                },
                                'type': 'video',
                                'session_id': session_id,
                                'metadata': {
                                    'model': model_id,
                                    'dimension': dimension,
                                    'duration': duration,
                                    'fps': fps,
                                    'seed': seed,
                                    'platform': platform,
                                    'content_type': content_type,
                                    'generation_time': f'{attempt * 15} seconds'
                                }
                            }
                            
                            yield f"data: {json.dumps(video_response)}\n\n"
                            
                            data = {
                                'type': 'stop',
                                'stopReason': 'completed',
                                'session_id': session_id,
                                'has_video': True,
                                'video_uri': final_video_uri,
                                'download_url': download_url,  # URL for downloading
                                'view_url': view_url,  # URL for inline viewing
                                'presigned_expires': presigned_expires,
                                'generation_config': {
                                    'dimension': dimension,
                                    'duration': duration,
                                    'fps': fps,
                                    'seed': seed
                                }
                            }
                            # Send completion metadata
                            yield f"data: {json.dumps(data)}\n\n"
                            
                            logger.info(f"[{session_id}] Video generation completed successfully: {final_video_uri}")
                            break
                            
                        elif status == "Failed":
                            error_message = job_status.get('failureMessage', 'Unknown error occurred')
                            logger.error(f"[{session_id}] Video generation failed: {error_message}")
                            
                            data = {
                                'error': f'Video generation failed: {error_message}', 
                                'type': 'error', 
                                'session_id': session_id
                            }
                            yield f"data: {json.dumps(data)}\n\n"
                            break
                            
                        elif status in ["InProgress", "Submitted"]:
                            # Continue polling
                            continue
                        else:
                            # Unknown status
                            logger.warning(f"[{session_id}] Unknown job status: {status}")
                            continue
                            
                    except Exception as poll_error:
                        logger.error(f"[{session_id}] Error polling job status: {str(poll_error)}")
                        data = {
                            'type': 'status',
                            'status': 'polling_error',
                            'message': f'Error checking job status: {str(poll_error)}',
                            'session_id': session_id
                        }
                        yield f"data: {json.dumps(data)}\n\n"
                
                # If we exit the loop without completion, it's a timeout
                if attempt >= max_attempts:
                    logger.error(f"[{session_id}] Video generation timed out after {max_attempts * 15} seconds")
                    data = {
                        'error': 'Video generation timed out. Please check your S3 bucket later.',
                        'type': 'error',
                        'session_id': session_id,
                        'invocation_arn': invocation_arn
                    }
                    yield f"data: {json.dumps(data)}\n\n"

                yield f"data: [DONE]\n\n"

            except Exception as stream_error:
                logger.error(f"[{session_id}] Unexpected error in video generation stream: {str(stream_error)}")
                yield f"data: {json.dumps({'error': f'Video generation failed: {str(stream_error)}', 'type': 'error', 'session_id': session_id})}\n\n"

        return StreamingResponse(video_event_stream(), media_type="text/event-stream")

    except Exception as e:
        logger.error(f"[{session_id}] Critical error in generate_video: {str(e)}")
        async def error_stream():
            yield f"data: {json.dumps({'error': f'Video generation service unavailable: {str(e)}', 'type': 'error', 'session_id': session_id})}\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")



def get_video_specifications(platform: str, content_type: str) -> dict:
    """
    Get video specifications based on platform and content type
    Compatible with Amazon Nova Reel dimension requirements
    
    Args:
        platform (str): Social media platform
        content_type (str): Type of content (story, post, reel, etc.)
    
    Returns:
        dict: Video specifications including width, height, ratio, and format
    """
    
    # Default specifications (Nova Reel compatible)
    default_spec = {
        "width": 1280,
        "height": 720,
        "ratio": "16:9 (Landscape)",
        "format": "MP4"
    }
    
    platform = platform.lower()
    content_type = content_type.lower()
    
    # Platform and content type specific specifications
    specs = {
        "instagram": {
            "post": {"width": 1280, "height": 720, "ratio": "16:9 (Landscape)", "format": "MP4"},
            "story": {"width": 720, "height": 1280, "ratio": "9:16 (Vertical)", "format": "MP4"},
            "reel": {"width": 720, "height": 1280, "ratio": "9:16 (Vertical)", "format": "MP4"},
            "igtv": {"width": 720, "height": 1280, "ratio": "9:16 (Vertical)", "format": "MP4"}
        },
        "tiktok": {
            "post": {"width": 720, "height": 1280, "ratio": "9:16 (Vertical)", "format": "MP4"},
            "story": {"width": 720, "height": 1280, "ratio": "9:16 (Vertical)", "format": "MP4"}
        },
        "youtube": {
            "short": {"width": 720, "height": 1280, "ratio": "9:16 (Vertical)", "format": "MP4"},
            "video": {"width": 1280, "height": 720, "ratio": "16:9 (Landscape)", "format": "MP4"}
        },
        "facebook": {
            "post": {"width": 1280, "height": 720, "ratio": "16:9 (Landscape)", "format": "MP4"},
            "story": {"width": 720, "height": 1280, "ratio": "9:16 (Vertical)", "format": "MP4"}
        }
    }
    
    # Get platform specs
    platform_specs = specs.get(platform, {})
    
    # Get content type specs, fallback to 'post' if not found
    content_spec = platform_specs.get(content_type) or platform_specs.get("post") or default_spec
    
    return content_spec

async def generate_download_object_url(s3_uri: str) -> Optional[str]:
    """
    Generate a direct S3 object URL from S3 URI
    Note: This creates a public URL that only works if the bucket/object is publicly accessible.
    For private buckets, use generate_presigned_url() instead.
    
    Args:
        s3_uri (str): S3 URI in format s3://bucket/key
        
    Returns:
        str: Direct S3 object URL or None if invalid URI
    """
    try:
        # Validate S3 URI format
        if not s3_uri or not s3_uri.startswith('s3://'):
            logger.error(f"Invalid S3 URI format: {s3_uri}")
            return None
        
        # Parse S3 URI
        path = s3_uri[5:]  # Remove 's3://'
        parts = path.split('/', 1)
        
        if len(parts) != 2:
            logger.error(f"Invalid S3 URI structure: {s3_uri}")
            return None
            
        bucket_name = parts[0]
        object_key = parts[1]
        
        # Get AWS region from environment
        region = os.getenv("BEDROCK_REGION", "us-east-1")
        
        # Generate direct S3 URL
        # Format: https://<bucket-name>.s3.<region>.amazonaws.com/<object-key>
        direct_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{object_key}"
        
        logger.info(f"Generated direct S3 URL: {direct_url}")
        
        return direct_url
        
    except Exception as e:
        logger.error(f"Error generating S3 object URL: {str(e)}")
        return None
    
async def generate_view_object_url(s3_uri: str, type:str = "video/mp4") -> Optional[str]:
    """
    Generate a public S3 object URL that forces inline viewing
    (video plays in browser instead of downloading).

    Args:
        s3_uri (str): S3 URI in format s3://bucket/key

    Returns:
        str: Direct S3 object view URL
    """
    try:
        from urllib.parse import urlparse
        # Parse the s3://bucket/key uri
        parsed = urlparse(s3_uri)
        bucket = parsed.netloc
        key = parsed.path.lstrip("/")

        if not bucket or not key:
            raise ValueError(f"Invalid S3 URI: {s3_uri}")

        # Create S3 client
        region = os.getenv("AWS_REGION", "us-east-1")
        s3 = boto3.client("s3", region_name=region)
        # Split directory and filename
        dir_name, file_name = os.path.split(key)

        # Split filename and extension
        base, ext = os.path.splitext(file_name)

        # Build new filename
        new_file_name = f"{base}-new{ext}"

        newkey=f"{dir_name}/{new_file_name}"

        # Copy object to itself to update metadata
        s3.copy_object(
            Bucket=bucket,
            CopySource={"Bucket": bucket, "Key": key},
            Key=newkey,
            ContentType=type,                  # ensure correct MIME
            ContentDisposition="inline",              # force view instead of download
            MetadataDirective="REPLACE",
        )

        # Return the direct public URL
        return f"https://{bucket}.s3.{region}.amazonaws.com/{newkey}"

    except Exception as e:
        print(f"Error generating view URL: {e}")
        return None


async def save_generated_image(image_data: dict, session_id: str) -> dict:
    """
    Save the generated image to a local output directory
    
    Args:
        image_data (dict): Dictionary containing image data with base64 bytes
        session_id (str): Unique request identifier for logging
        
    Returns:
        dict: Information about the saved image including path and status
    """
    try:
        # Get base64 string from image data
        base64_string = image_data.get("source", {}).get("bytes")
        if not base64_string:
            raise ValueError("No image data found")

        # Create output directory if it doesn't exist
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"[{session_id}] Created output directory: {output_dir}")

        # Generate filename with timestamp and format
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_format = image_data.get("format", "png").lower()
        filename = f"generated_image_{timestamp}_{session_id}.{image_format}"
        file_path = os.path.join(output_dir, filename)

        # Decode base64 to bytes and save
        image_bytes = base64.b64decode(base64_string)
        with open(file_path, "wb") as f:
            f.write(image_bytes)

        logger.info(f"[{session_id}] Successfully saved image to {file_path}")
        return {
            "success": True,
            "file_path": file_path,
            "file_name": filename,
            "directory": output_dir,
            "size_bytes": len(image_bytes)
        }

    except Exception as e:
        logger.error(f"[{session_id}] Error saving image: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

async def generate_presigned_url(s3_uri: str, expiration: int = 7200) -> Optional[str]:
    """
    Generate a presigned URL for an S3 object from S3 URI
    
    Args:
        s3_uri (str): S3 URI in format s3://bucket/key
        expiration (int): URL expiration time in seconds (default: 2 hours)
    
    Returns:
        str: Presigned URL or None if error
    """
    try:
        # Parse S3 URI
        if not s3_uri.startswith('s3://'):
            logger.error(f"Invalid S3 URI format: {s3_uri}")
            return None
        
        # Remove s3:// prefix and split bucket and key
        path = s3_uri[5:]  # Remove 's3://'
        parts = path.split('/', 1)
        if len(parts) != 2:
            logger.error(f"Invalid S3 URI structure: {s3_uri}")
            return None
            
        bucket_name = parts[0]
        object_key = parts[1]
        
        logger.info(f"Generating presigned URL - Bucket: {bucket_name}, Key: {object_key}")
        
        # Get AWS region from environment
        region = os.getenv("BEDROCK_REGION", "us-east-1")
        
        # Create S3 client
        s3_client = boto3.client('s3', region_name=region)
        
        # Log AWS identity for debugging
        try:
            sts_client = boto3.client('sts', region_name=region)
            identity = sts_client.get_caller_identity()
            logger.debug(f"AWS Identity - Account: {identity.get('Account')}, ARN: {identity.get('Arn')}")
        except Exception as identity_error:
            logger.warning(f"Could not get AWS identity: {str(identity_error)}")
        
        # Check if bucket exists and is accessible
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            logger.debug(f"Bucket {bucket_name} is accessible")
        except ClientError as bucket_error:
            error_code = bucket_error.response['Error']['Code']
            if error_code == '403':
                logger.error(f"Access denied to bucket {bucket_name} - check IAM permissions")
            elif error_code == '404':
                logger.error(f"Bucket {bucket_name} not found - check bucket name and region")
            else:
                logger.error(f"Bucket access error: {bucket_error.response['Error']['Message']}")
            return None
        
        # Check if object exists
        try:
            obj_response = s3_client.head_object(Bucket=bucket_name, Key=object_key)
            content_length = obj_response.get('ContentLength', 0)
            logger.info(f"Object found - Size: {content_length} bytes")
        except ClientError as obj_error:
            error_code = obj_error.response['Error']['Code']
            if error_code == '404':
                logger.error(f"Object not found: {object_key} in bucket {bucket_name}")
            elif error_code == '403':
                logger.error(f"Access denied to object: {object_key}")
            else:
                logger.error(f"Object access error: {obj_error.response['Error']['Message']}")
            return None
        
        # Generate presigned URL using the documented method
        download_presigned_url = s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': bucket_name, 'Key': object_key},
            ExpiresIn=expiration
        )

        view_presigned_url = s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket_name, 
                'Key': object_key,
                'ResponseContentType': 'video/mp4',           # Force content type
                'ResponseContentDisposition': 'inline'        # Force inline display
            },
            ExpiresIn=expiration
        )
        
        logger.info(f"Successfully generated presigned URLs for {s3_uri} (expires in {expiration}s)")
        
        # Log URL structure (without signature for security)
        download_url_base = download_presigned_url.split('?')[0]
        view_url_base = view_presigned_url.split('?')[0]
        logger.debug(f"Download URL base: {download_url_base}")
        logger.debug(f"View URL base: {view_url_base}")

        return {
            "download_url": download_presigned_url,
            "view_url": view_presigned_url,
            "expire_time": expiration,
            "s3_uri": s3_uri,
            "bucket": bucket_name,
            "key": object_key
        }
        
    except ClientError as e:
        logger.error(f"AWS ClientError generating presigned URL: {e.response['Error']['Code']} - {e.response['Error']['Message']}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error generating presigned URL: {str(e)}")
        return None

async def test_facebook_connection() -> Dict[str, Any]:
    """Test Facebook Graph API connection"""
    try:
        if not ACCESS_TOKEN:
            return {
                "platform": "Facebook",
                "connected": False,
                "status_code": None,
                "message": "Missing ACCESS_TOKEN environment variable",
                "error": "No access token provided"
            }

        url = f"{FACEBOOK_GRAPH_URL}/me"
        params = {"access_token": ACCESS_TOKEN}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            
            # Check if the response is successful
            if response.status_code == 200:
                try:
                    data = response.json()
                    return {
                        "platform": "Facebook",
                        "connected": True,
                        "status_code": response.status_code,
                        "message": "Connection successful",
                        "data": data
                    }
                except Exception as json_error:
                    return {
                        "platform": "Facebook",
                        "connected": False,
                        "status_code": response.status_code,
                        "message": "Invalid JSON response",
                        "error": f"JSON decode error: {str(json_error)}",
                        "raw_response": response.text[:500]  # First 500 chars
                    }
            else:
                # Try to get error details from response
                try:
                    error_data = response.json()
                    return {
                        "platform": "Facebook",
                        "connected": False,
                        "status_code": response.status_code,
                        "message": f"API request failed: {response.status_code}",
                        "error": error_data.get("error", {}).get("message", "Unknown API error"),
                        "error_details": error_data
                    }
                except:
                    return {
                        "platform": "Facebook",
                        "connected": False,
                        "status_code": response.status_code,
                        "message": f"API request failed: {response.status_code}",
                        "error": "Non-JSON error response",
                        "raw_response": response.text[:500]
                    }
                    
    except Exception as e:
        return {
            "platform": "Facebook",
            "connected": False,
            "status_code": None,
            "message": "Connection test failed",
            "error": str(e)
        }

def get_youtube_credentials():
    creds = None
    # Load saved credentials if they exist
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    # If no valid credentials, go through OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # auto refresh token
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret.json",
                SCOPES
            )
            creds = flow.run_local_server(port=8080, access_type="offline", prompt="consent")

        
        # Save credentials for next run
        with open(TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())
    
    return creds

async def get_facebook_stats() -> Dict[str, Any]:
    if not ACCESS_TOKEN or not FACEBOOK_PAGE_ID:
        return {"platform": "Facebook", "connected": False, "error": "Missing credentials"}

    url = f"{FACEBOOK_GRAPH_URL}/{FACEBOOK_PAGE_ID}"
    params = {
        "access_token": ACCESS_TOKEN,
        "fields": "followers_count,fan_count,posts.limit(1).summary(true),about,name,link,picture"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return {
                "platform": "Facebook",
                "connected": True,
                "name": data.get("name"),
                "followers": data.get("followers_count", 0),
                "likes": data.get("fan_count", 0),
                "posts": data.get("posts", {}).get("summary", {}).get("total_count", 0),
                "about": data.get("about"),
                "profile_url": data.get("link"),
                "profile_picture": data.get("picture", {}).get("data", {}).get("url"),
            }
        else:
            return {"platform": "Facebook", "connected": False, "error": response.json().get("error", {}).get("message", "Unknown error")}


async def get_instagram_stats() -> Dict[str, Any]:
    if not ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
        return {"platform": "Instagram", "connected": False, "error": "Missing credentials"}

    url = f"{FACEBOOK_GRAPH_URL}/{INSTAGRAM_ACCOUNT_ID}"
    params = {
        "access_token": ACCESS_TOKEN,
        "fields": "id,username,followers_count,follows_count,media_count,media{like_count,comments_count}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            media_data = data.get("media", {}).get("data", [])

            total_likes = sum(post.get("like_count", 0) for post in media_data)
            total_comments = sum(post.get("comments_count", 0) for post in media_data)
            engagement_rate = 0
            if data.get("followers_count") and media_data:
                engagement = (total_likes + total_comments) / len(media_data)
                engagement_rate = (engagement / data.get("followers_count")) * 100

            return {
                "platform": "Instagram",
                "connected": True,
                "id": data.get("id"),
                "username": data.get("username"),
                "followers": data.get("followers_count", 0),
                "following": data.get("follows_count", 0),
                "posts": data.get("media_count", 0),
                "total_likes": total_likes,
                "total_comments": total_comments,
                "engagement_rate": round(engagement_rate, 2)
            }
        else:
            return {"platform": "Instagram", "connected": False, "error": response.json().get("error", {}).get("message", "Unknown error")}


async def get_youtube_stats() -> Dict[str, Any]:
    """
    Get YouTube channel statistics using OAuth credentials.
    Includes: basic stats + analytics (views, watch time, average view duration, total likes).
    """
    try:
        creds = get_youtube_credentials()

        youtube_data = build("youtube", "v3", credentials=creds)
        youtube_analytics = build("youtubeAnalytics", "v2", credentials=creds)

        # Get channel info
        request = youtube_data.channels().list(part="id,snippet,statistics", mine=True)
        response = request.execute()
        if not response["items"]:
            return {"platform": "YouTube", "connected": False, "error": "Channel not found"}

        channel = response["items"][0]
        channel_id = channel["id"]
        stats = channel["statistics"]

        # Get total likes across all videos
        total_likes = 0
        next_page_token = None
        while True:
            search_request = youtube_data.search().list(
                part="id",
                channelId=channel_id,
                maxResults=50,
                pageToken=next_page_token,
                type="video",
                order="date"
            )
            search_response = search_request.execute()
            video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]

            if video_ids:
                videos_request = youtube_data.videos().list(
                    part="statistics",
                    id=",".join(video_ids)
                )
                videos_response = videos_request.execute()
                for v in videos_response.get("items", []):
                    total_likes += int(v["statistics"].get("likeCount", 0))

            next_page_token = search_response.get("nextPageToken")
            if not next_page_token:
                break

        # Channel-level analytics
        analytics_request = youtube_analytics.reports().query(
            ids=f"channel=={channel_id}",
            startDate="2000-01-01",
            endDate="2030-01-01",
            metrics="views,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost"
        )
        analytics_response = analytics_request.execute()
        analytics_data = {}
        if "rows" in analytics_response:
            row = analytics_response["rows"][0]
            headers = [col["name"] for col in analytics_response["columnHeaders"]]
            analytics_data = dict(zip(headers, row))

        return {
            "platform": "YouTube",
            "connected": True,
            "name": channel["snippet"]["title"],
            "subscribers": int(stats.get("subscriberCount", 0)),
            "views": int(stats.get("viewCount", 0)),
            "videos": int(stats.get("videoCount", 0)),
            "total_likes": total_likes,
            "profile_picture": channel["snippet"]["thumbnails"]["default"]["url"],
            "analytics": analytics_data
        }

    except Exception as e:
        return {"platform": "YouTube", "connected": False, "error": str(e)}

async def get_all_platform_stats() -> Dict[str, Any]:
    results = await asyncio.gather(
        get_facebook_stats(),
        get_instagram_stats(),
        get_youtube_stats()
    )

    # Initialize totals
    total_followers = 0
    total_likes = 0
    total_views = 0
    platforms_connected = 0

    for platform in results:
        if platform.get("connected"):
            platforms_connected += 1

            # Followers / subscribers
            if platform["platform"] == "YouTube":
                total_followers += platform.get("subscribers", 0)
            else:
                total_followers += platform.get("followers", 0)

            # Views
            total_views += platform.get("views", 0)

            # Likes field differs by platform
            if platform["platform"] == "Facebook":
                total_likes += platform.get("likes", 0)
            elif platform["platform"] == "Instagram":
                total_likes += platform.get("total_likes", 0)
            elif platform["platform"] == "YouTube":
                total_likes += platform.get("total_likes", 0)

    return {
        "platforms": {p["platform"].lower(): p for p in results},
        "summary": {
            "total_followers": total_followers,
            "total_likes": total_likes,
            "total_views": total_views,
            "platforms_connected": platforms_connected
        }
    }

async def get_all_social_stats() -> Dict[str, Any]:
    """Get statistics from all social media platforms"""\
    
    facebook_stats = await get_facebook_stats()
    instagram_stats = await get_instagram_stats()
    
    # Calculate total reach across platforms
    total_followers = (
        facebook_stats.get("followers", 0) +
        instagram_stats.get("followers", 0)
    )
    
    return {
        "facebook": facebook_stats,
        "instagram": instagram_stats,
        "summary": {
            "total_followers": total_followers,
            "platforms_connected": sum([
                facebook_stats.get("connected", False),
                instagram_stats.get("connected", False)
            ])
        }
    }


async def get_post_insights(platform: str, post_id: str) -> Dict[str, Any]:
    """
    Get insights of a specific post from Facebook or Instagram.
    """
    try:
        if not ACCESS_TOKEN:
            return {
                "platform": platform,
                "connected": False,
                "error": "Missing ACCESS_TOKEN"
            }

        # Supported metrics
        fb_metrics = "post_impressions,post_reactions_by_type_total,post_clicks,post_engaged_users"
        ig_metrics = "reach,saved,likes,comments,shares"

        if platform.lower() == "facebook":
            url = f"{FACEBOOK_GRAPH_URL}/{post_id}/insights"
            params = {
                "metric": fb_metrics,
                "access_token": ACCESS_TOKEN
            }
        elif platform.lower() == "instagram":
            url = f"{FACEBOOK_GRAPH_URL}/{post_id}/insights"
            params = {
                "metric": ig_metrics,
                "access_token": ACCESS_TOKEN
            }
        else:
            return {
                "platform": platform,
                "connected": False,
                "error": "Unsupported platform. Use 'facebook' or 'instagram'."
            }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                return {
                    "platform": platform,
                    "connected": True,
                    "post_id": post_id,
                    "insights": data.get("data", [])
                }
            else:
                error_data = response.json()
                return {
                    "platform": platform,
                    "connected": False,
                    "error": error_data.get("error", {}).get("message", "Unknown error")
                }

    except Exception as e:
        return {
            "platform": platform,
            "connected": False,
            "error": str(e)
        }

def fetch_youtube_video_analytics(max_videos: int = 5, max_comments: int = 50):
    """
    Fetch total analytics for videos on the authenticated user's channel,
    including top most-liked comments and video URL.
    """
    creds = get_youtube_credentials()

    youtube_data = build("youtube", "v3", credentials=creds)
    youtube_analytics = build("youtubeAnalytics", "v2", credentials=creds)

    # Get channel ID
    request = youtube_data.channels().list(part="id", mine=True)
    response = request.execute()
    channel_id = response["items"][0]["id"]

    # Get videos
    videos = []
    next_page_token = None
    while len(videos) < max_videos:
        video_request = youtube_data.search().list(
            part="id,snippet",
            channelId=channel_id,
            maxResults=min(max_videos - len(videos), 50),
            pageToken=next_page_token,
            type="video",
            order="date"
        )
        video_response = video_request.execute()
        for item in video_response["items"]:
            video_id = item["id"]["videoId"]
            videos.append({
                "video_id": video_id,
                "title": item["snippet"]["title"],
                "url": f"https://www.youtube.com/watch?v={video_id}"
            })
        next_page_token = video_response.get("nextPageToken")
        if not next_page_token:
            break

    # Get analytics and top comments
    for video in videos:
        analytics_request = youtube_analytics.reports().query(
            ids=f"channel=={channel_id}",
            startDate="2000-01-01",
            endDate="2030-01-01",
            metrics="views,likes,estimatedMinutesWatched",
            filters=f"video=={video['video_id']}"
        )
        analytics_response = analytics_request.execute()
        video["analytics"] = analytics_response.get("rows", [])

        comments = []
        next_comment_token = None
        while len(comments) < max_comments:
            comment_request = youtube_data.commentThreads().list(
                part="snippet",
                videoId=video["video_id"],
                maxResults=min(max_comments - len(comments), 50),
                order="relevance",
                pageToken=next_comment_token,
                textFormat="plainText"
            )
            comment_response = comment_request.execute()
            for item in comment_response.get("items", []):
                top_comment = item["snippet"]["topLevelComment"]["snippet"]
                comments.append({
                    "author": top_comment.get("authorDisplayName"),
                    "text": top_comment.get("textDisplay"),
                    "likeCount": top_comment.get("likeCount"),
                    "publishedAt": top_comment.get("publishedAt")
                })
            next_comment_token = comment_response.get("nextPageToken")
            if not next_comment_token:
                break
        video["top_comments"] = comments

    return videos


def fetch_youtube_channel_info() -> dict:
    """
    Fetch basic information about the authenticated user's YouTube channel.
    """
    creds = get_youtube_credentials()
    youtube_data = build("youtube", "v3", credentials=creds)

    # Get channel info
    channel_resp = youtube_data.channels().list(
        part="snippet,statistics",
        mine=True
    ).execute()

    if not channel_resp.get("items"):
        return {"success": False, "error": "No channel found for this account."}

    channel = channel_resp["items"][0]
    snippet = channel.get("snippet", {})
    stats = channel.get("statistics", {})

    return {
        "success": True,
        "channel": {
            "channel_id": channel.get("id"),
            "title": snippet.get("title"),
            "description": snippet.get("description"),
            "published_at": snippet.get("publishedAt"),
            "profile_picture": snippet.get("thumbnails", {}).get("default", {}).get("url"),
            "subscribers": stats.get("subscriberCount"),
            "total_views": stats.get("viewCount"),
            "total_videos": stats.get("videoCount")
        }
    }

async def get_instagram_post_urls(limit: int = 10) -> Dict[str, Any]:
    """Get recent Instagram post URLs and captions"""
    try:
        # Get the full Instagram stats first
        instagram_data = await get_instagram_stats()
        
        if not instagram_data.get("connected", False):
            return {
                "social_media": "instagram",
                "success": False,
                "error": instagram_data.get("error", "Not connected"),
                "posts": []
            }
        
        # Extract URLs and captions from recent posts
        recent_posts = instagram_data.get("recent_posts", [])
        posts: List[Dict[str, str]] = [
            {
                "url": post.get("url"),
                "caption": post.get("caption", ""),
                "post_id": post.get("post_id", "")
            }
            for post in recent_posts[:limit] if post.get("url")
        ]
        
        return {
            "social_media": "instagram",
            "success": True,
            "posts": posts,
            "total_posts": len(posts)
        }
        
    except Exception as e:
        return {
            "social_media": "instagram",
            "success": False,
            "error": str(e),
            "posts": []
        }


def get_youtube_video_urls(max_videos: int = 5) -> Dict[str, Any]:
    """Get recent YouTube video URLs and titles"""
    try:
        # Get the full YouTube analytics first
        videos_data = fetch_youtube_video_analytics(max_videos=max_videos, max_comments=1)
        
        # Extract URLs and titles
        videos: List[Dict[str, str]] = [
            {
                "url": video.get("url"),
                "title": video.get("title", ""),
                "video_id": video.get("video_id", "")
            }
            for video in videos_data if video.get("url")
        ]
        
        return {
            "social_media": "youtube",
            "success": True,
            "videos": videos,
            "total_videos": len(videos)
        }
        
    except Exception as e:
        return {
            "social_media": "youtube",
            "success": False,
            "error": str(e),
            "videos": []
        }

async def get_all_social_urls(instagram_limit: int = 10, youtube_limit: int = 5) -> Dict[str, Any]:
    """Get URLs + captions (Instagram) and URLs + titles (YouTube)"""
    try:
        instagram_data = await get_instagram_post_urls(limit=instagram_limit)
        youtube_data = get_youtube_video_urls(max_videos=youtube_limit)
        
        # Extract posts/videos safely
        instagram_posts = instagram_data.get("posts", [])
        youtube_videos = youtube_data.get("videos", [])
        
        return {
            "success": True,
            "data": {
                "instagram": instagram_posts,   # each contains {url, caption}
                "youtube": youtube_videos,     # each contains {url, title}
                "summary": {
                    "total_urls": len(instagram_posts) + len(youtube_videos),
                    "platforms": ["instagram", "youtube"]
                }
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": {
                "instagram": [],
                "youtube": [],
                "summary": {"total_urls": 0, "platforms": []}
            }
        }


async def get_youtube_video_insights(video_id: str, max_comments: int = 50) -> Dict[str, Any]:
    """Fetch insights and comments for a specific YouTube video by video_id"""
    try:
        creds = get_youtube_credentials()
        youtube_data = build("youtube", "v3", credentials=creds)
        youtube_analytics = build("youtubeAnalytics", "v2", credentials=creds)

        # Get channel ID
        request = youtube_data.channels().list(part="id", mine=True)
        response = request.execute()
        channel_id = response["items"][0]["id"]

        # Get video details
        video_request = youtube_data.videos().list(
            part="snippet,statistics",
            id=video_id
        )
        video_response = video_request.execute()

        if not video_response.get("items"):
            return {
                "social_media": "youtube",
                "success": False,
                "error": "Video not found",
                "video": None
            }

        video_item = video_response["items"][0]
        title = video_item["snippet"]["title"]
        url = f"https://www.youtube.com/watch?v={video_id}"

        # Get analytics
        analytics_request = youtube_analytics.reports().query(
            ids=f"channel=={channel_id}",
            startDate="2000-01-01",
            endDate="2030-01-01",
            metrics="views,likes,estimatedMinutesWatched",
            filters=f"video=={video_id}"
        )
        analytics_response = analytics_request.execute()
        analytics = analytics_response.get("rows", [])

        # Get comments
        comments: List[Dict[str, Any]] = []
        next_comment_token = None
        while len(comments) < max_comments:
            comment_request = youtube_data.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=min(max_comments - len(comments), 50),
                order="relevance",
                pageToken=next_comment_token,
                textFormat="plainText"
            )
            comment_response = comment_request.execute()
            for item in comment_response.get("items", []):
                top_comment = item["snippet"]["topLevelComment"]["snippet"]
                comments.append({
                    "author": top_comment.get("authorDisplayName"),
                    "text": top_comment.get("textDisplay"),
                    "likeCount": top_comment.get("likeCount"),
                    "publishedAt": top_comment.get("publishedAt")
                })
            next_comment_token = comment_response.get("nextPageToken")
            if not next_comment_token:
                break

        return {
            "social_media": "youtube",
            "success": True,
            "video": {
                "video_id": video_id,
                "title": title,
                "url": url,
                "analytics": analytics,
                "comments": comments
            }
        }

    except Exception as e:
        return {
            "social_media": "youtube",
            "success": False,
            "error": str(e),
            "video": None
        }
    
async def post_to_instagram(caption: str, image_url: str):
    """
    Post an image with caption to Instagram using the Graph API.

    Args:
        caption (str): The caption for the Instagram post
        image_url (str): Public URL of the image to post

    Returns:
        dict: Response from Instagram API
    """

    # Step 1: Create container
    url = f"https://graph.facebook.com/v23.0/{INSTAGRAM_ACCOUNT_ID}/media"
    payload = {
        "caption": caption,
        "image_url": image_url,
        "access_token": ACCESS_TOKEN
    }

    response = requests.post(url, data=payload).json()
    print("Container Response:", response)

    if "id" not in response:
        raise Exception(f"Failed to create media container: {response}")

    creation_id = response["id"]

    # Step 2: Publish container
    publish_url = f"https://graph.facebook.com/v23.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
    publish_payload = {
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN
    }

    publish_response = requests.post(publish_url, data=publish_payload).json()
    print("Publish Response:", publish_response)

    return publish_response

async def analyze_youtube_video_with_llm(video_id: str, max_comments: int, prompt: str) -> Dict[str, Any]:
    """
    Analyze a YouTube video using insights + comments, then run Bedrock LLM analysis
    """
    try:
        # 1. Get video insights (stats + comments)
        youtube_data = await get_youtube_video_insights(video_id=video_id, max_comments=max_comments)

        if not youtube_data.get("success", False):
            return {
                "success": False,
                "error": youtube_data.get("error", "Failed to fetch YouTube insights"),
                "analysis": None
            }

        video_info = youtube_data.get("video", {})

        # 2. Extract analytics with labels
        analytics_raw = video_info.get("analytics", [])
        analytics = {}
        if analytics_raw and len(analytics_raw[0]) == 3:
            analytics = {
                "views": analytics_raw[0][0],
                "likes": analytics_raw[0][1],
                "estimatedMinutesWatched": analytics_raw[0][2],
            }

        # 3. Prepare input for LLM
        llm_input = {
            "prompt": prompt,
            "video_id": video_info.get("video_id", ""),
            "title": video_info.get("title", ""),
            "url": video_info.get("url", ""),
            "analytics": analytics,
            "top_comments": video_info.get("comments", []),
        }

        # 4. Call Bedrock LLM (using converse API)
        response = bedrock.converse(
            modelId=TEXT_LLM_MODEL,
            messages=[{
                "role": "user",
                "content": [{
                    "text": f"Analyze this YouTube video:\n\n{json.dumps(llm_input, ensure_ascii=False, indent=2)}\n\nTask: {prompt}"
                }]
            }],
            inferenceConfig={"temperature": 0.5, "topP": 0.9, "maxTokens": 500}
        )

        # 5. Parse LLM output
        output_text = response["output"]["message"]["content"][0]["text"]

        return {
            "success": True,
            "video": {
                "video_id": video_info.get("video_id", ""),
                "title": video_info.get("title", ""),
                "url": video_info.get("url", ""),
                "analytics": analytics,
                "top_comments": video_info.get("comments", []),
            },
            "analysis": output_text,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "analysis": None
        }
    
def get_instagram_post(post_id: str):
    """
    Get Instagram post information by post ID.
    Args:
        post_id (str): The IG post ID returned when you published a post.
    Returns:
        dict: Post details from the Instagram Graph API
    """
    url = f"https://graph.facebook.com/v23.0/{post_id}"
    params = {
        "fields": "id,caption,media_type,media_url,permalink,timestamp",
        "access_token": ACCESS_TOKEN
    }

    response = requests.get(url, params=params).json()
    return response
