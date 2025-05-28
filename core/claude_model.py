"""
Claude LLM Model Module
Extracted from the notebook for modular use
"""
import boto3
import json
import os
import warnings
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv, find_dotenv

warnings.filterwarnings('ignore')


class ClaudeModel:
    """Claude 3 Sonnet model wrapper for AWS Bedrock"""
    
    def __init__(self):
        dotenv_path = find_dotenv()
        if not dotenv_path:
            raise FileNotFoundError("Could not find .env file")
        load_dotenv(dotenv_path)
        
        self.aws_access_key_id = os.getenv("aws_access_key_id")
        self.aws_secret_access_key = os.getenv("aws_secret_access_key")
        self.aws_session_token = os.getenv("aws_session_token")
        
        if not all([self.aws_access_key_id, self.aws_secret_access_key, self.aws_session_token]):
            raise ValueError("One or more AWS credentials are missing in the .env file")

        try:
            self.brt = boto3.client(
                service_name='bedrock-runtime',
                region_name='eu-central-1',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                aws_session_token=self.aws_session_token
            )
        except (BotoCoreError, ClientError) as error:
            raise ConnectionError(f"Failed to create boto3 client: {error}")

        self.modelId = "anthropic.claude-3-sonnet-20240229-v1:0"
        self.accept = 'application/json'
        self.contentType = 'application/json'

    def generate_response(self, prompt_text, temperature=0.1, ai_role="You are a helpful assistant."):
        """Generate response using Claude model"""
        body = json.dumps({
            "messages": [
                {"role": "assistant", "content": ai_role},
                {"role": "user", "content": [{'type': 'text', "text": prompt_text}]}
            ],
            "max_tokens": 5000,
            "temperature": temperature,
            "top_p": 0.9,
            "anthropic_version": "bedrock-2023-05-31"
        })

        try:
            response = self.brt.invoke_model(
                body=body, 
                modelId=self.modelId, 
                accept=self.accept, 
                contentType=self.contentType
            )
            response_body = json.loads(response.get('body').read())
        except (BotoCoreError, ClientError) as error:
            raise RuntimeError(f"Failed to invoke model: {error}")
        except json.JSONDecodeError as error:
            raise ValueError(f"Failed to parse response body: {error}")

        try:
            text = response_body['content'][0]['text']
            usage = response_body['usage']
            prompt_tokens = usage['input_tokens']
            response_tokens = usage['output_tokens']
            total_tokens = prompt_tokens + response_tokens
        except KeyError as error:
            raise KeyError(f"Missing expected key in response body: {error}")

        return {
            'text': text,
            'prompt_tokens': prompt_tokens,
            'response_tokens': response_tokens,
            'total_tokens': total_tokens
        }
