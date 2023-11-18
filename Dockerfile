FROM python:3.8.2

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "main.py", "runserver", "0.0.0.0:8000"]