FROM nginx
RUN apt-get update && apt-get install -y curl
COPY home.000 /usr/share/nginx/html
RUN cd /usr/share/nginx/html && tar xvf home.000
EXPOSE 80