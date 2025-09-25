FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade setuptools
RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]