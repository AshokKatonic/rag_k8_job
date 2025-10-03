# Test the complete workflow
from usage import scrape_website

result = scrape_website("test_org_123", "https://httpbin.org/html")
if not result:
    print(f"No content was scraped from")
    raise ValueError(f"No content was scraped from - check if the page is accessible and scrapeable")
print(f"Scraping result: {result}")






