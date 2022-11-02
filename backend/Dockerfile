FROM python:3.7-slim
WORKDIR /app
COPY . .
RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]