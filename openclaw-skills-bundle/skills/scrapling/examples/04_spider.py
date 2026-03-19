"""
Example 4: Python - Spider (auto-crawling framework)

Scrapes all pages of quotes.toscrape.com by following pagination automatically.
The spider yields structured items and exports them to JSON.
"""

from scrapling.spiders import Spider, Response


class QuotesSpider(Spider):
    name = "quotes"
    start_urls = ["https://quotes.toscrape.com/"]
    concurrent_requests = 5

    async def parse(self, response: Response):
        for quote in response.css(".quote"):
            yield {
                "text": quote.css(".text::text").get(),
                "author": quote.css(".author::text").get(),
                "tags": quote.css(".tags .tag::text").getall(),
            }

        next_page = response.css(".next a")
        if next_page:
            yield response.follow(next_page[0].attrib["href"])


if __name__ == "__main__":
    result = QuotesSpider().start()
    result.items.to_json("quotes.json", indent=True)
    print(f"Scraped {result.stats.items_scraped} quotes")
    print("Exported to quotes.json")
