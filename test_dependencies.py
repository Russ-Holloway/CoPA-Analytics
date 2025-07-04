#!/usr/bin/env python3
"""
Test script to verify Azure Cosmos DB dependencies are working
"""

import sys
import importlib.util

def test_import(module_name):
    """Test if a module can be imported"""
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            print(f"❌ {module_name} - Module not found")
            return False
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"✅ {module_name} - Successfully imported")
        return True
    except Exception as e:
        print(f"❌ {module_name} - Error: {str(e)}")
        return False

def main():
    """Test all required dependencies"""
    print("Testing Python dependencies for Azure Functions...")
    print(f"Python version: {sys.version}")
    print("-" * 50)
    
    modules_to_test = [
        'azure.functions',
        'azure.cosmos',
        'requests',
        'datetime',
        'json',
        'os',
        'logging'
    ]
    
    success_count = 0
    for module in modules_to_test:
        if test_import(module):
            success_count += 1
    
    print("-" * 50)
    print(f"Results: {success_count}/{len(modules_to_test)} modules imported successfully")
    
    if success_count == len(modules_to_test):
        print("🎉 All dependencies are working!")
        return 0
    else:
        print("⚠️  Some dependencies are missing. Check your requirements.txt and installation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
