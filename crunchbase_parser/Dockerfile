FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /crunchbase_parser

RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    curl \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

COPY crunchbase_parser/requirements.txt /crunchbase_parser/

RUN pip install --upgrade pip
RUN pip install -r /crunchbase_parser/requirements.txt

RUN wget https://chromedriver.storage.googleapis.com/$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/ && \
    rm chromedriver_linux64.zip

COPY crunchbase_parser /crunchbase_parser

EXPOSE 8000

CMD ["uvicorn", "crunchbase_parser.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
