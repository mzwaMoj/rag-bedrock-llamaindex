"""
Streamlit RAG Chatbot Application
A conversational interface for the RAG system
"""
import streamlit as st
import sys
import os
from typing import Dict, Any

# Add the parent directory to the path to import core modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from core.rag_system import RAGSystem
    from core.claude_model import ClaudeModel
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please ensure you're running from the correct directory and all dependencies are installed.")
    st.stop()


class StreamlitChatbot:
    """Streamlit chatbot interface for RAG system"""
    
    def __init__(self):
        # Initialize session state variables if they don't exist
        if 'rag_system' not in st.session_state:
            st.session_state.rag_system = None
        if 'claude_model' not in st.session_state:
            st.session_state.claude_model = None
        if 'rag_initialized' not in st.session_state:
            st.session_state.rag_initialized = False
    
    @property
    def rag_system(self):
        """Access RAG system from session state"""
        return st.session_state.rag_system
    
    @property
    def claude_model(self):
        """Access Claude model from session state"""
        return st.session_state.claude_model
        
    def initialize_app(self):
        """Initialize the Streamlit app"""
        st.set_page_config(
            page_title="ExconAI RAG Chatbot",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS for better styling
        st.markdown("""
        <style>
        .main {
            padding-top: 1rem;
        }
        .stChatMessage {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        .chat-header {
            text-align: center;
            color: #2E86C1;
            margin-bottom: 2rem;
        }
        .source-box {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-top: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Header
        st.markdown("<h1 class='chat-header'>🤖 AI RAG Chatbot</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #5D6D7E;'>Ask questions about your documents using AWS Bedrock AI</p>", unsafe_allow_html=True)
    
    def sidebar_config(self):
        """Configure the sidebar"""
        with st.sidebar:
            st.header("⚙️ Configuration")
            
            # Data directory selection
            data_dir = st.text_input(
                "Data Directory", 
                value="./data",
                help="Path to your documents directory"
            )
            
            # AWS Region
            aws_region = st.selectbox(
                "AWS Region",
                ["eu-central-1", "us-east-1", "us-west-2", "eu-west-1"],
                index=0
            )
            
            # Top-k similarity
            top_k = st.slider(
                "Number of Similar Documents",
                min_value=1,
                max_value=10,
                value=3,
                help="Number of similar documents to retrieve for context"
            )
            
            # Initialize system button
            if st.button("🚀 Initialize RAG System", type="primary"):
                with st.spinner("Initializing RAG system..."):
                    success = self.initialize_rag_system(data_dir, aws_region)
                    if success:
                        st.success("✅ RAG System initialized successfully!")
                        st.session_state.rag_initialized = True
                        st.session_state.top_k = top_k
                        st.rerun()  # Force rerun to update the UI
                    else:
                        st.error("❌ Failed to initialize RAG system. Check your configuration.")
                        st.session_state.rag_initialized = False
            
            # System status
            st.subheader("📊 System Status")
            if st.session_state.rag_initialized:
                st.success("🟢 RAG System: Active")
                if st.session_state.rag_system and hasattr(st.session_state.rag_system, 'documents') and st.session_state.rag_system.documents:
                    st.info(f"📄 Documents loaded: {len(st.session_state.rag_system.documents)}")
            else:
                st.warning("🟡 RAG System: Not initialized")
            
            # Additional settings
            st.subheader("🎛️ Chat Settings")
            use_direct_claude = st.checkbox(
                "Use Direct Claude (without RAG)",
                help="Query Claude directly without document context"
            )
            
            st.session_state.use_direct_claude = use_direct_claude
            
            return data_dir, aws_region, top_k
    
    def initialize_rag_system(self, data_dir: str, aws_region: str) -> bool:
        """Initialize the RAG system"""
        try:
            # Store in session state instead of instance variables
            st.session_state.rag_system = RAGSystem(data_directory=data_dir, aws_region=aws_region)
            success = st.session_state.rag_system.initialize_system()
            
            # Also initialize Claude model for direct queries
            if success:
                try:
                    st.session_state.claude_model = ClaudeModel()
                except Exception as e:
                    st.warning(f"Claude model initialization failed: {e}")
                    
            return success
            
        except Exception as e:
            st.error(f"Error initializing RAG system: {e}")
            return False
    
    def display_chat_interface(self, top_k: int):
        """Display the main chat interface"""
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Display sources if available
                if "sources" in message and message["sources"]:
                    self.display_sources(message["sources"])
        
        # Chat input
        if prompt := st.chat_input("Ask a question about your documents..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate response
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                sources_placeholder = st.empty()
                
                with st.spinner("Thinking..."):
                    response_data = self.get_response(prompt, top_k)
                
                # Display response
                if response_data["error"]:
                    response_text = f"❌ Error: {response_data['error']}"
                    sources = []
                else:
                    response_text = response_data["response"]
                    sources = response_data.get("sources", [])
                
                response_placeholder.markdown(response_text)
                
                # Display sources
                if sources:
                    with sources_placeholder.container():
                        self.display_sources(sources)
                  # Add assistant response to chat history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response_text,
                    "sources": sources
                })
    
    def get_response(self, query: str, top_k: int) -> Dict[str, Any]:
        """Get response from the appropriate model"""
        if hasattr(st.session_state, 'use_direct_claude') and st.session_state.use_direct_claude:
            # Use direct Claude model
            if st.session_state.claude_model:
                try:
                    result = st.session_state.claude_model.generate_response(query)
                    return {
                        "error": None,
                        "response": result["text"],
                        "sources": [],
                        "query": query,
                        "num_sources": 0
                    }
                except Exception as e:
                    return {
                        "error": f"Claude model error: {str(e)}",
                        "response": None,
                        "sources": [],
                        "query": query
                    }
            else:
                return {
                    "error": "Claude model not initialized",
                    "response": None,
                    "sources": [],
                    "query": query
                }
        else:
            # Use RAG system
            if st.session_state.rag_system and st.session_state.rag_initialized:
                try:
                    return st.session_state.rag_system.query_documents(query, top_k)
                except Exception as e:
                    return {
                        "error": f"RAG query error: {str(e)}",
                        "response": None,
                        "sources": [],
                        "query": query
                    }
            else:
                return {
                    "error": "RAG system not initialized. Please initialize it first using the sidebar.",
                    "response": None,
                    "sources": [],
                    "query": query
                }
    
    def display_sources(self, sources):
        """Display source documents"""
        if not sources:
            return
            
        with st.expander(f"📚 Sources ({len(sources)} documents)", expanded=False):
            for i, source in enumerate(sources, 1):
                st.markdown(f"**Source {i}** (Score: {source['score']})")
                st.markdown(f"```\n{source['text_preview']}\n```")
                st.markdown("---")
    
    def display_examples(self):
        """Display example queries"""
        st.subheader("💡 Example Questions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **General Questions:**
            - What is AWS Bedrock?
            - Explain the main concepts in the documents
            - Summarize the key points
            """)
        
        with col2:
            st.markdown("""
            **Specific Queries:**
            - What are Authorised Dealers?
            - List the BOP codes mentioned
            - Show payment instruction formats
            """)
    
    def run(self):
        """Run the Streamlit application"""
        self.initialize_app()
        
        # Sidebar configuration
        data_dir, aws_region, top_k = self.sidebar_config()
        
        # Main content area
        if not st.session_state.rag_initialized:
            # Welcome screen
            st.info("👋 Welcome! Please initialize the RAG system using the sidebar to get started.")
            self.display_examples()
        else:
            # Chat interface
            self.display_chat_interface(top_k)
            # Clear chat button
            if st.button("🗑️ Clear Chat History"):
                st.session_state.messages = []
                st.rerun()


def main():
    """Main function to run the app"""
    chatbot = StreamlitChatbot()
    chatbot.run()


if __name__ == "__main__":
    main()
