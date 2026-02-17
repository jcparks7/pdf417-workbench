FROM python:3.11-slim

WORKDIR /project

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY code/app.py code/app.py

EXPOSE 8888

CMD ["python3", "code/app.py"]
