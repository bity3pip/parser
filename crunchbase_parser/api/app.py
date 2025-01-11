from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from parser.selenium_parser import WebParserSelenium

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