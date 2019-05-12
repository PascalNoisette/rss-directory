FROM python:3.7.3-alpine3.9
RUN mkdir /app /pub
COPY . /app/
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "-u", "./directoryrss.py"]
