import html
import os
import time
import random
import urllib.parse
import requests
from bs4 import BeautifulSoup

# Try to import cloudscraper as fallback (used when ScraperAPI is not configured)
try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False

baseURL = "https://www.1377x.to" 
defUserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"  

# ScraperAPI configuration (recommended for Cloudflare bypass)
# Get your API key from https://www.scraperapi.com/
SCRAPERAPI_KEY = os.getenv('SCRAPERAPI_KEY')
SCRAPERAPI_GEO = os.getenv('SCRAPERAPI_GEO')  # Optional: country code (e.g., 'us', 'uk')
SCRAPERAPI_RENDER = os.getenv('SCRAPERAPI_RENDER', 'false').lower() == 'true'  # Enable JS rendering

# Request configuration
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '60'))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))

# Get proxy from environment variable if set (used when ScraperAPI is not configured)
# Format: http://user:pass@host:port or http://host:port
PROXY = os.getenv('HTTP_PROXY') or os.getenv('HTTPS_PROXY') or os.getenv('PROXY')

# Transport mode logging
if SCRAPERAPI_KEY:
    print(f"ScraperAPI transport enabled (geo={SCRAPERAPI_GEO or 'auto'}, render={SCRAPERAPI_RENDER})")
elif CLOUDSCRAPER_AVAILABLE:
    print("Using cloudscraper transport (ScraperAPI not configured)")
else:
    print("Using basic requests transport (ScraperAPI not configured, cloudscraper not installed)")

# Global session - will be initialized on first use
_session = None
_session_initialized = False

def build_scraperapi_url(target_url):
    """Build ScraperAPI URL with configured options"""
    params = {
        'api_key': SCRAPERAPI_KEY,
        'url': target_url,
    }
    if SCRAPERAPI_GEO:
        params['country_code'] = SCRAPERAPI_GEO
    if SCRAPERAPI_RENDER:
        params['render'] = 'true'
    return f"http://api.scraperapi.com?{urllib.parse.urlencode(params)}"

def get_session():
    """Get or create a session for making requests.
    
    Priority:
    1. ScraperAPI (if SCRAPERAPI_KEY is set) - handles Cloudflare automatically
    2. cloudscraper (if available) - attempts to bypass Cloudflare locally
    3. Basic requests session (fallback)
    """
    global _session, _session_initialized
    
    if _session is None:
        # For ScraperAPI, use a simple requests session (ScraperAPI handles everything)
        if SCRAPERAPI_KEY:
            _session = requests.Session()
            _session.headers.update(get_headers(defUserAgent))
        # Use cloudscraper if available and no ScraperAPI
        elif CLOUDSCRAPER_AVAILABLE:
            _session = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'desktop': True
                }
            )
            # Don't override cloudscraper's headers - it handles them automatically
        else:
            _session = requests.Session()
            # Set default headers for requests fallback
            _session.headers.update(get_headers(defUserAgent))
        
        # Configure proxy if available (not needed for ScraperAPI - it proxies for you)
        if PROXY and not SCRAPERAPI_KEY:
            _session.proxies = {
                'http': PROXY,
                'https': PROXY
            }
    
    # Initialize session by visiting homepage to get cookies (skip for ScraperAPI)
    if not _session_initialized:
        if SCRAPERAPI_KEY:
            # ScraperAPI handles sessions/cookies, just mark as initialized
            _session_initialized = True
            print("ScraperAPI session ready")
        else:
            try:
                print("Initializing session by visiting homepage...")
                # Don't pass custom headers to cloudscraper - let it handle them
                if CLOUDSCRAPER_AVAILABLE:
                    r = _session.get(baseURL, timeout=REQUEST_TIMEOUT)
                else:
                    r = _session.get(baseURL, headers=get_headers(defUserAgent), timeout=REQUEST_TIMEOUT)
                r.raise_for_status()
                _session_initialized = True
                print("Session initialized successfully")
                # Small delay after initialization
                time.sleep(random.uniform(0.5, 1.0))
            except Exception as e:
                print(f"Warning: Failed to initialize session: {e}")
                # Continue anyway - might still work
    
    return _session

def get_headers(userAgent=defUserAgent, referer=None):
    """Generate realistic browser headers to avoid detection"""
    headers = {
        'User-Agent': userAgent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none' if referer is None else 'same-origin',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    if referer:
        headers['Referer'] = referer
    return headers

def fetch(query,pgno,userAgent=defUserAgent):
    data_list = []
    if query== None:
        return {"Message":"Empty Request"}
    if pgno ==None:
        pgno =1
    url = f"https://www.1377x.to/category-search/{query}/Music/{pgno}/"
    # Use baseURL as referer for the search page
    soup = getSoup(url, userAgent, referer=baseURL)
    # Store the search URL to use as referer for detail pages
    scrapeData(soup,userAgent,data_list,search_url=url)

    if len(data_list) == 0:
        return {"Message":"No data found"}

    return data_list

def getSoup(url, userAgent, referer=None, retries=None):
    """Fetch page with anti-detection measures and retry logic.
    
    Uses ScraperAPI if configured, otherwise falls back to cloudscraper or requests.
    """
    if retries is None:
        retries = MAX_RETRIES
    
    session = get_session()
    
    # Add random delay to mimic human behavior (shorter for ScraperAPI since it handles rate limiting)
    if SCRAPERAPI_KEY:
        time.sleep(random.uniform(0.3, 0.8))
    else:
        time.sleep(random.uniform(1, 3))
    
    for attempt in range(retries):
        try:
            # ScraperAPI transport - route through their proxy with Cloudflare bypass
            if SCRAPERAPI_KEY:
                api_url = build_scraperapi_url(url)
                headers = get_headers(userAgent, referer)
                r = session.get(api_url, headers=headers, timeout=REQUEST_TIMEOUT)
            # cloudscraper transport
            elif CLOUDSCRAPER_AVAILABLE:
                if referer:
                    r = session.get(url, headers={'Referer': referer}, timeout=REQUEST_TIMEOUT)
                else:
                    r = session.get(url, timeout=REQUEST_TIMEOUT)
            # Basic requests fallback
            else:
                headers = get_headers(userAgent, referer)
                r = session.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            return soup
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response is not None else None
            # Retry on transient errors (403, 429, 5xx)
            if status_code in (403, 429) or (status_code and status_code >= 500):
                if attempt < retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    print(f"HTTP {status_code} fetching {url} (attempt {attempt + 1}/{retries}). Retrying in {wait_time:.2f}s...")
                    time.sleep(wait_time)
                else:
                    print(f"HTTP {status_code} fetching {url} after {retries} attempts")
                    raise
            else:
                raise
        except Exception as e:
            if attempt < retries - 1:
                # Exponential backoff with jitter
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Error fetching {url} (attempt {attempt + 1}/{retries}): {e}. Retrying in {wait_time:.2f}s...")
                time.sleep(wait_time)
            else:
                print(f"Error fetching {url} after {retries} attempts: {e}")
                raise

def scrapeData(soup,userAgent,data_list,search_url=None):
    table = soup.find('table', class_='table-list table table-responsive table-striped')

    if table is None or len(table) == 0:
        print("No table found")
        return data_list
    
    # Use provided search_url or default to baseURL
    if search_url is None:
        search_url = baseURL
    
    for row in table.find_all('tr')[1:]:
        columns = row.find_all('td')
        name = columns[0].text.strip()
        link = columns[0].find_all('a')[1]
        href = link.get('href')
        se =  columns[1].text.strip()
        le = columns[2].text.strip()
        date = columns[3].text.strip()
        size = columns[4].text.strip()
        complete_url = baseURL+href
        # Use the search page as referer for detail pages
        magnet,lst1,lst2,imgSrc = scrapeMagnet(complete_url,userAgent,referer=search_url)
        try:
            data = {"name": name,"Images":imgSrc,"Seeders": se,"Leechers": le,"Date": date,"Size":size,"otherDetails":{"category":lst1[0].text,"type":lst1[1].text,"language":lst1[2].text,"uploader":lst1[4].text,"downloads":lst2[0].text,"dateUploaded":lst2[2].text},"magnet": magnet}
        except Exception as e:
            print(e)
            data = {"error":"Failed to scrape data for "+name}
        print(data)
        data_list.append(data)
        # Add delay between requests to avoid rate limiting
        time.sleep(random.uniform(0.5, 1.5))
    
def scrapeMagnet(complete_url,userAgent,referer=None): 
    soup = getSoup(complete_url,userAgent,referer=referer)
    try:
        magnet_tag = soup.find(
            lambda tag: tag.name == "a"
            and "Magnet Download" in tag.get_text(strip=True)
        )
        if magnet_tag and magnet_tag.has_attr("href"):
            magnet = html.unescape(magnet_tag.get("href"))
        else:
            magnet = "Na"
    except:
        magnet = "Na"  
    imgSrc = []
    try:
        for i in  soup.find_all("img", class_="img-responsive"):
          imgSrc.append(i.get("src"))
    except:
        imgSrc = "Na"
    try:      
        lst = soup.find_all("ul", class_="list")
        lst1 = lst[1].find_all("span")
        lst2 = lst[2].find_all("span")
    except:
        lst,lst1,lst2 = None,None,None     
    return magnet,lst1,lst2,imgSrc   
