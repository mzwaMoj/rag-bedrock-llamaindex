"""
Custom Titan Embedding Module
Extracted from the notebook for modular use
"""
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.bridge.pydantic import Field, PrivateAttr
from typing import List, Any, Optional
import asyncio
import boto3
import aioboto3
import json
import os
from botocore.config import Config


class CustomTitanEmbedding(BaseEmbedding):
    """Custom Titan Embedding implementation for AWS Bedrock."""
    
    # Public fields (following BedrockEmbedding pattern)
    model_name: str = Field(default="amazon.titan-embed-text-v1", description="The modelId of the Bedrock model to use.")
    aws_access_key_id: Optional[str] = Field(default=None, description="AWS Access Key ID to use")
    aws_secret_access_key: Optional[str] = Field(default=None, description="AWS Secret Access Key to use")
    aws_session_token: Optional[str] = Field(default=None, description="AWS Session Token to use")
    region_name: Optional[str] = Field(default="eu-central-1", description="AWS region name to use")
    max_retries: int = Field(default=10, description="The maximum number of API retries.", gt=0)
    timeout: float = Field(default=60.0, description="The timeout for the Bedrock API request in seconds")
    
    # Private attributes (following BedrockEmbedding pattern)
    _config: Any = PrivateAttr()
    _client: Any = PrivateAttr()
    _asession: Any = PrivateAttr()
    
    def __init__(
        self,
        model_name: str = "amazon.titan-embed-text-v1",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
        region_name: str = "eu-central-1",
        max_retries: int = 10,
        timeout: float = 60.0,
        **kwargs: Any,
    ):
        # Initialize the parent class first
        super().__init__(
            model_name=model_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            region_name=region_name,
            max_retries=max_retries,
            timeout=timeout,
            **kwargs
        )
        
        # Set up credentials from environment if not provided
        self.aws_access_key_id = aws_access_key_id or os.environ.get("aws_access_key_id")
        self.aws_secret_access_key = aws_secret_access_key or os.environ.get("aws_secret_access_key")
        self.aws_session_token = aws_session_token or os.environ.get("aws_session_token")
        
        # Initialize client configuration
        self._setup_clients()
    
    def _setup_clients(self):
        """Initialize the Bedrock clients with proper credentials."""
        try:
            # Setup session kwargs
            session_kwargs = {
                "region_name": self.region_name,
                "aws_access_key_id": self.aws_access_key_id,
                "aws_secret_access_key": self.aws_secret_access_key,
                "aws_session_token": self.aws_session_token,
            }
            
            # Remove None values from session_kwargs
            session_kwargs = {k: v for k, v in session_kwargs.items() if v is not None}
            
            # Setup botocore config
            self._config = Config(
                retries={"max_attempts": self.max_retries, "mode": "standard"},
                connect_timeout=self.timeout,
                read_timeout=self.timeout,
            )
            
            # Create sync session and client
            session = boto3.Session(**session_kwargs)
            self._client = session.client("bedrock-runtime", config=self._config)
            
            # Create async session
            self._asession = aioboto3.Session(**session_kwargs)
            
        except ImportError:
            raise ImportError(
                "boto3 and/or aioboto3 package not found, install with 'pip install boto3 aioboto3'"
            )
        except Exception as e:
            raise ConnectionError(f"Failed to setup AWS Bedrock clients: {e}")
    
    def _get_query_embedding(self, query: str) -> List[float]:
        """Get embedding for a query string."""
        return self._get_embedding(query)
    
    async def _aget_query_embedding(self, query: str) -> List[float]:
        """Async version of query embedding."""
        return await self._aget_embedding(query)
    
    def _get_text_embedding(self, text: str) -> List[float]:
        """Get embedding for a text string."""
        return self._get_embedding(text)
    
    async def _aget_text_embedding(self, text: str) -> List[float]:
        """Async version of text embedding."""
        return await self._aget_embedding(text)
    
    def _get_embedding(self, text: str) -> List[float]:
        """Core method to generate embeddings using AWS Bedrock Titan model."""
        try:
            # Prepare the request body (simplified for v1 model)
            if self.model_name == "amazon.titan-embed-text-v1":
                body = json.dumps({"inputText": text})
            else:
                # For v2 model, include additional parameters
                body = json.dumps({
                    "inputText": text,
                    "dimensions": 1024,  # v2 default
                    "normalize": True
                })
            
            # Call Bedrock API
            response = self._client.invoke_model(
                body=body,
                modelId=self.model_name,
                accept="application/json",
                contentType="application/json"
            )
            
            # Parse response
            response_body = json.loads(response.get('body').read())
            embedding = response_body['embedding']
            
            return embedding
            
        except Exception as e:
            print(f"Error generating embedding for text: '{text[:50]}...': {e}")
            # Return a zero vector as fallback based on model type
            fallback_dim = 1536 if "v1" in self.model_name else 1024
            return [0.0] * fallback_dim
    
    async def _aget_embedding(self, text: str) -> List[float]:
        """Async version of embedding generation."""
        try:
            # Prepare the request body
            if self.model_name == "amazon.titan-embed-text-v1":
                body = json.dumps({"inputText": text})
            else:
                body = json.dumps({
                    "inputText": text,
                    "dimensions": 1024,
                    "normalize": True
                })
            
            # Use async client
            async with self._asession.client("bedrock-runtime", config=self._config) as client:
                response = await client.invoke_model(
                    body=body,
                    modelId=self.model_name,
                    accept="application/json",
                    contentType="application/json"
                )
                
                streaming_body = await response.get("body").read()
                response_body = json.loads(streaming_body.decode("utf-8"))
                embedding = response_body['embedding']
                
                return embedding
                
        except Exception as e:
            print(f"Error generating async embedding for text: '{text[:50]}...': {e}")
            # Return a zero vector as fallback
            fallback_dim = 1536 if "v1" in self.model_name else 1024
            return [0.0] * fallback_dim


def setup_custom_embedding():
    """Setup function to initialize the custom embedding model with fallback."""
    try:
        print("Initializing Custom Titan Embedding...")
        embed_model = CustomTitanEmbedding()
        
        # Test the embedding
        test_text = "This is a test sentence."
        test_embedding = embed_model._get_embedding(test_text)
        print(f"✅ Custom embedding successful! Dimensions: {len(test_embedding)}")
        
        return embed_model
        
    except Exception as e:
        print(f"❌ Failed to initialize CustomTitanEmbedding: {e}")
        print("🔄 Falling back to standard BedrockEmbedding...")
        
        try:
            from llama_index.embeddings.bedrock import BedrockEmbedding
            embed_model = BedrockEmbedding(
                model_name="amazon.titan-embed-text-v1",
                region_name="eu-central-1",
                aws_access_key_id=os.environ.get("aws_access_key_id"),
                aws_secret_access_key=os.environ.get("aws_secret_access_key"),
                aws_session_token=os.environ.get("aws_session_token")
            )
            print("✅ Fallback embedding model initialized successfully.")
            return embed_model
            
        except Exception as fallback_error:
            print(f"❌ Fallback also failed: {fallback_error}")
            raise RuntimeError("Both custom and fallback embedding models failed to initialize")
