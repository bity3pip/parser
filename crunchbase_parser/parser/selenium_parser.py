from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

class BaseWebParserSelenium(ABC):
    @abstractmethod
    def fetch_data(self, url: str) -> list:
        pass

class WebParserSelenium:
    def __init__(self, data, num_threads: int = 40):
        self.driver = None
        self.results = {}
        self._data = data
        self.num_threads = num_threads

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

    def fetch_data(self, url: str) -> list:
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

    def _process_row(self, row):
        uuid = row.get("uuid", "").strip()
        url = row.get("cb_url", "").strip()
        industries = []

        if url:
            industries = self.fetch_data(url)
        return uuid, industries

    def process_csv(self):
        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = [executor.submit(self._process_row, row) for row in self._data]

            for future in as_completed(futures):
                try:
                    uuid, industries = future.result()
                    self.results[uuid] = industries
                except Exception as e:
                    print(f"Error processing row: {e}")

    def get_result(self):
        return [{"uuid": uuid, "industry": ", ".join(industries)} for uuid, industries in self.results.items()]
