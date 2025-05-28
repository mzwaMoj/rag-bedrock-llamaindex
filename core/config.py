"""
Configuration settings for the RAG application
"""
import os
from typing import Dict, Any


class Config:
    """Configuration class for RAG application"""
      # Default settings
    DEFAULT_DATA_DIR = "./data"
    DEFAULT_AWS_REGION = "eu-central-1"
    DEFAULT_TOP_K = 3
    DEFAULT_CHUNK_SIZE = 512
    DEFAULT_CHUNK_OVERLAP = 20
    
    # Model configurations
    CLAUDE_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"
    CLAUDE_35_MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    TITAN_EMBEDDING_MODEL_V1 = "amazon.titan-embed-text-v1"
    TITAN_EMBEDDING_MODEL_V2 = "amazon.titan-embed-text-v2:0"
    
    # AWS regions with Bedrock support
    SUPPORTED_REGIONS = [
        "us-east-1",
        "us-west-2", 
        "eu-west-1",
        "eu-central-1",
        "ap-southeast-1",
        "ap-northeast-1"
    ]
    
    @classmethod
    def get_aws_credentials(cls) -> Dict[str, str]:
        """Get AWS credentials from environment variables"""
        return {
            "aws_access_key_id": os.getenv("aws_access_key_id"),
            "aws_secret_access_key": os.getenv("aws_secret_access_key"),
            "aws_session_token": os.getenv("aws_session_token")
        }
    
    @classmethod
    def validate_credentials(cls) -> bool:
        """Validate that required AWS credentials are available"""
        creds = cls.get_aws_credentials()
        return all(creds.values())
    
    @classmethod
    def get_model_config(cls, model_type: str = "claude") -> Dict[str, Any]:
        """Get model configuration"""
        if model_type == "claude":
            return {
                "model_id": cls.CLAUDE_MODEL_ID,
                "max_tokens": 5000,
                "temperature": 0.1,
                "top_p": 0.9
            }
        elif model_type == "claude_35":
            return {
                "model_id": cls.CLAUDE_35_MODEL_ID,
                "max_tokens": 5000,
                "temperature": 0.1,
                "top_p": 0.9
            }
        elif model_type == "titan_embedding":
            return {
                "model_id": cls.TITAN_EMBEDDING_MODEL_V1,
                "dimensions": 1536
            }
        else:
            raise ValueError(f"Unknown model type: {model_type}")


class AppTexts:
    """Text constants for the application"""
    
    APP_TITLE = "🤖 ExconAI RAG Chatbot"
    APP_DESCRIPTION = "Ask questions about your documents using AWS Bedrock AI"
    
    WELCOME_MESSAGE = "👋 Welcome! Please initialize the RAG system using the sidebar to get started."
    
    INITIALIZATION_SUCCESS = "✅ RAG System initialized successfully!"
    INITIALIZATION_ERROR = "❌ Failed to initialize RAG system. Check your configuration."
    
    SYSTEM_ACTIVE = "🟢 RAG System: Active"
    SYSTEM_INACTIVE = "🟡 RAG System: Not initialized"
    
    EXAMPLE_QUESTIONS = {
        "General Questions": [
            "What is AWS Bedrock?",
            "Explain the main concepts in the documents",
            "Summarize the key points"
        ],
        "Specific Queries": [
            "What are Authorised Dealers?",
            "List the BOP codes mentioned", 
            "Show payment instruction formats"
        ]
    }
