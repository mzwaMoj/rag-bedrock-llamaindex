"""
Simple launcher script for the RAG Streamlit chatbot
"""
import subprocess
import sys
import os


def main():
    """Launch the Streamlit application"""
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(current_dir, "frontend", "streamlit_app.py")
    
    # Check if the app file exists
    if not os.path.exists(app_path):
        print(f"❌ Error: Application file not found at {app_path}")
        return
    
    print("🚀 Starting ExconAI RAG Chatbot...")
    print(f"📁 App location: {app_path}")
    print("🌐 The app will open in your default web browser")
    print("⏹️  Press Ctrl+C to stop the application")
    print("-" * 50)
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", app_path,
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error launching application: {e}")


if __name__ == "__main__":
    main()
