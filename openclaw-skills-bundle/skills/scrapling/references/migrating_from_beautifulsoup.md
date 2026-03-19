# Migrating from BeautifulSoup to Scrapling

API comparison between BeautifulSoup and Scrapling. Scrapling is faster, provides equivalent parsing capabilities, and adds features for fetching and handling modern web pages.

Some BeautifulSoup shortcuts have no direct Scrapling equivalent. Scrapling avoids those shortcuts to preserve performance.

## Common mappings

- `from bs4 import BeautifulSoup` → `from scrapling.parser import Selector`
- `BeautifulSoup(html, 'html.parser')` → `Selector(html)`
- `soup.find(...)` → `page.find(...)`
- `soup.find_all(...)` → `page.find_all(...)`
- `soup.select_one(...)` → `page.css(...).first`
- `soup.select(...)` → `page.css(...)`
- `str(soup)` → `page.html_content`
- `soup.get_text(strip=True)` → `page.get_all_text(strip=True)`
- `element.attrs` → `element.attrib`
- `element.parent` → `element.parent`
- `list(element.children)` → `element.children`
- `list(element.descendants)` → `element.below_elements`

## Example: extracting links

BeautifulSoup:

```python
import requests
from bs4 import BeautifulSoup

response = requests.get('https://example.com')
soup = BeautifulSoup(response.text, 'html.parser')
for link in soup.find_all('a'):
    print(link['href'])
```

Scrapling:

```python
from scrapling import Fetcher

page = Fetcher.get('https://example.com')
for link in page.css('a::attr(href)'):
    print(link)
```

## Notes

- Scrapling combines fetching and parsing into one workflow.
- Scrapling always uses `lxml` for performance.
- Scrapling is read-only and optimized for extraction; it does not support DOM mutation like BeautifulSoup.
- `page.css()` returns an empty collection when nothing matches; use `.first` to safely get one element or `None`.
- `TextHandler` in Scrapling adds extra text cleaning helpers.
