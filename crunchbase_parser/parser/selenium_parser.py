from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


class WebParserSelenium:
    def __init__(self):
        self.driver = None

    def _initialize_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-browser-side-navigation")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def fetch_data(self, url):
        try:
            if not self.driver:
                self._initialize_driver()

            self.driver.get(url)

            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".chip-text"))
            )

            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")

            chips_container = soup.find("chips-container")
            if chips_container:
                chip_texts = chips_container.find_all("div", class_="chip-text")
                return [chip.text.strip() for chip in chip_texts]
            return ["Industries not found"]
        except Exception as e:
            print(f"Parsing error: {str(e)}")
            return [f"Parsing error: {str(e)}"]

    def fetch_data_multiple_pages(self, urls):
        if not self.driver:
            self._initialize_driver()

        all_results = {}
        for url in urls:
            results = self.fetch_data(url)
            all_results[url] = results

        self.driver.quit()
        return all_results