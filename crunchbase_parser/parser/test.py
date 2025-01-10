from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_selenium_function():
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        test_url = "https://www.google.com"
        driver.get(test_url)

        title = driver.title
        driver.quit()

        return {"status": "success", "message": f"Page title: {title}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
