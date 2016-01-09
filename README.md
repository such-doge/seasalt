## seasalt
Seasonal Anime List Thing - Retrieves and parses MyAnimeList season data to generate an XML database of new anime for Taiga. MyAnimeList<->Hummingbird relations are scraped from LiveChart.me

### Prerequisites
Python 3, pycurl, BeautifulSoup4, lxml.

### Instructions
1. Set the name of the season, output file name, and user agent at the top of the script before you use it.
2. Run the command `python seasalt.py`
3. Place the resulting XML file in `Taiga\data\db\season\`

### Warnings
1. This script skips SSL verification for the sake of simplicity.
2. Do not repeatedly use this script to spam LiveChart.me. Once is enough.
