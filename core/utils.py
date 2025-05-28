"""
Utility functions for the RAG application
"""
import os
import streamlit as st
from typing import List, Dict, Any, Optional
import logging

# Add llama_index import for document loading
try:
    from llama_index.core import Document, SimpleDirectoryReader
    LLAMA_INDEX_AVAILABLE = True
except ImportError:
    LLAMA_INDEX_AVAILABLE = False


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def check_file_exists(file_path: str) -> bool:
    """Check if a file exists"""
    return os.path.isfile(file_path)


def check_directory_exists(dir_path: str) -> bool:
    """Check if a directory exists"""
    return os.path.isdir(dir_path)


def create_directory_if_not_exists(dir_path: str) -> bool:
    """Create directory if it doesn't exist"""
    try:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            return True
        return True
    except Exception as e:
        print(f"Error creating directory {dir_path}: {e}")
        return False


def get_file_list(directory: str, extensions: Optional[List[str]] = None) -> List[str]:
    """Get list of files in directory with optional extension filtering"""
    if not check_directory_exists(directory):
        return []
    
    files = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            if extensions is None:
                files.append(filename)
            else:
                if any(filename.lower().endswith(ext.lower()) for ext in extensions):
                    files.append(filename)
    
    return sorted(files)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def get_directory_stats(directory: str) -> Dict[str, Any]:
    """Get statistics about a directory"""
    if not check_directory_exists(directory):
        return {
            "exists": False,
            "file_count": 0,
            "total_size": 0,
            "file_types": {}
        }
    
    file_count = 0
    total_size = 0
    file_types = {}
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            file_count += 1
            file_size = os.path.getsize(file_path)
            total_size += file_size
            
            # Track file extensions
            _, ext = os.path.splitext(filename)
            ext = ext.lower()
            if ext:
                file_types[ext] = file_types.get(ext, 0) + 1
            else:
                file_types["no_extension"] = file_types.get("no_extension", 0) + 1
    
    return {
        "exists": True,
        "file_count": file_count,
        "total_size": total_size,
        "total_size_formatted": format_file_size(total_size),
        "file_types": file_types
    }


def display_directory_info(directory: str):
    """Display information about a directory in Streamlit"""
    stats = get_directory_stats(directory)
    
    if not stats["exists"]:
        st.warning(f"📁 Directory '{directory}' does not exist")
        return
    
    st.info(f"""
    📁 **Directory Information:**
    - Path: `{directory}`
    - Files: {stats['file_count']}
    - Total Size: {stats['total_size_formatted']}
    """)
    
    if stats["file_types"]:
        st.write("**File Types:**")
        for ext, count in stats["file_types"].items():
            if ext == "no_extension":
                st.write(f"  - Files without extension: {count}")
            else:
                st.write(f"  - {ext}: {count}")


def create_sample_document(directory: str, filename: str = "sample_document.txt") -> str:
    """Create a sample document for testing"""
    content = """This is a sample document for the ExconAI RAG system.

The system demonstrates the following capabilities:
- Document ingestion and processing
- Vector embeddings using AWS Bedrock Titan
- Question answering using Claude models
- Retrieval-Augmented Generation (RAG)

Key Features:
1. Support for multiple document formats
2. Semantic search and similarity matching
3. Context-aware response generation
4. Source citation and transparency

AWS Bedrock Integration:
- Provides access to foundation models
- Scalable and secure AI services
- Support for various model providers
- Enterprise-grade security and compliance

For more information about Authorised Dealers and BOP codes, 
please refer to the official documentation and regulatory guidelines.
"""
    
    file_path = os.path.join(directory, filename)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path
    except Exception as e:
        print(f"Error creating sample document: {e}")
        return None


def validate_environment() -> Dict[str, bool]:
    """Validate the environment setup"""
    checks = {
        "dotenv_available": False,
        "boto3_available": False,
        "llama_index_available": False,
        "aws_credentials": False
    }
    
    try:
        from dotenv import load_dotenv
        checks["dotenv_available"] = True
    except ImportError:
        pass
    
    try:
        import boto3
        checks["boto3_available"] = True
    except ImportError:
        pass
    
    try:
        from llama_index.core import VectorStoreIndex
        checks["llama_index_available"] = True
    except ImportError:
        pass
    
    # Check AWS credentials
    aws_vars = ["aws_access_key_id", "aws_secret_access_key", "aws_session_token"]
    checks["aws_credentials"] = all(os.getenv(var) for var in aws_vars)
    
    return checks


def display_environment_status():
    """Display environment validation status in Streamlit"""
    st.subheader("🔍 Environment Status")
    
    checks = validate_environment()
    
    for check_name, status in checks.items():
        status_icon = "✅" if status else "❌"
        check_display = check_name.replace("_", " ").title()
        st.write(f"{status_icon} {check_display}")
    
    if not all(checks.values()):
        st.warning("⚠️ Some environment checks failed. Please ensure all dependencies are installed and AWS credentials are configured.")
    else:
        st.success("🎉 Environment is properly configured!")


def truncate_text(text: str, max_length: int = 150) -> str:
    """Truncate text to specified length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def highlight_search_terms(text: str, search_terms: List[str]) -> str:
    """Highlight search terms in text (simple implementation)"""
    highlighted_text = text
    for term in search_terms:
        if term.lower() in text.lower():
            # Simple highlighting - in a real app, you might use more sophisticated highlighting
            highlighted_text = highlighted_text.replace(
                term, f"**{term}**"
            )
    return highlighted_text


def load_documents_from_directory(data_dir: str) -> List[Any]:
    """
    Load PDF documents from the specified directory using SimpleDirectoryReader.
    Only processes PDF files to avoid dependency issues with other file formats.
    
    Args:
        data_dir (str): Path to the directory containing documents
        
    Returns:
        List[Document]: List of loaded PDF documents
        
    Raises:
        FileNotFoundError: If the directory doesn't exist
        ImportError: If llama_index is not available
        Exception: If there's an error loading documents
    """
    if not LLAMA_INDEX_AVAILABLE:
        raise ImportError("llama_index is not available. Please install it with: pip install llama-index")
    
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Directory not found: {data_dir}")
    
    logger = setup_logging()
    
    try:
        # Only load PDF files to avoid PowerPoint and other format dependencies
        documents = SimpleDirectoryReader(
            input_dir=data_dir,
            required_exts=[".pdf"]  # Only process PDF files
        ).load_data()
        logger.info(f"Successfully loaded {len(documents)} PDF documents from {data_dir}")
        return documents
    except Exception as e:
        logger.error(f"Error loading PDF documents from {data_dir}: {e}")
        raise
