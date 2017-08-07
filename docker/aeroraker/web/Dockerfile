FROM ubuntu:17.04
RUN apt-get update && apt-get install -y \
    apache2 \
    libapache2-mod-wsgi-py3 \
    libjs-jquery \
    python3-django \
    python3-djangorestframework \
    protobuf-compiler \
    python3-protobuf \
    python3-requests \
    pwgen \
    git
RUN apt-get clean

ENV PROJECT_HOME /home/project

RUN git clone https://github.com/dme113q1/aeroraker.git ${PROJECT_HOME}
RUN mkdir ${PROJECT_HOME}/static
RUN sed -i "s/SECRET_KEY.*/SECRET_KEY = \'$(pwgen 50 1)\'/" ${PROJECT_HOME}/web/web/settings.py
RUN cd ${PROJECT_HOME}/web \
    && python3 manage.py makemigrations 'aeroraker' \
    && python3 manage.py migrate \
    && python3 manage.py collectstatic --noinput \
    && python3 manage.py shell < prepare.py

RUN protoc --python_out=${PROJECT_HOME}/web/aeroraker --proto_path=${PROJECT_HOME}/protobuf ${PROJECT_HOME}/protobuf/messages.proto

RUN chown -R www-data:www-data ${PROJECT_HOME}/web
COPY web.conf /etc/apache2/conf-available/web.conf
RUN a2enconf web
COPY static.conf /etc/apache2/conf-available/static.conf
RUN a2enconf static

CMD ["apache2ctl", "-D", "FOREGROUND"]
