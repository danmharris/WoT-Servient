FROM python:3.7
WORKDIR /usr/src/app
COPY . .
RUN pip install gunicorn && pip install .
RUN mkdir -p /data

ENV DB_PATH /data
EXPOSE 8000
VOLUME /data
ENTRYPOINT ["gunicorn", "-b 0.0.0.0:8000", "wot.grouper.app:create_app()"]
