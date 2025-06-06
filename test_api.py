import requests
import json

def test_api_endpoints(base_url):
    """Test various API endpoints to diagnose 400 errors"""
    
    print(f"Testing API at: {base_url}")
    print("=" * 50)
    
    # Test endpoints
    endpoints = [
        ('Root', ''),
        ('Health Check', 'api/health/'),
        ('Swagger', 'swagger/'),
        ('API Root', 'api/'),
        ('Books (no auth)', 'api/books/'),
        ('Admin', 'admin/'),
    ]
    
    for name, endpoint in endpoints:
        url = f"{base_url.rstrip('/')}/{endpoint}"
        try:
            print(f"\n{name}: {url}")
            response = requests.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCESS")
                # Try to show JSON response if it's JSON
                try:
                    data = response.json()
                    print(f"Response: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"Response length: {len(response.text)} chars")
            elif response.status_code == 400:
                print("❌ BAD REQUEST (400)")
                print(f"Response: {response.text[:300]}...")
            elif response.status_code == 401:
                print("🔒 UNAUTHORIZED (401) - Authentication required")
            elif response.status_code == 403:
                print("🚫 FORBIDDEN (403) - Permission denied")
            elif response.status_code == 404:
                print("❓ NOT FOUND (404)")
            else:
                print(f"⚠️  Status {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ CONNECTION ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("TESTING COMPLETE")
    print("\nIf you're getting 400 errors:")
    print("1. Check if you're sending correct HTTP methods (GET, POST, etc.)")
    print("2. For POST requests, ensure you're sending proper JSON data")
    print("3. Check if authentication is required (use /api/accounts/users/login/)")
    print("4. Check CORS settings if accessing from a browser")

if __name__ == "__main__":
    # Replace with your Railway URL
    BASE_URL = input("Enter your Railway URL (e.g., https://your-app.up.railway.app): ").strip()
    if not BASE_URL:
        BASE_URL = "http://localhost:8000"  # Default for local testing
    
    test_api_endpoints(BASE_URL)
