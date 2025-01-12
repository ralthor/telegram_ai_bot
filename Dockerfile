FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY telegram_bot.py /app
COPY open_ai_chat.py /app
COPY text_to_speach.py /app
COPY utils.py /app

CMD ["python", "telegram_bot.py"]
