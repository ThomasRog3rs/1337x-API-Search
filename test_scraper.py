#!/usr/bin/env python3
"""
Standalone CLI scraper test for 1337x
Just calls the service and outputs the raw response - no parsing
"""

import requests
import urllib.parse

# HARDCODED CONFIGURATION
SCRAPERAPI_KEY = ""  # Replace with your actual key
TARGET_URL = "https://1337x.to/"
USE_PREMIUM = False  # Change to False to test without premium
USE_ULTRA_PREMIUM = False  # Change to True if premium doesn't work
REQUEST_TIMEOUT = 6000

def build_scraperapi_url(target_url):
    """Build ScraperAPI URL with configured options."""
    params = {
        'api_key': SCRAPERAPI_KEY,
        'url': target_url,
    }
    if USE_ULTRA_PREMIUM:
        params['ultra_premium'] = 'true'
    elif USE_PREMIUM:
        params['premium'] = 'true'
    
    return f"http://api.scraperapi.com?{urllib.parse.urlencode(params)}"

def test_site():
    """Just call the service and output raw response."""
    print("=== 1337x Scraper Test ===")
    print(f"Target URL: {TARGET_URL}")
    print(f"Premium: {USE_PREMIUM}")
    print(f"Ultra Premium: {USE_ULTRA_PREMIUM}")
    print(f"Request Timeout: {REQUEST_TIMEOUT}s")
    print()
    
    try:
        api_url = build_scraperapi_url(TARGET_URL)
        print(f"ScraperAPI URL: {api_url.replace(SCRAPERAPI_KEY, '***')}")
        print()
        
        print("Making request...")
        response = requests.get(api_url, timeout=REQUEST_TIMEOUT)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Length: {len(response.text)} characters")
        print()
        
        print("=== RAW RESPONSE ===")
        print(response.text)
        print("=== END RESPONSE ===")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ REQUEST FAILED: {e}")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_search(query="test", page=1):
    """Test actual search URL."""
    print(f"\n=== SEARCH TEST: {query} ===")
    search_url = f"https://1337x.to/search/{query}/{page}/"
    
    try:
        api_url = build_scraperapi_url(search_url)
        print(f"Search URL: {search_url}")
        print(f"ScraperAPI URL: {api_url.replace(SCRAPERAPI_KEY, '***')}")
        
        response = requests.get(api_url, timeout=REQUEST_TIMEOUT)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Length: {len(response.text)} characters")
        print()
        
        print("=== RAW SEARCH RESPONSE ===")
        print(response.text)
        print("=== END RESPONSE ===")
        
    except Exception as e:
        print(f"❌ SEARCH TEST ERROR: {e}")

if __name__ == "__main__":
    test_site()
    print("\n" + "="*50 + "\n")
    test_search()