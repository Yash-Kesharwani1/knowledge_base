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

            for url in links[:200]:
                try:
                    print(f"Deep scraping: {url}")
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    time.sleep(random.uniform(4, 6))

                    # 1. Get the Job Description Container
                    # This contains the raw summary and the list of points
                    jd_container = page.locator("[class*='job-desc-container']")
                    raw_summary = jd_container.first.inner_text() if jd_container.count() > 0 else "N/A"

                    # 2. Extract Responsibilities (the bullet points in description)
                    # These are usually in a div with 'dang-inner-html'
                    resp_elements = page.locator("[class*='dang-inner-html'] li")
                    
                    # 3. Extract Qualifications (UG/PG details)
                    qual_elements = page.locator("[class*='education'] [class*='details']")

                    # 4. Extract Preferred Skills (the clickable chips)
                    skill_elements = page.locator("[class*='key-skill'] a span")

                    # 5. Extract Salary and Experience directly
                    salary = page.locator("[class*='salary']").first.inner_text() if page.locator("[class*='salary']").count() > 0 else "Not Disclosed"
                    
                    job_details = {
                        "jobRole": page.locator("h1[class*='jd-header-title']").first.inner_text(),
                        "job_summary": raw_summary[:300].replace('\n', ' ') + "...",
                        "employment_type": "Full-time",
                        "seniority_level": "Entry-level",
                        "responsibilities": self.clean_list(resp_elements.all_inner_texts()),
                        "qualifications": self.clean_list(qual_elements.all_inner_texts()),
                        "preferred_skills": self.clean_list(skill_elements.all_inner_texts()),
                        "salary_range": salary,
                        "experience_level": page.locator("[class*='exp'] span").first.inner_text() if page.locator("[class*='exp']").count() > 0 else "0",
                        "scraped_url": url
                    }

                    final_data.append(job_details)

                except Exception as e:
                    print(f"Skipping {url} due to error: {e}")

            with open(self.output_file, "w") as f:
                json.dump(final_data, f, indent=4)
            print(f"Saved results to {self.output_file}")
            browser.close()

if __name__ == "__main__":
    DetailParser().run()