FROM python:3.10-slim
COPY . /sing-box-subscribe
WORKDIR /sing-box-subscribe
RUN \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
EXPOSE 8080
VOLUME /data

CMD ["python", "main.py", "server", "-d", "/data"]
