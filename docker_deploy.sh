docker build -t eodhp_website .
docker tag eodhp_website hcollingwoodtpz/eodhp_website:0.1.4
docker push hcollingwoodtpz/eodhp_website:0.1.4

#docker run --rm -p 8000:8000 eodhp_web_presence
