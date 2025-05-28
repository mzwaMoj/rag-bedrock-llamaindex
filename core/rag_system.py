"""
RAG System Core Module
Main RAG system implementation extracted from notebook
"""
import logging
import sys
import os
from typing import List, Dict, Optional, Any

# LlamaIndex imports
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.bedrock import BedrockEmbedding
from llama_index.llms.bedrock import Bedrock
from llama_index.core.node_parser import SentenceSplitter
from dotenv import load_dotenv, find_dotenv

from .embeddings import setup_custom_embedding


class RAGSystem:
    """Main RAG System class for document indexing and querying"""
    
    def __init__(self, data_directory: str = "../data", aws_region: str = "eu-central-1"):
        """
        Initialize the RAG system
        
        Args:
            data_directory (str): Path to the directory containing documents
            aws_region (str): AWS region for Bedrock services
        """
        self.data_directory = data_directory
        self.aws_region = aws_region
        self.documents = []
        self.index = None
        self.query_engine = None
        
        # Setup logging
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
        logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
        
        # Load environment variables
        load_dotenv(find_dotenv())
        
        # Initialize models
        self._setup_models()
        
    def _setup_models(self):
        """Setup LLM and embedding models"""
        try:
            # Initialize Bedrock LLM (Claude 3.5 Sonnet)
            self.llm = Bedrock(
                model="anthropic.claude-3-5-sonnet-20240620-v1:0",
                region_name=self.aws_region,
            )
            
            # Initialize embedding model
            self.embed_model = setup_custom_embedding()
            
            # Set global settings for LlamaIndex
            Settings.llm = self.llm
            Settings.embed_model = self.embed_model
            Settings.chunk_size = 512
            Settings.chunk_overlap = 20
            
            print("✅ Models initialized successfully")
            
        except Exception as e:
            print(f"❌ Error setting up models: {e}")
            raise
    
    def load_documents(self) -> bool:
        """
        Load documents from the data directory
        
        Returns:
            bool: True if documents loaded successfully, False otherwise
        """
        try:
            # Check if directory exists and create sample if it doesn't
            if not os.path.exists(self.data_directory):
                os.makedirs(self.data_directory)
                print(f"Created directory: {self.data_directory}")
                  # Add a dummy file for testing
                sample_file = os.path.join(self.data_directory, "sample_document.txt")
                with open(sample_file, "w") as f:
                    f.write("This is a sample document for the LlamaIndex RAG system. ")
                    f.write("It contains information about AI and machine learning. ")
                    f.write("AWS Bedrock provides access to powerful foundation models.")
                print(f"Created sample_document.txt in {self.data_directory}")
              # Load only PDF documents to avoid PowerPoint dependency issues
            self.documents = SimpleDirectoryReader(
                input_dir=self.data_directory,
                required_exts=[".pdf"],  # Only process PDF files
                recursive=False  # Don't read subdirectories
            ).load_data()
            
            if not self.documents:
                print(f"No PDF documents found in {self.data_directory}. Please add PDF files to the directory.")
                print("The system is configured to only process PDF files to avoid dependency issues.")
                return False
            else:
                print(f"✅ Loaded {len(self.documents)} PDF document(s).")
                return True
                
        except Exception as e:
            print(f"❌ Error loading documents: {e}")
            self.documents = []
            return False
    
    def create_index(self) -> bool:
        """
        Create vector index from loaded documents
        
        Returns:
            bool: True if index created successfully, False otherwise
        """
        if not self.documents:
            print("❌ No documents loaded. Please load documents first.")
            return False
        
        try:
            self.index = VectorStoreIndex.from_documents(self.documents)
            print("✅ Index created successfully.")
            return True
            
        except Exception as e:
            print(f"❌ Error creating index: {e}")
            print("This might be due to model access permissions. Please check your AWS Bedrock model access.")
            self.index = None
            return False
    
    def create_query_engine(self, similarity_top_k: int = 3) -> bool:
        """
        Create query engine from the index
        
        Args:
            similarity_top_k (int): Number of top similar documents to retrieve
            
        Returns:
            bool: True if query engine created successfully, False otherwise
        """
        if not self.index:
            print("❌ No index available. Please create index first.")
            return False
        
        try:
            self.query_engine = self.index.as_query_engine(
                similarity_top_k=similarity_top_k
            )
            print("✅ Query engine created successfully.")
            return True
            
        except Exception as e:
            print(f"❌ Error creating query engine: {e}")
            self.query_engine = None
            return False
    
    def query_documents(self, user_input: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Query the indexed documents with user input
        
        Args:
            user_input (str): The question or query from the user
            top_k (int): Number of top similar documents to retrieve
            
        Returns:
            dict: Dictionary containing response text, source information, and metadata
        """
        if not self.query_engine:
            return {
                "error": "Query engine is not available. Please ensure documents are loaded and indexed.",
                "response": None,
                "sources": []
            }
        
        try:
            # Query the engine
            response = self.query_engine.query(user_input)
            
            # Extract source information
            sources = []
            for node in response.source_nodes:
                sources.append({
                    "node_id": node.node_id,
                    "score": round(node.score, 4),
                    "text_preview": node.text[:150] + "..." if len(node.text) > 150 else node.text,
                    "full_text": node.text
                })
            
            return {
                "error": None,
                "response": str(response),
                "sources": sources,
                "query": user_input,
                "num_sources": len(sources)
            }
            
        except Exception as e:
            return {
                "error": f"Error processing query: {str(e)}",
                "response": None,
                "sources": [],
                "query": user_input
            }
    
    def initialize_system(self) -> bool:
        """
        Initialize the complete RAG system
        
        Returns:
            bool: True if system initialized successfully, False otherwise
        """
        print("🚀 Initializing RAG System...")
        
        # Load documents
        if not self.load_documents():
            return False
        
        # Create index
        if not self.create_index():
            return False
        
        # Create query engine
        if not self.create_query_engine():
            return False
        
        print("✅ RAG System initialized successfully!")
        return True
