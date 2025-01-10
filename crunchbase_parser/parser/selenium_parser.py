from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class WebParserSelenium:
    def __init__(self):
        self.driver = None

    def _initialize_driver(self):
        chrome_options = Options()
        #chrome_options.add_argument("--headless")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def fetch_data(self, url):
        try:
            print(f"Запрос к URL: {url}")
            if not self.driver:
                self._initialize_driver()

            self.driver.get(url)

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "chips-container"))
            )

            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")

            chips_container = soup.find("chips-container")
            if chips_container:
                chip_texts = chips_container.find_all("div", class_="chip-text")
                return [chip.text.strip() for chip in chip_texts]
            return ["Индустрия не найдена"]
        except Exception as e:
            print(f"Ошибка при парсинге {url}: {str(e)}")
            return [f"Ошибка при парсинге {url}: {str(e)}"]

    def fetch_data_multiple_pages(self, urls):
        if not self.driver:
            self._initialize_driver()

        all_results = {}
        for url in urls:
            results = self.fetch_data(url)
            all_results[url] = results

        self.driver.quit()
        return all_results