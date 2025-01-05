FROM python:3.11-slim-bullseye

WORKDIR /usr/src/app
COPY . .

RUN pip install -r requirements.txt

CMD ["python", "app.py"]