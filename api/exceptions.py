"""
Custom exceptions for SmartAILocalizer API
"""
from typing import Optional, Dict, Any


class SmartAILocalizerException(Exception):
    """Base exception for SmartAILocalizer"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class AudioSearchException(SmartAILocalizerException):
    """Exception raised during audio search operations"""
    pass


class ComplianceCheckException(SmartAILocalizerException):
    """Exception raised during compliance checking operations"""
    pass


class DatabaseException(SmartAILocalizerException):
    """Exception raised during database operations"""
    pass


class AWSBedrockException(SmartAILocalizerException):
    """Exception raised during AWS Bedrock operations"""
    pass


class ValidationException(SmartAILocalizerException):
    """Exception raised during input validation"""
    pass


class ConfigurationException(SmartAILocalizerException):
    """Exception raised due to configuration issues"""
    pass


class MusicSearchException(SmartAILocalizerException):
    """Exception raised during music search operations"""
    pass


class BedrockMusicAnalysisException(MusicSearchException):
    """Exception raised during AWS Bedrock music analysis"""
    pass


class YouTubeSearchException(MusicSearchException):
    """Exception raised during YouTube API operations"""
    pass


class MusicRecommendationException(MusicSearchException):
    """Exception raised during music recommendation logic"""
    pass


class InvalidMusicInputException(MusicSearchException):
    """Exception raised for invalid music search input"""
    pass