FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    flask \
    pdf417gen \
    qrcode[pil] \
    Pillow

COPY code/app.py .

EXPOSE 8888

CMD ["python", "app.py"]