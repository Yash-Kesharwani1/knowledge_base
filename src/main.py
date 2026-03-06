from src.scrapers.naukri.detail_parser import DetailParser
from src.scrapers.naukri.crawler import NaukriCrawler

if __name__ == "__main__":
    NaukriCrawler().run()
    DetailParser().run()