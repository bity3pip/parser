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

    def fetch_data_multiple_pages(self, urls):
        if not self.driver:
            self._initialize_driver()

        all_results = {}
        for url in urls:
            results = self.fetch_data(url)
            all_results[url] = results

        self.driver.quit()
        return all_results

    def _process_row(self, row):
        local_results = {}
        uuid = row.get("uuid", "").strip()
        urls = row.get("urls", "").strip()

        if urls:
            print(f"Processing {urls}")
            industries = self.fetch_data_multiple_pages(urls)
            if industries:
                for industry in industries:
                    if uuid in local_results:
                        local_results[uuid].add(industry)
                    else:
                        local_results[uuid] = {industry}
        return local_results

    def process_csv(self):
        local_results_list = []
        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            future_to_row = {executor.submit(self._process_row, row): row for row in self._data}

            for future in as_completed(future_to_row):
                try:
                    local_results = future.result()
                    local_results_list.append(local_results)
                except Exception as e:
                    row = future_to_row[future]
                    print(f"Error processing row {row}: {e}")

        for local_results in local_results_list:
            for uuid, industries in local_results.items():
                if uuid in self.results:
                    self.results[uuid].update(industries)
                else:
                    self.results[uuid] = industries