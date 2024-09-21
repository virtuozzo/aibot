FROM python:3.11 AS build
ADD vzbot-server.py .
#Load local .env file if needed
#COPY .env .
COPY static ./static
COPY templates ./templates
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
CMD ["python3", "./vzbot-server.py"] 
