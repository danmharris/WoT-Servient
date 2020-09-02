FROM python:3.7
WORKDIR /usr/src/app
COPY . .
RUN pip install gunicorn
RUN pip install .
WORKDIR /opt/wot/
ENTRYPOINT ["gunicorn", "-b 0.0.0.0:8000", "wot.grouper.app:create_app()"]
