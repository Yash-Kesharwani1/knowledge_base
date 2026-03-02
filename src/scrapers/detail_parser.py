import json
import time
import random
import re
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

class DetailParser:
    def __init__(self):
        self.output_file = "data/jobs_final.json"

    def clean_list(self, text_list):
        """Removes empty strings and whitespace from lists."""
        return [t.strip() for t in text_list if len(t.strip()) > 5]

    def run(self):
        with open("data/raw_links.json", "r") as f:
            links = json.load(f)

        final_data = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            Stealth().apply_stealth_sync(page)

            for url in links[:5]: # Testing first 5
                try:
                    print(f"Deep scraping: {url}")
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    time.sleep(random.uniform(5, 8)) # Give dynamic content time to load

                    # Use broader selectors to find content
                    raw_summary = page.locator('section.job-desc').first.inner_text() if page.locator('section.job-desc').count() > 0 else "N/A"
                    
                    # Target the JSON keys you want
                    job_details = {
                        "jobRole": page.locator("h1.jd-header-title").first.inner_text() if page.locator("h1.jd-header-title").count() > 0 else "Python Developer",
                        "job_summary": raw_summary[:300] + "...", # First few sentences
                        "employment_type": "Full-time", # Typically fixed
                        "seniority_level": "Entry-level",
                        "responsibilities": self.clean_list(page.locator(".job-desc li").all_inner_texts()),
                        "qualifications": self.clean_list(page.locator(".education li").all_inner_texts()),
                        "preferred_skills": self.clean_list(page.locator(".key-skill span").all_inner_texts()),
                        "salary_range": page.locator(".salary").first.inner_text() if page.locator(".salary").count() > 0 else "Not Disclosed",
                        "experience_level": 0,
                        "scraped_url": url
                    }

                    # FALLBACK: If lists are empty, split the raw_summary by periods/newlines
                    if not job_details["responsibilities"] and raw_summary != "N/A":
                        sentences = re.split(r'\. |\n', raw_summary)
                        job_details["responsibilities"] = self.clean_list(sentences[:5])

                    final_data.append(job_details)
                except Exception as e:
                    print(f"Skipping {url} due to error: {e}")

            with open(self.output_file, "w") as f:
                json.dump(final_data, f, indent=4)
            print(f"Saved results to {self.output_file}")
            browser.close()

if __name__ == "__main__":
    DetailParser().run()