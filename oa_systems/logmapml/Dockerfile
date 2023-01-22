FROM python:3.8.13

RUN pip install --upgrade pip

RUN apt-get update && \
    apt-get install -y openjdk-11-jdk-headless;

WORKDIR /app

ADD main.py /app
ADD src /app/src
ADD requirements.txt /app

RUN pip install -r ./requirements.txt

VOLUME ["/app/output_dir"]
VOLUME ["/app/onto_dir"]
VOLUME ["/app/config_dir"]
VOLUME ["/app/word2vec"]
VOLUME ["/app/owl2vec_star"]

RUN echo "import nltk; nltk.download('punkt')" | python

CMD [ "python", "./main.py", "-c", "/app/config_dir/", "-i", "/app/onto_dir/", "-o", "/app/output_dir/" ]