FROM ubuntu:latest
EXPOSE 80

RUN apt-get update -y && \
    apt-get install -y python-pip python3-pip python3-dev python-virtualenv \
                       libjpeg-dev zlib1g-dev \
                       build-essential mariadb-client libmariadbclient-dev apache2 libapache2-mod-wsgi-py3
RUN rm /etc/apache2/sites-enabled/000-default.conf
COPY ./docker/apache-filmlog.conf /etc/apache2/sites-available/filmlog.conf
RUN ln -s /etc/apache2/sites-available/filmlog.conf /etc/apache2/sites-enabled/filmlog.conf
COPY . /srv/filmlog.org
COPY docker/venv.wsgi /srv/filmlog.org/venv.wsgi
RUN useradd -d /srv/filmlog.org filmlog
RUN chown -R filmlog:filmlog /srv/filmlog.org
RUN su - filmlog -c "virtualenv -p /usr/bin/python3 /srv/filmlog.org/venv"
RUN su - filmlog -c "cd /srv/filmlog.org && . venv/bin/activate && pip install -r /srv/filmlog.org/requirements.txt"
CMD /usr/sbin/apache2ctl -D FOREGROUND
