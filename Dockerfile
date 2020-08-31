FROM python:3.7
WORKDIR /usr/src/app
COPY . .
RUN pip install gunicorn
RUN pip install .
RUN mkdir -p /opt/wot/config/ && mv config/* /opt/wot/config/
CMD ["gunicorn", "-b 0.0.0.0:8000", "wot.adapter.app:create_app()"]
