FROM nginx
LABEL version="1.0.0" description="Disponibilizando site com NGINX" maintainer="Matheus Castiglioni<matheushcastiglioni@gmail.com>"
RUN cd / && mkdir Arquivos && chmod 777 -R Arquivos/
COPY ./site/index.html /usr/share/nginx/html/
VOLUME /Arquivos/
EXPOSE 80
ENV API_URL=http://localhost:8000/api/
ENV API_BANCO=meu_site
WORKDIR /usr/share/nginx/html/
ENTRYPOINT ["/usr/sbin/nginx"]
CMD ["-g", "daemon off;"]