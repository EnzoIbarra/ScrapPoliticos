FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema requeridas
RUN apt-get update && apt-get install -y \
    tor \
    wget \
    gnupg \
    tesseract-ocr \
    tesseract-ocr-spa \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar navegadores y sus dependencias de sistema
RUN playwright install --with-deps chromium

COPY . .

CMD ["python", "main.py"]
