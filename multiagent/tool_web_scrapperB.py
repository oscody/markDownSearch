import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from dotenv import load_dotenv


class SeleniumScraper:
    def __init__(self):
        load_dotenv()  
        self.driver_path = 'multiagent/chromedriver'
        

    def scrape_website(self, website):
        print("Connecting to Scraping Browser...")
        try:
            options = Options()
            options.add_argument("--headless") 
            service = Service(executable_path=self.driver_path)
            driver = webdriver.Chrome(service=service, options=options)


            driver.get(website)
            print("Navigated! Scraping page content...")
            html = driver.page_source
            return html
        except Exception as e:
                print(f"Error processing specific file: {e}")
        finally:
            driver.quit()

    @staticmethod
    def extract_body_content(html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        body_content = soup.body
        return str(body_content) if body_content else ""

    @staticmethod
    def clean_body_content(body_content):
        soup = BeautifulSoup(body_content, "html.parser")
        for script_or_style in soup(["script", "style"]):
            script_or_style.extract()
        cleaned_content = soup.get_text(separator="\n")
        cleaned_content = "\n".join(
            line.strip() for line in cleaned_content.splitlines() if line.strip()
        )
        return cleaned_content

    @staticmethod
    def split_dom_content(dom_content, max_length=6000):
        return [
            dom_content[i : i + max_length]
            for i in range(0, len(dom_content), max_length)
        ]

    # If run doesn't need instance data either, you could do staticmethod or classmethod
    # But if it needs to use self.scrape_website, keep it as an instance method or do more advanced usage.
    def run(self, url):
        raw_html = self.scrape_website(url)
        body_content = self.extract_body_content(raw_html)
        cleaned_content = self.clean_body_content(body_content)
        return cleaned_content