#!/bin/bash

sudo apt-get install software-properties-common
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update
sudo apt-get install certbot

# Run this in a different window:
sudo python3 -m http.server 80

# Then this to collect the certificate
sudo certbot certonly --webroot -w . -d colourize.cf

sudo cp /etc/letsencrypt/live/colourize.cf/fullchain.pem docker_nginx/ssl_certificates/fullchain.pem
sudo cp /etc/letsencrypt/live/colourize.cf/privkey.pem docker_nginx/ssl_certificates/privkey.pem

sudo chmod +r docker_nginx/ssl_certificates/privkey.pem