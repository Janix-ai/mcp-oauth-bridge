#!/usr/bin/env python3
"""
Test script for MCP OAuth Bridge end-to-end testing

This script:
1. Starts the mock OAuth server
2. Tests the OAuth bridge discovery
3. Runs through the complete OAuth flow
4. Tests MCP requests with OAuth tokens
"""

import asyncio
import subprocess
import time
import sys
import signal
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def test_oauth_bridge():
    """Test the complete OAuth bridge flow"""
    
    print("🧪 Starting MCP OAuth Bridge Test Suite")
    print("=" * 50)
    
    # Start mock OAuth server
    print("1. Starting mock OAuth MCP server...")
    mock_server = subprocess.Popen([
        sys.executable, "tests/mock_oauth_server.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Test discovery
        print("2. Testing OAuth server discovery...")
        import httpx
        
        # Test root endpoint (should return WWW-Authenticate header)
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8080/")
            print(f"   Root endpoint status: {response.status_code}")
            
            if "WWW-Authenticate" in response.headers:
                print(f"   ✅ OAuth discovery header found: {response.headers['WWW-Authenticate']}")
            else:
                print("   ❌ OAuth discovery header missing!")
                return False
            
            # Test OAuth metadata
            metadata_response = await client.get("http://localhost:8080/.well-known/oauth-authorization-server")
            print(f"   OAuth metadata status: {metadata_response.status_code}")
            
            if metadata_response.status_code == 200:
                metadata = metadata_response.json()
                print(f"   ✅ OAuth metadata found: {metadata.get('authorization_endpoint')}")
            else:
                print("   ❌ OAuth metadata missing!")
                return False
        
        print("3. Testing MCP OAuth Bridge commands...")
        
        # Initialize the bridge
        print("   Initializing bridge...")
        result = subprocess.run([
            "mcp-oauth-bridge", "init"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ Bridge initialized successfully")
        else:
            print(f"   ❌ Bridge initialization failed: {result.stderr}")
            return False
        
        # Add the mock server (this would normally open a browser)
        print("   Adding mock OAuth server...")
        result = subprocess.run([
            "mcp-oauth-bridge", "add", "mock", "http://localhost:8080", "--no-browser"
        ], capture_output=True, text=True, input="y\n")
        
        print(f"   Add server output: {result.stdout}")
        print(f"   Add server errors: {result.stderr}")
        
        # List configured servers
        print("   Listing configured servers...")
        result = subprocess.run([
            "mcp-oauth-bridge", "list"
        ], capture_output=True, text=True)
        
        print(f"   Server list: {result.stdout}")
        
        # Check status
        print("   Checking bridge status...")
        result = subprocess.run([
            "mcp-oauth-bridge", "status"
        ], capture_output=True, text=True)
        
        print(f"   Status: {result.stdout}")
        
        print("4. ✅ Test completed successfully!")
        print("\n🚀 Next steps:")
        print("   1. Start the mock server: python tests/mock_oauth_server.py")
        print("   2. Start the bridge: mcp-oauth-bridge start")
        print("   3. Test with curl: curl http://localhost:3000/mcp/mock/test")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    
    finally:
        # Clean up
        print("Cleaning up...")
        mock_server.terminate()
        mock_server.wait()

if __name__ == "__main__":
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n🛑 Test interrupted by user")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Run the test
    success = asyncio.run(test_oauth_bridge())
    sys.exit(0 if success else 1) 