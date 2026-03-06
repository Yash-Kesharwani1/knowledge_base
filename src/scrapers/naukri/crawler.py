import json
import time
import random
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

class NaukriCrawler:
    def __init__(self):
        # Directly targeting Python Developer, 0-2 years
        self.search_url = "https://www.naukri.com/python-developer-jobs-10?k=python+developer&qproductJobSource=2&naukriCampus=true&nignbevent_src=jobsearchDeskGNB&experience=2"
        
        self.links = []

    def run(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(user_agent="Mozilla/5.0...")
            page = context.new_page()
            Stealth().apply_stealth_sync(page)

            print("Gathering job links...")
            page.goto(self.search_url, wait_until="networkidle")
            
            # Simple pagination loop (collects first 2 pages)
            for page_num in range(1, 3):
                page.wait_for_selector(".srp-jobtuple-wrapper")
                job_cards = page.locator(".srp-jobtuple-wrapper")
                
                for i in range(job_cards.count()):
                    url = job_cards.nth(i).locator("a.title").get_attribute("href")
                    if url: self.links.append(url)
                
                # Click 'Next' if available
                next_btn = page.locator("a.next-button")
                if next_btn.is_visible():
                    next_btn.click()
                    time.sleep(random.uniform(2, 4))

            # 1. Load existing links if the file exists
            existing_links = []
            try:
                with open("data/raw_links.json", "r") as f:
                    existing_links = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                # If file doesn't exist or is empty, start with an empty list
                existing_links = []

            # 2. Combine existing and new links
            # Using a set automatically handles deduplication
            combined_links = list(set(existing_links + self.links))

            # 3. Write the updated list back to the file
            with open("data/raw_links.json", "w") as f:
                json.dump(combined_links, f, indent=4)
            
            print(f"Update complete. Total links stored: {len(combined_links)}")
            browser.close()

if __name__ == "__main__":
    NaukriCrawler().run()