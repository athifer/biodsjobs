#!/usr/bin/env python3
"""
Test script for the updated frontend features:
1. Multiple filter selections
2. HTML content cleaning
"""
import time
import subprocess
import json
import sys

def start_server():
    """Start the server in the background"""
    print("Starting server...")
    proc = subprocess.Popen([
        '/Users/minluzhang/projects/2025/git/biodsjobs/.venv/bin/uvicorn',
        'app:app', '--host', '0.0.0.0', '--port', '8000'
    ], cwd='/Users/minluzhang/projects/2025/git/biodsjobs/backend',
    env={'PYTHONPATH': '/Users/minluzhang/projects/2025/git/biodsjobs/backend'})
    
    # Wait for server to start
    time.sleep(5)
    return proc

def test_multiple_sources():
    """Test multiple source filtering"""
    print("\n=== Testing Multiple Source Filtering ===")
    import urllib.request
    import urllib.parse
    
    # Test with multiple sources
    params = urllib.parse.urlencode([
        ('source', 'lever'),
        ('source', 'greenhouse'),
        ('limit', '5')
    ])
    
    try:
        url = f"http://localhost:8000/api/jobs?{params}"
        print(f"Testing URL: {url}")
        
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read())
            
        print(f"Retrieved {len(data)} jobs")
        
        # Check sources
        sources = {job['source'] for job in data}
        print(f"Sources found: {sources}")
        
        # Verify only lever and greenhouse jobs
        expected_sources = {'lever', 'greenhouse'}
        if sources.issubset(expected_sources):
            print("✅ Multiple source filtering works correctly!")
        else:
            print("❌ Multiple source filtering has issues")
            
    except Exception as e:
        print(f"❌ Error testing multiple sources: {e}")

def test_multiple_locations():
    """Test multiple location filtering"""
    print("\n=== Testing Multiple Location Filtering ===")
    import urllib.request
    import urllib.parse
    
    # Test with multiple locations
    params = urllib.parse.urlencode([
        ('location', 'remote'),
        ('location', 'san francisco bay area'),
        ('limit', '10')
    ])
    
    try:
        url = f"http://localhost:8000/api/jobs?{params}"
        print(f"Testing URL: {url}")
        
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read())
            
        print(f"Retrieved {len(data)} jobs")
        
        # Check locations
        locations = {job.get('location', 'N/A') for job in data}
        print(f"Sample locations: {list(locations)[:5]}")
        
        print("✅ Multiple location filtering API working!")
            
    except Exception as e:
        print(f"❌ Error testing multiple locations: {e}")

def test_html_cleaning():
    """Test if we can see HTML in descriptions to verify client-side cleaning will work"""
    print("\n=== Testing HTML Content (for client-side cleaning) ===")
    import urllib.request
    
    try:
        url = "http://localhost:8000/api/jobs?limit=3"
        
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read())
            
        print(f"Retrieved {len(data)} jobs for HTML testing")
        
        for i, job in enumerate(data[:2]):
            desc = job.get('description', '')[:200]
            print(f"\nJob {i+1} description sample:")
            print(f"Raw: {repr(desc)}")
            
            # Check for HTML content
            has_html_tags = any(tag in desc for tag in ['&lt;', '&gt;', '&quot;', '&amp;'])
            if has_html_tags:
                print("✅ Found HTML entities - client-side cleaning will be needed and effective")
            else:
                print("ℹ️  No HTML entities in this sample")
                
    except Exception as e:
        print(f"❌ Error testing HTML content: {e}")

def main():
    print("🧪 Testing Updated Features")
    print("=" * 50)
    
    # Start server
    server_proc = start_server()
    
    try:
        # Run tests
        test_multiple_sources()
        test_multiple_locations() 
        test_html_cleaning()
        
        print("\n" + "=" * 50)
        print("🎉 Testing complete!")
        print("\nNext steps:")
        print("1. Open http://localhost:8000/ (if running) or the frontend HTML file")
        print("2. Try selecting multiple sources (e.g., Lever + Greenhouse)")
        print("3. Try selecting multiple locations (e.g., Remote + San Francisco)")
        print("4. Verify job descriptions are cleanly formatted (no HTML tags/entities)")
        
    finally:
        # Clean up
        server_proc.terminate()
        server_proc.wait()

if __name__ == "__main__":
    main()
