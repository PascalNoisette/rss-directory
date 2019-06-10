FROM python:3.7.3-alpine3.9

RUN apk add --no-cache --virtual .build-deps gcc libc-dev linux-headers openssl-dev

RUN adduser -S uwsgi

RUN mkdir /app /pub
COPY . /app/

RUN chown uwsgi -R /app/static
WORKDIR /app

RUN pip install -r requirements.txt && CFLAGS="-I/usr/local/opt/openssl/include" LDFLAGS="-L/usr/local/opt/openssl/lib" UWSGI_PROFILE_OVERRIDE=ssl=true pip install uwsgi -I --no-cache-dir

CMD ["python", "-u", "./directoryrss.py"]
