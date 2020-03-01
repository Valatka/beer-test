FROM python:3.7.2-stretch

WORKDIR /api

Add . /api

RUN pip install -r requirements.txt

RUN python graph.py -r

CMD ["uwsgi", "uwsgi.ini"]