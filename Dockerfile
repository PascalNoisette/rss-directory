FROM python:3.7.3-alpine3.9

RUN apk add --no-cache --virtual .build-deps gcc libc-dev linux-headers

RUN adduser -S uwsgi

RUN mkdir /app /pub
COPY . /app/

RUN chown uwsgi -R /app/static
WORKDIR /app

RUN pip install -r requirements.txt && pip install uwsgi

CMD ["python", "-u", "./directoryrss.py"]
