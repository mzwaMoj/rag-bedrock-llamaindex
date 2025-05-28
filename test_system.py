"""
Test script to verify the RAG system components work correctly
"""
import sys
import os

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all core modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from core.config import Config, AppTexts
        print("✅ Config module imported successfully")
    except ImportError as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from core.utils import setup_logging, validate_environment
        print("✅ Utils module imported successfully")
    except ImportError as e:
        print(f"❌ Utils import failed: {e}")
        return False
    
    try:
        from core.embeddings import CustomTitanEmbedding, setup_custom_embedding
        print("✅ Embeddings module imported successfully")
    except ImportError as e:
        print(f"❌ Embeddings import failed: {e}")
        return False
    
    try:
        from core.claude_model import ClaudeModel
        print("✅ Claude model module imported successfully")
    except ImportError as e:
        print(f"❌ Claude model import failed: {e}")
        return False
    
    try:
        from core.rag_system import RAGSystem
        print("✅ RAG system module imported successfully")
    except ImportError as e:
        print(f"❌ RAG system import failed: {e}")
        return False
    
    return True

def test_environment():
    """Test environment setup"""
    print("\n🔍 Testing environment...")
    
    from core.utils import validate_environment
    checks = validate_environment()
    
    for check_name, status in checks.items():
        status_icon = "✅" if status else "❌"
        check_display = check_name.replace("_", " ").title()
        print(f"{status_icon} {check_display}")
    
    return all(checks.values())

def test_config():
    """Test configuration"""
    print("\n⚙️ Testing configuration...")
    
    from core.config import Config
    
    # Test credential validation
    creds_valid = Config.validate_credentials()
    print(f"{'✅' if creds_valid else '❌'} AWS credentials validation")
    
    # Test model config
    try:
        claude_config = Config.get_model_config("claude")
        print(f"✅ Claude model config: {claude_config['model_id']}")
    except Exception as e:
        print(f"❌ Claude model config failed: {e}")
        return False
    
    return True

def test_data_directory():
    """Test data directory"""
    print("\n📁 Testing data directory...")
    
    from core.utils import get_directory_stats
    
    data_dir = "./data"
    stats = get_directory_stats(data_dir)
    
    if stats["exists"]:
        print(f"✅ Data directory exists: {data_dir}")
        print(f"📄 Files found: {stats['file_count']}")
        print(f"💾 Total size: {stats['total_size_formatted']}")
        if stats["file_types"]:
            print("📋 File types:")
            for ext, count in stats["file_types"].items():
                print(f"   - {ext}: {count}")
        return stats["file_count"] > 0
    else:
        print(f"❌ Data directory does not exist: {data_dir}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting RAG System Tests")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Environment", test_environment),
        ("Configuration", test_config),
        ("Data Directory", test_data_directory)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Your RAG system is ready to use.")
        print("\n🚀 To start the chatbot, run:")
        print("   python run_chatbot.py")
    else:
        print("⚠️  Some tests failed. Please check the configuration and try again.")
        if not Config.validate_credentials():
            print("\n💡 Tip: Make sure to create a .env file with your AWS credentials")
            print("   Copy .env.template to .env and fill in your credentials")

if __name__ == "__main__":
    main()
