# 1337x-API

## Introduction

1337x-API is a simple API that allows you to access information about torrents from 1337x using web scraping via ScraperAPI proxy. This API provides easy access to torrent data, including details such as the torrent name, images, seeders, leechers, date uploaded, size, category, type, language, uploader, and more.

## Disclaimer

This project is intended for educational purposes only. The developer of this project is not responsible for any piracy or illegal activities that may result from the use of this API. Please use this tool responsibly and in compliance with all relevant laws and regulations.

## Requirements

This API requires a [ScraperAPI](https://www.scraperapi.com/) account. ScraperAPI handles Cloudflare challenges and provides automatic proxy rotation for reliable scraping.

## Setup

### 1. Get a ScraperAPI Key

Create an account at [ScraperAPI](https://www.scraperapi.com/) and get your API key.

### 2. Set Environment Variable

```bash
export SCRAPERAPI_KEY=your_api_key_here
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Server

```bash
python app.py
```

Or with Gunicorn:

```bash
gunicorn --bind 0.0.0.0:8000 app:app
```

## Docker

### Build and Run

```bash
# Build the Docker image
docker build -t 1337x-api .

# Run with ScraperAPI key
docker run -e SCRAPERAPI_KEY=your_key -p 8000:8000 1337x-api
```

### With All Options

```bash
docker run \
  -e SCRAPERAPI_KEY=your_key \
  -e SCRAPERAPI_GEO=us \
  -e REQUEST_TIMEOUT=90 \
  -p 8000:8000 \
  1337x-api
```

## Configuration

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SCRAPERAPI_KEY` | Your ScraperAPI key | Yes | - |
| `SCRAPERAPI_GEO` | Country code for geo-targeting (e.g., `us`, `uk`) | No | Auto |
| `SCRAPERAPI_RENDER` | Enable JavaScript rendering (`true`/`false`) | No | `false` |
| `REQUEST_TIMEOUT` | Request timeout in seconds | No | `60` |
| `MAX_RETRIES` | Maximum retry attempts | No | `3` |

## Usage

You can use this API in the following ways:

1. **Access torrent by filename and page number (default page 1):**
```bash
127.0.0.1:5000/<filename>/<pageno>
```

2. **Access torrent by filename with default page number 1:**
```bash
127.0.0.1:5000/<filename>
```

3. **Access torrent by filename and page number using query parameters:**
```bash
127.0.0.1:5000?q=<filename>&page=<pageno>
```

## JSON Response

The API returns a JSON response with the following structure:

```json
[
  {
    "name": "",
    "Images": ["", ""],
    "Seeders": "",
    "Leechers": "",
    "Date": "",
    "Size": "",
    "otherDetails": {
      "category": "",
      "type": "",
      "language": "",
      "uploader": "",
      "downloads": "",
      "dateUploaded": ""
    },
    "magnet": ""
  }
]
```

## Example Response

```json
[
  {
    "name": "Zathura: A Space Adventure (2005) 720p BrRip x264 - YIFY",
    "Images": [
      "http://i5.minus.com/iUDOCknAFoU6E.png",
      "http://cdn.piczend.com/images/PwhUfggS/oy5ju8jq1i26g3sgbqismsmfw.jpeg"
    ],
    "Seeders": "58",
    "Leechers": "0",
    "Date": "Jun. 21st '13",
    "Size": "750.8 MB",
    "otherDetails": {
      "category": "Movies",
      "type": "HD",
      "language": "English",
      "uploader": "YIFY",
      "downloads": "3751",
      "dateUploaded": "Jun. 21st '13"
    },
    "magnet": "magnet:?xt=urn:btih:228502D093EF9A9E4E6EA7B2A9EEF419E1BECA92&dn=..."
  }
]
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `RuntimeError: SCRAPERAPI_KEY required` | Set the `SCRAPERAPI_KEY` environment variable |
| Still getting 403 errors | Try enabling `SCRAPERAPI_RENDER=true` for JavaScript rendering |
| Slow responses | ScraperAPI adds latency; this is expected |
| Empty results | Check if the search term exists on the site |
| Timeout errors | Increase `REQUEST_TIMEOUT` value |
