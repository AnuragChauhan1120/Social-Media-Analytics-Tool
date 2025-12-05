FROM python:3.10-slim

# System deps for wordcloud / pillow / scraping
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

RUN chmod +x start.sh

EXPOSE 8080

CMD ["./start.sh"]
