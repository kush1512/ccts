#!/usr/bin/env python
"""
Simple Test Script - Verify Backend is Working
Run this to test all endpoints quickly
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_connection():
    """Test if backend is reachable"""
    print("\n🔌 Testing connection to backend...")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=2)
        print("✓ Backend is running!")
        return True
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to backend!")
        print("  Make sure to run: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return False

def test_create_project():
    """Test creating a project"""
    print("\n📝 Testing project creation...")
    try:
        response = requests.post(
            f"{BASE_URL}/projects/",
            json={"name": "Test Project"},
            timeout=5
        )
        
        if response.status_code == 200:
            project = response.json()
            project_id = project['id']
            print(f"✓ Project created successfully!")
            print(f"  ID: {project_id}")
            print(f"  Name: {project['name']}")
            print(f"  Status: {project['status']}")
            return project_id
        else:
            print(f"✗ Failed to create project (Status: {response.status_code})")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def test_get_project(project_id):
    """Test retrieving project"""
    print(f"\n📋 Testing project retrieval (ID: {project_id})...")
    try:
        response = requests.get(
            f"{BASE_URL}/projects/{project_id}",
            timeout=5
        )
        
        if response.status_code == 200:
            project = response.json()
            print("✓ Project retrieved successfully!")
            print(f"  Name: {project['name']}")
            print(f"  Status: {project['status']}")
            return True
        else:
            print(f"✗ Failed to retrieve project (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_upload_empty():
    """Test uploading with no files (should fail gracefully)"""
    print(f"\n📤 Testing upload endpoint...")
    try:
        project_id = 1
        response = requests.post(
            f"{BASE_URL}/projects/{project_id}/upload-images/",
            timeout=5
        )
        
        # Should return error for no files, but endpoint exists
        if response.status_code in [200, 422]:
            print("✓ Upload endpoint is accessible!")
            return True
        else:
            print(f"⚠ Unexpected response: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_api_docs():
    """Test API documentation endpoint"""
    print("\n📚 Testing API documentation...")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        
        if response.status_code == 200:
            print("✓ API documentation is available!")
            print(f"  Access it at: {BASE_URL}/docs")
            return True
        else:
            print(f"✗ Documentation not available (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print(" " * 15 + "BACKEND TEST SUITE")
    print("=" * 60)
    
    tests_passed = 0
    tests_total = 5
    
    # Test 1: Connection
    if test_connection():
        tests_passed += 1
    else:
        print("\n⚠️  Stopping tests - backend is not running")
        return
    
    # Test 2: Create Project
    project_id = test_create_project()
    if project_id:
        tests_passed += 1
    
    # Test 3: Get Project
    if project_id and test_get_project(project_id):
        tests_passed += 1
    
    # Test 4: Upload Endpoint
    if test_upload_empty():
        tests_passed += 1
    
    # Test 5: API Docs
    if test_api_docs():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"TESTS PASSED: {tests_passed}/{tests_total}")
    print("=" * 60)
    
    if tests_passed == tests_total:
        print("\n✓ All tests passed! Backend is working correctly.")
        print("\nNext steps:")
        print("1. Add your drone images to: ./data/sample_images/")
        print("2. Run: python workflow.py")
        print("3. Check results in: ./data/{project_id}/carbon_inventory.csv")
    else:
        print(f"\n⚠️  {tests_total - tests_passed} test(s) failed. Check errors above.")

if __name__ == "__main__":
    run_all_tests()
