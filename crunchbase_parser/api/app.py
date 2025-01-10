from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from crunchbase_parser.parser.selenium_parser import WebParserSelenium
from crunchbase_parser.parser.test import test_selenium_function

app = FastAPI()


class UrlsRequest(BaseModel):
    urls: List[str]


@app.post("/parse/")
async def parse_urls(request: UrlsRequest):
    parser = WebParserSelenium()

    results = {}
    for url in request.urls:
        data = parser.fetch_data(url)
        results[url] = data

    return {"results": results}


@app.get("/test-selenium/")
async def test_selenium():
    result = test_selenium_function()
    return result