#!/usr/bin/env python3
"""
Test script to verify the GenAI CSV Enhancer setup
"""

import sys
import importlib
import pandas as pd

def test_imports():
    """Test if all required packages can be imported"""
    required_packages = [
        'streamlit',
        'pandas', 
        'boto3',
        'plotly',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    return missing_packages

def test_aws_config():
    """Test AWS configuration"""
    try:
        import boto3
        # Try to create a Bedrock client
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        print("✅ AWS Bedrock client created successfully")
        return True
    except Exception as e:
        print(f"❌ AWS configuration issue: {e}")
        return False

def test_sample_data():
    """Test loading sample data"""
    try:
        df = pd.read_csv('sample_data.csv')
        print(f"✅ Sample data loaded: {len(df)} rows, {len(df.columns)} columns")
        return True
    except Exception as e:
        print(f"❌ Sample data loading failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing GenAI CSV Enhancer Setup")
    print("=" * 40)
    
    # Test imports
    print("\n📦 Testing Package Imports:")
    missing_packages = test_imports()
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    # Test AWS configuration
    print("\n🔧 Testing AWS Configuration:")
    aws_ok = test_aws_config()
    
    # Test sample data
    print("\n📊 Testing Sample Data:")
    data_ok = test_sample_data()
    
    # Final result
    print("\n" + "=" * 40)
    if aws_ok and data_ok:
        print("🎉 All tests passed! Your setup is ready.")
        print("\n🚀 To start the application, run:")
        print("   streamlit run main.py")
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        if not aws_ok:
            print("\n🔧 AWS Setup Help:")
            print("   1. Configure AWS credentials: aws configure")
            print("   2. Ensure Bedrock access in your region")
            print("   3. Request Claude 3 Sonnet model access")
    
    return aws_ok and data_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
