FROM python:3.8.2

RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]