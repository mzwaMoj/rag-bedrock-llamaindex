# ExconAI RAG Chatbot

A Streamlit-based conversational interface for document querying using AWS Bedrock and LlamaIndex.

## 🚀 Features

- **Document-based Q&A**: Ask questions about your documents using advanced RAG (Retrieval-Augmented Generation)
- **AWS Bedrock Integration**: Powered by Claude 3 and Titan embedding models
- **Interactive Web Interface**: User-friendly Streamlit chatbot interface
- **Source Attribution**: See which documents contributed to each answer
- **Modular Architecture**: Clean, maintainable code structure
- **Direct Claude Mode**: Option to query Claude directly without document context
- **PDF-Only Processing**: Optimized for PDF files to avoid dependency issues

## 📄 Supported File Formats

**✅ Supported:**
- PDF (.pdf) - Primary format, fully optimized

**❌ Not Supported (by design):**
- PowerPoint (.pptx, .ppt) - Removed to avoid dependency issues
- Word (.docx, .doc) - Removed to avoid dependency issues
- Other formats - System focused on PDF processing only

## 📁 Project Structure

```
rag/
├── core/                      # Core RAG system modules
│   ├── __init__.py
│   ├── claude_model.py        # Claude model wrapper
│   ├── config.py              # Configuration settings
│   ├── embeddings.py          # Custom Titan embedding implementation
│   ├── rag_system.py          # Main RAG system class
│   └── utils.py               # Utility functions
├── frontend/                  # Streamlit application
│   └── streamlit_app.py       # Main Streamlit chatbot interface
├── data/                      # Document storage directory
├── notebooks/                 # Jupyter notebooks (development)
│   └── rag_system.ipynb       # Original development notebook
├── requirements.txt           # Python dependencies
├── run_chatbot.py            # Application launcher
└── README.md                 # This file
```

## 🛠️ Setup and Installation

### Prerequisites

1. **Python 3.8+**
2. **AWS Account** with Bedrock access
3. **AWS Credentials** configured
4. **Model Access** enabled in AWS Bedrock console for:
   - Claude 3 Sonnet (`anthropic.claude-3-sonnet-20240229-v1:0`)
   - Claude 3.5 Sonnet (`anthropic.claude-3-5-sonnet-20240620-v1:0`)
   - Titan Embeddings (`amazon.titan-embed-text-v1`)

### Environment Setup

1. **Clone or navigate to the project directory**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create `.env` file in the project root:**
   ```env
   aws_access_key_id=your_access_key_here
   aws_secret_access_key=your_secret_key_here
   aws_session_token=your_session_token_here
   ```

4. **Add your documents:**
   - Place PDF documents in the `data/` directory
   - ⚠️ **Note**: The system is configured to process PDF files only to avoid dependency issues
   - The system will automatically process these files

### AWS Bedrock Model Access

Ensure you have enabled model access in the AWS Bedrock console:

1. Go to AWS Bedrock console
2. Navigate to "Model access"
3. Enable access for:
   - Anthropic Claude models
   - Amazon Titan Embeddings

## 🚀 Running the Application

### Option 1: Using the Launcher Script
```bash
python run_chatbot.py
```

### Option 2: Direct Streamlit Command
```bash
streamlit run frontend/streamlit_app.py
```

The application will open in your default web browser at `http://localhost:8501`

## 💬 How to Use

1. **Initialize the System:**
   - Use the sidebar to configure your data directory and AWS region
   - Click "🚀 Initialize RAG System" to load and index your documents

2. **Ask Questions:**
   - Type your questions in the chat input
   - The system will search your documents and provide contextual answers
   - View source documents that contributed to each answer

3. **Configuration Options:**
   - **Data Directory**: Path to your documents
   - **AWS Region**: Choose your preferred Bedrock region
   - **Similarity Count**: Number of similar documents to retrieve
   - **Direct Claude Mode**: Query Claude without document context

## 📊 Example Queries

### General Questions
- "What is AWS Bedrock?"
- "Explain the main concepts in the documents"
- "Summarize the key points"

### Domain-Specific (based on your documents)
- "What are Authorised Dealers?"
- "List the BOP codes mentioned"
- "Show payment instruction formats"

## 🔧 Configuration

### Core Settings (config.py)
- Default data directory
- AWS regions
- Model configurations
- Chunk sizes for document processing

### Runtime Settings (Streamlit sidebar)
- Data directory path
- AWS region selection
- Number of similar documents to retrieve
- Direct Claude mode toggle

## 🏗️ Architecture

### Core Components

1. **RAGSystem** (`core/rag_system.py`):
   - Main orchestrator for document loading, indexing, and querying
   - Integrates LlamaIndex components

2. **ClaudeModel** (`core/claude_model.py`):
   - Direct interface to AWS Bedrock Claude models
   - Handles authentication and response parsing

3. **CustomTitanEmbedding** (`core/embeddings.py`):
   - Custom implementation of Titan embeddings
   - Handles both sync and async operations

4. **StreamlitChatbot** (`frontend/streamlit_app.py`):
   - Web interface and user interaction logic
   - Chat history management and response display

### Data Flow

1. **Document Loading**: SimpleDirectoryReader loads documents from data directory
2. **Embedding**: Documents are converted to vectors using Titan embeddings
3. **Indexing**: Vector index is created for similarity search
4. **Query Processing**: User queries are embedded and matched against document vectors
5. **Response Generation**: Claude generates responses using relevant document context

## 🛡️ Security Considerations

- AWS credentials are loaded from environment variables
- Session tokens are supported for temporary credentials
- All communication with AWS services uses secure HTTPS
- No sensitive data is logged or exposed in the interface

## 🐛 Troubleshooting

### Common Issues

1. **"Model access not enabled"**
   - Enable model access in AWS Bedrock console
   - Check your AWS region has Bedrock support

2. **"AWS credentials missing"**
   - Verify `.env` file exists with correct credentials
   - Ensure credentials have Bedrock permissions

3. **"No documents found"**
   - Check the data directory path
   - Ensure documents are in supported formats (txt, pdf, etc.)

4. **"Embedding generation failed"**
   - Verify Titan embedding model access
   - Check AWS region configuration

### Debug Mode

To enable detailed logging, modify the logging level in `core/utils.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance Tips

- **Document Size**: Smaller, focused documents work better than large files
- **Chunk Size**: Adjust in config.py based on your document types
- **Region Selection**: Choose a region close to your location for better performance
- **Similarity Count**: Start with 3-5 similar documents, adjust based on results

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review AWS Bedrock documentation
3. Check LlamaIndex documentation
4. Create an issue in the project repository

## 🔄 Updates and Maintenance

- Regularly update dependencies for security patches
- Monitor AWS Bedrock model availability and updates
- Test with new document types as needed
- Keep AWS credentials rotated according to security policies
