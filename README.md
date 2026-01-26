# 1337x-API

## Introduction

1337x-API is a simple API that allows you to access information about torrents from 1337x using web scraping. This API provides easy access to torrent data, including details such as the torrent name, images, seeders, leechers, date uploaded, size, category, type, language, uploader, and more. You can use this API by making HTTP requests to a local server running at `127.0.0.1:5000`, followed by specific routes to access torrent information.

## Disclaimer

This project is intended for educational purposes only. The developer of this project is not responsible for any piracy or illegal activities that may result from the use of this API. Please use this tool responsibly and in compliance with all relevant laws and regulations.

## Anti-Detection Features

This API includes several anti-detection measures to avoid 403 Forbidden errors:

- **ScraperAPI Integration**: Managed Cloudflare bypass with automatic proxy rotation (recommended)
- **Realistic Browser Headers**: Mimics real browser requests with proper Accept, Accept-Language, and other headers
- **Referer Headers**: Uses proper referer headers to simulate navigation flow
- **Request Delays**: Random delays between requests to mimic human behavior
- **Retry Logic**: Automatic retries with exponential backoff on 403/429/5xx errors
- **Proxy Support**: Optional proxy configuration via environment variables

## ScraperAPI Configuration (Recommended)

ScraperAPI handles Cloudflare challenges and provides automatic proxy rotation, making it the most reliable option for consistent scraping.

### Setup Steps

1. **Create an account** at [ScraperAPI](https://www.scraperapi.com/) and get your API key
2. **Set the environment variable**:
   ```bash
   export SCRAPERAPI_KEY=your_api_key_here
   ```

3. **For Docker**:
   ```bash
   docker run -e SCRAPERAPI_KEY=your_api_key_here -p 8000:8000 1337x-api
   ```

### Optional ScraperAPI Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `SCRAPERAPI_KEY` | Your ScraperAPI key (required for ScraperAPI) | - |
| `SCRAPERAPI_GEO` | Country code for geo-targeting (e.g., `us`, `uk`) | Auto |
| `SCRAPERAPI_RENDER` | Enable JavaScript rendering (`true`/`false`) | `false` |
| `REQUEST_TIMEOUT` | Request timeout in seconds | `60` |
| `MAX_RETRIES` | Maximum retry attempts | `3` |

### Example with All Options

```bash
docker run \
  -e SCRAPERAPI_KEY=your_key \
  -e SCRAPERAPI_GEO=us \
  -e REQUEST_TIMEOUT=90 \
  -p 8000:8000 \
  1337x-api
```

## Alternative: Direct Proxy Configuration

If you prefer to use your own proxy instead of ScraperAPI, you can configure it via environment variables. Note: this may not bypass Cloudflare challenges.

### Setting up a Proxy

1. **Using Environment Variables**:
   ```bash
   export HTTP_PROXY=http://proxy.example.com:8080
   export HTTPS_PROXY=http://proxy.example.com:8080
   # Or use a single PROXY variable
   export PROXY=http://proxy.example.com:8080
   ```

2. **For Docker**:
   ```bash
   docker run -e HTTP_PROXY=http://proxy.example.com:8080 -e HTTPS_PROXY=http://proxy.example.com:8080 -p 8000:8000 1337x-api
   ```

3. **Proxy with Authentication**:
   ```bash
   export HTTP_PROXY=http://username:password@proxy.example.com:8080
   ```

### Proxy Service Recommendations

- **Residential Proxies**: Bright Data, Smartproxy, Oxylabs (rotating residential IPs)
- **Datacenter Proxies**: ProxyMesh, ProxyRack (faster, cheaper, but more detectable)

**Note**: Always ensure you comply with the terms of service of both the proxy provider and the target website.

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
     "Images": [
         "",
         ""
     ],
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
 // More torrent entries...
]
```


## Example of a JSON Response
```json
[
 {
     "name": "Zathura: A Space Adventure (2005) 720p BrRip x264 - YIFY",
     "Images": [
         "http://i5.minus.com/iUDOCknAFoU6E.png",
         "http://cdn.piczend.com/images/PwhUfggS/oy5ju8jq1i26g3sgbqismsmfw.jpeg",
         "http://cdn.piczend.com/images/PwhUfggS/wmii4o43esut7fhm8nqeazapl.png",
         "http://cdn.piczend.com/images/PwhUfggS/harngaasjjnxdhbv1vt6sw55d.png",
         "http://cdn.piczend.com/images/PwhUfggS/952zle7bwkixbqgk43dbvzsgj.png"
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
     "magnet": "magnet:?xt=urn:btih:228502D093EF9A9E4E6EA7B2A9EEF419E1BECA92&dn=Zathura%3A+A+Space+Adventure+%282005%29+720p+BrRip+x264+-+YIFY&tr=udp%3A%2F%2Ftracker.yify-torrents.com%2Fannounce&tr=udp%3A%2F%2Ftwig.gs%3A6969&tr=udp%3A%2F%2Ftracker.publichd.eu%2Fannounce&tr=http%3A%2F%2Ftracker.publichd.eu%2Fannounce&tr=udp%3A%2F%2Ftracker.police.maori.nz%2Fannounce&tr=udp%3A%2F%2Ftracker.1337x.org%3A80%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969&tr=udp%3A%2F%2Ftracker.istole.it%3A80&tr=udp%3A%2F%2Ftracker.ccc.de%3A80%2Fannounce&tr=http%3A%2F%2Ftracker.yify-torrents.com%2Fannounce&tr=udp%3A%2F%2F9.rarbg.com%3A2710%2Fannounce&tr=http%3A%2F%2Ffr33dom.h33t.com%3A3310%2Fannounce&tr=udp%3A%2F%2Ftracker.zer0day.to%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969%2Fannounce&tr=udp%3A%2F%2Fcoppersurfer.tk%3A6969%2Fannounce"
 }
]
```

## Testing Checklist

Use this checklist to verify the scraper is working correctly:

### 1. Verify ScraperAPI Configuration
```bash
# Check that the API key is set
echo $SCRAPERAPI_KEY
```

### 2. Build and Run with ScraperAPI
```bash
# Build the Docker image
docker build -t 1337x-api .

# Run with ScraperAPI key
docker run -e SCRAPERAPI_KEY=your_key -p 8000:8000 1337x-api
```

### 3. Test a Search Request
```bash
# Make a test request (should return JSON with torrent data)
curl http://localhost:8000/test

# Check the Docker logs for:
# - "ScraperAPI transport enabled" on startup
# - "ScraperAPI session ready" on first request
# - No 403 errors
```

### 4. Verify Server IP is Hidden
- Your server's IP should not appear in requests to the target site
- All requests go through ScraperAPI's proxy network
- Check your ScraperAPI dashboard for request logs

### 5. Troubleshooting

| Issue | Solution |
|-------|----------|
| Still getting 403 | Verify API key is correct, try enabling `SCRAPERAPI_RENDER=true` |
| Slow responses | ScraperAPI adds latency; this is normal |
| Empty results | Check if the search term exists on the site |
| Timeout errors | Increase `REQUEST_TIMEOUT` value |
