FROM nginx:1.17-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d

COPY /static /webapp/static
RUN chown -R nginx:nginx /webapp/static

RUN mkdir /ssl_certificates

COPY /ssl_certificates/fullchain.pem /ssl_certificates/fullchain.pem
COPY /ssl_certificates/privkey.pem /ssl_certificates/privkey.pem

RUN chmod 400 /ssl_certificates/privkey.pem

COPY /password/.htpasswd /password/.htpasswd
RUN chmod 666 /password/.htpasswd


EXPOSE 80
EXPOSE 5000
EXPOSE 443