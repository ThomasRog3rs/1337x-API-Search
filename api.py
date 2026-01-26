import html
import os
import time
import random
import urllib.parse
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.1377x.to"
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# ScraperAPI configuration (required)
# Get your API key from https://www.scraperapi.com/
SCRAPERAPI_KEY = os.getenv('SCRAPERAPI_KEY')
SCRAPERAPI_GEO = os.getenv('SCRAPERAPI_GEO')  # Optional: country code (e.g., 'us', 'uk')
SCRAPERAPI_RENDER = os.getenv('SCRAPERAPI_RENDER', 'false').lower() == 'true'

# Request configuration
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '60'))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))

# Validate API key on startup
if not SCRAPERAPI_KEY:
    raise RuntimeError(
        "SCRAPERAPI_KEY environment variable is required. "
        "Get your API key from https://www.scraperapi.com/"
    )

print(f"ScraperAPI transport enabled (geo={SCRAPERAPI_GEO or 'auto'}, render={SCRAPERAPI_RENDER})")

# Global session
_session = None


def build_scraperapi_url(target_url):
    """Build ScraperAPI URL with configured options."""
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
    """Get or create a requests session."""
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers.update(get_headers())
    return _session


def get_headers(user_agent=DEFAULT_USER_AGENT, referer=None):
    """Generate realistic browser headers."""
    headers = {
        'User-Agent': user_agent,
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


def get_soup(url, user_agent=DEFAULT_USER_AGENT, referer=None, retries=None):
    """Fetch page via ScraperAPI with retry logic."""
    if retries is None:
        retries = MAX_RETRIES

    session = get_session()

    # Small delay between requests (ScraperAPI handles rate limiting)
    time.sleep(random.uniform(0.3, 0.8))

    for attempt in range(retries):
        try:
            api_url = build_scraperapi_url(url)
            headers = get_headers(user_agent, referer)
            response = session.get(api_url, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')

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
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Error fetching {url} (attempt {attempt + 1}/{retries}): {e}. Retrying in {wait_time:.2f}s...")
                time.sleep(wait_time)
            else:
                print(f"Error fetching {url} after {retries} attempts: {e}")
                raise


def fetch(query, pgno, user_agent=DEFAULT_USER_AGENT):
    """Search for torrents and return results."""
    if query is None:
        return {"Message": "Empty Request"}
    if pgno is None:
        pgno = 1

    url = f"https://www.1377x.to/category-search/{query}/Music/{pgno}/"
    soup = get_soup(url, user_agent, referer=BASE_URL)

    data_list = []
    scrape_data(soup, user_agent, data_list, search_url=url)

    if len(data_list) == 0:
        return {"Message": "No data found"}

    return data_list


def scrape_data(soup, user_agent, data_list, search_url=None):
    """Parse search results table and fetch details for each torrent."""
    table = soup.find('table', class_='table-list table table-responsive table-striped')

    if table is None or len(table) == 0:
        print("No table found")
        return data_list

    if search_url is None:
        search_url = BASE_URL

    for row in table.find_all('tr')[1:]:
        columns = row.find_all('td')
        name = columns[0].text.strip()
        link = columns[0].find_all('a')[1]
        href = link.get('href')
        seeders = columns[1].text.strip()
        leechers = columns[2].text.strip()
        date = columns[3].text.strip()
        size = columns[4].text.strip()

        complete_url = BASE_URL + href
        magnet, info_list1, info_list2, images = scrape_magnet(complete_url, user_agent, referer=search_url)

        try:
            data = {
                "name": name,
                "Images": images,
                "Seeders": seeders,
                "Leechers": leechers,
                "Date": date,
                "Size": size,
                "otherDetails": {
                    "category": info_list1[0].text,
                    "type": info_list1[1].text,
                    "language": info_list1[2].text,
                    "uploader": info_list1[4].text,
                    "downloads": info_list2[0].text,
                    "dateUploaded": info_list2[2].text
                },
                "magnet": magnet
            }
        except Exception as e:
            print(e)
            data = {"error": "Failed to scrape data for " + name}

        print(data)
        data_list.append(data)

        # Delay between requests
        time.sleep(random.uniform(0.5, 1.5))


def scrape_magnet(url, user_agent, referer=None):
    """Fetch torrent detail page and extract magnet link and metadata."""
    soup = get_soup(url, user_agent, referer=referer)

    # Extract magnet link
    try:
        magnet_tag = soup.find(
            lambda tag: tag.name == "a" and "Magnet Download" in tag.get_text(strip=True)
        )
        if magnet_tag and magnet_tag.has_attr("href"):
            magnet = html.unescape(magnet_tag.get("href"))
        else:
            magnet = "Na"
    except:
        magnet = "Na"

    # Extract images
    images = []
    try:
        for img in soup.find_all("img", class_="img-responsive"):
            images.append(img.get("src"))
    except:
        images = "Na"

    # Extract torrent info lists
    try:
        lists = soup.find_all("ul", class_="list")
        info_list1 = lists[1].find_all("span")
        info_list2 = lists[2].find_all("span")
    except:
        info_list1, info_list2 = None, None

    return magnet, info_list1, info_list2, images
