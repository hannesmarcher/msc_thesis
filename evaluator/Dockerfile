FROM python:3.8.13

RUN pip install --upgrade pip

RUN apt-get update

WORKDIR /app/working_dir

ADD evaluate.py /app
ADD helpers /app/helpers
ADD requirements.txt /app

RUN pip install -r /app/requirements.txt

VOLUME ["/app/working_dir"]

CMD [ "python", "/app/evaluate.py" ]