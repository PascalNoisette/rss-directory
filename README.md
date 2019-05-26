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
