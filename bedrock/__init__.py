"""
AWS Bedrock integration for LLM functionality.
Handles model initialization, configuration, and response generation.
Supports mock mode for frontend/CLI testing without AWS access.
"""

import boto3
from langchain_aws import ChatBedrock
from botocore.exceptions import ClientError, NoCredentialsError
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockLLM:
    """Mock LLM for testing UI without AWS Bedrock."""
    def invoke(self, prompt):
        return f"[MOCK RESPONSE] You asked: '{prompt}'. This is a simulated answer."

class BedrockLLM:
    """AWS Bedrock LLM wrapper for cluster information queries. Supports mock mode."""
    
    # Available models with their configurations
    AVAILABLE_MODELS = {
        "claude-3-sonnet": {
            "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
            "max_tokens": 4096,
            "temperature": 0.1
        },
        "claude-3-haiku": {
            "model_id": "anthropic.claude-3-haiku-20240307-v1:0",
            "max_tokens": 4096,
            "temperature": 0.1
        },
        "titan-text": {
            "model_id": "amazon.titan-text-express-v1",
            "max_tokens": 4096,
            "temperature": 0.1
        }
    }
    
    def __init__(self, model_name: str = "claude-3-haiku", region: str = None, mock_mode: bool = None):
        """
        Initialize Bedrock LLM (or mock LLM if mock_mode is enabled).
        
        Args:
            model_name: Name of the model to use (from AVAILABLE_MODELS)
            region: AWS region for Bedrock service
            mock_mode: If True, use mock LLM for testing (set via env BEDROCK_MOCK_MODE)
        """
        self.model_name = model_name
        self.region = region or os.getenv("AWS_REGION", "us-west-2")
        self.mock_mode = mock_mode if mock_mode is not None else os.getenv("BEDROCK_MOCK_MODE", "false").lower() == "true"
        
        if model_name not in self.AVAILABLE_MODELS:
            raise ValueError(f"Model {model_name} not supported. Available: {list(self.AVAILABLE_MODELS.keys())}")
        
        self.model_config = self.AVAILABLE_MODELS[model_name]
        self.llm = None
        
        if self.mock_mode:
            self._initialize_mock_llm()
        else:
            self._initialize_bedrock()
    
    def _initialize_mock_llm(self):
        """Initialize the mock LLM for UI/CLI testing."""
        self.llm = MockLLM()
        logger.info("Initialized MOCK LLM for frontend/CLI testing.")
    
    def _initialize_bedrock(self):
        """Initialize the Bedrock client and LLM."""
        try:
            # Test AWS credentials
            session = boto3.Session()
            credentials = session.get_credentials()
            
            if not credentials:
                raise NoCredentialsError()
            
            # Initialize Bedrock client
            self.bedrock_client = boto3.client(
                service_name='bedrock-runtime',
                region_name=self.region
            )
            # Instead of list_foundation_models, do a simple model invocation for connection test
            # This will be handled in test_connection()
            
            # Initialize LangChain ChatBedrock
            self.llm = ChatBedrock(
                client=self.bedrock_client,
                model_id=self.model_config["model_id"],
                model_kwargs={
                    "max_tokens": self.model_config["max_tokens"],
                    "temperature": self.model_config["temperature"]
                }
            )
            
            logger.info(f"Initialized Bedrock LLM with model: {self.model_name} in region: {self.region}")
            
        except NoCredentialsError:
            logger.error("AWS credentials not found. Please configure using 'aws configure' or environment variables.")
            raise
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'UnauthorizedOperation':
                logger.error("Insufficient permissions for Bedrock. Please check IAM policies.")
            elif error_code == 'AccessDenied':
                logger.error("Access denied to Bedrock service. Please check your permissions.")
            else:
                logger.error(f"AWS Client Error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error initializing Bedrock: {e}")
            raise
    
    def get_llm(self):
        """Get the initialized LLM instance (mock or real)."""
        if not self.llm:
            raise RuntimeError("LLM not initialized. Call _initialize_bedrock() or _initialize_mock_llm() first.")
        return self.llm
    
    def test_connection(self) -> bool:
        """
        Test the Bedrock connection (always True in mock mode).
        
        Returns:
            True if connection is successful, False otherwise
        """
        if self.mock_mode:
            logger.info("Mock mode enabled: test_connection always returns True.")
            return True
        
        try:
            # Test with a simple prompt
            test_prompt = "Hello"
            response = self.llm.invoke(test_prompt)
            logger.info("Bedrock connection test successful")
            return True
        except Exception as e:
            logger.error(f"Bedrock connection test failed: {e}")
            return False
    
    @classmethod
    def list_available_models(cls) -> dict:
        """List all available models and their configurations."""
        return cls.AVAILABLE_MODELS
    
    def get_model_info(self) -> dict:
        """Get information about the current model."""
        return {
            "model_name": self.model_name,
            "model_id": self.model_config["model_id"],
            "region": self.region,
            "max_tokens": self.model_config["max_tokens"],
            "temperature": self.model_config["temperature"]
        }


def create_bedrock_llm(model_name: str = None, region: str = None, mock_mode: bool = None) -> BedrockLLM:
    """
    Factory function to create a BedrockLLM instance (supports mock mode).
    
    Args:
        model_name: Model to use (defaults to environment variable or claude-3-haiku)
        region: AWS region (defaults to environment variable or us-west-2)
        mock_mode: If True, use mock LLM for testing (set via env BEDROCK_MOCK_MODE)
    
    Returns:
        Initialized BedrockLLM instance
    """
    model_name = model_name or os.getenv("BEDROCK_MODEL_NAME", "claude-3-haiku")
    region = region or os.getenv("AWS_REGION", "us-west-2")
    if mock_mode is None:
        mock_mode = os.getenv("BEDROCK_MOCK_MODE", "false").lower() == "true"
    return BedrockLLM(model_name=model_name, region=region, mock_mode=mock_mode)
