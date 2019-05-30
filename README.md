# rss-directory
Rss from directory listing

## Run as microservice in container

```
docker run --rm -d -p5000:5000 -v ~/YourPodcast:/pub/ netpascal0123/rss-directory
```
By default, this application will list all podcast file in the /pub/ directory and publish a RSS report on port 5000

## Run as wsgi service 

```
docker run --rm -d -p3031:3031 -v ~/YourPodcast:/pub/ netpascal0123/rss-directory uwsgi --ini uwsgi.ini

```


### Sample configuration to run with a reverse proxy

You must forward host and original protocol to backend

```
   location /podcast/ {

       proxy_pass         http://127.0.0.1:5000/;
       proxy_set_header X-Forwarded-Host $host/podcast;
       proxy_set_header X-Forwarded-Proto $scheme;
   }
```

This is similar if you prefer the wsgi backend

```

    location /podcast {
        # solve lot of problem caused by
        # - uwsgi's manage-script-name
        # - nginx uwsgi_modifier1 30;
        rewrite /podcast(.*) $1 break;

        include uwsgi_params;
        uwsgi_pass backend:3031;
        uwsgi_param X-Forwarded-Host $host/podcast;
        uwsgi_param X-Forwarded-Proto $scheme;
    }
    
```

You must have a clean document root for the backend

```
        uwsgi_param DOCUMENT_ROOT /pub/;
```

## Or build
```
git clone https://github.com/PascalNoisette/rss-directory.git
pip install -r requirements.txt
python ./directoryrss.py 
```

## Batch
You can also generate the rss file in command line, outside a server context
```
python ./background.py 
```
## Use broker instead of thread

If the broker url is supplied in the environment variable `BROKER` celery will be used instead of a thread.
In that case workers must also be started

```yaml
version: '3'

services:
  backend:
    build: .
    volumes:
      - "~/YourPodcast:/pub/"
    depends_on:
      - rabbitmq
    user: uwsgi
    command: sh -c "python -u ./directoryrss.py & python ./venv/bin/celery -A background worker --loglevel=debug"
    environment:
      - BROKER=pyamqp://guest@rabbitmq//
    ports:
      - 5000:5000

  rabbitmq:
      image: rabbitmq
```