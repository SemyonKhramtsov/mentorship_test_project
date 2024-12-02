FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app/src

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

CMD ["python", "/app/src/manage.py", "runserver", "127.0.0.1:8000"]