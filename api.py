import html
import os
import time
import random
try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    import requests
    CLOUDSCRAPER_AVAILABLE = False
    print("Warning: cloudscraper not installed. Install it with: pip install cloudscraper")
from bs4 import BeautifulSoup

baseURL = "https://www.1377x.to" 
defUserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"  

# Get proxy from environment variable if set
# Format: http://user:pass@host:port or http://host:port
PROXY = os.getenv('HTTP_PROXY') or os.getenv('HTTPS_PROXY') or os.getenv('PROXY')

# Global session - will be initialized on first use
_session = None
_session_initialized = False

def get_session():
    """Get or create a session using cloudscraper to bypass Cloudflare"""
    global _session, _session_initialized
    
    if _session is None:
        # Use cloudscraper if available, otherwise fall back to requests
        if CLOUDSCRAPER_AVAILABLE:
            _session = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'desktop': True
                }
            )
            # Don't override cloudscraper's headers - it handles them automatically
        else:
            import requests
            _session = requests.Session()
            # Set default headers for requests fallback
            _session.headers.update(get_headers(defUserAgent))
        
        # Configure proxy if available
        if PROXY:
            _session.proxies = {
                'http': PROXY,
                'https': PROXY
            }
    
    # Initialize session by visiting homepage to get cookies
    if not _session_initialized:
        try:
            print("Initializing session by visiting homepage...")
            # Don't pass custom headers to cloudscraper - let it handle them
            if CLOUDSCRAPER_AVAILABLE:
                r = _session.get(baseURL, timeout=60)
            else:
                r = _session.get(baseURL, headers=get_headers(defUserAgent), timeout=60)
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

def getSoup(url,userAgent,referer=None,retries=3):
    """Fetch page with anti-detection measures and retry logic"""
    session = get_session()
    
    # Add random delay to mimic human behavior
    time.sleep(random.uniform(1, 3))
    
    for attempt in range(retries):
        try:
            # For cloudscraper, don't override headers - let it handle Cloudflare automatically
            # Only set referer if provided
            if CLOUDSCRAPER_AVAILABLE:
                if referer:
                    r = session.get(url, headers={'Referer': referer}, timeout=60)
                else:
                    r = session.get(url, timeout=60)
            else:
                # For requests fallback, use full headers
                headers = get_headers(userAgent, referer)
                r = session.get(url, headers=headers, timeout=60)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            return soup
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
