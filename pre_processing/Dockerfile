FROM python:3.8.13

RUN pip install --upgrade pip

RUN apt-get update

WORKDIR /app

ADD main.py /app
ADD ground_truth /app/ground_truth
ADD ontology_preprocessing /app/ontology_preprocessing
ADD requirements.txt /app

RUN pip install -r ./requirements.txt

VOLUME ["/app/sub_ontologies"]
VOLUME ["/app/full_ontologies"]
VOLUME ["/app/resources"]

CMD [ "python", "./main.py", "-r", "/app/resources", "-s", "/app/sub_ontologies", "-f", "/app/full_ontologies" ]