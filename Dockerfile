FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

EXPOSE 8080

# 运行 Flask 服务（main.py 内部已 app.run(host=0.0.0.0, port=8080)）
CMD ["python", "main.py"]