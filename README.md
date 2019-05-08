# rss-directory
Rss from directory listing

## Run in container

```
docker run --rm -d -p5000:5000 -v ~/YourPodcast:/pub/ netpascal0123/rss-directory
```
By default, this application will list all podcast file in the /pub/ directory and publish a RSS report on port 5000

## Or build
```
git clone https://github.com/PascalNoisette/rss-directory.git
pip install -r requirements.txt
python ./directoryrss.py 
```
