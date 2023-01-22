FROM python:3.8.13

RUN pip install --upgrade pip
RUN pip install owl2vec_star

WORKDIR /app

VOLUME ["/app/output_dir"]
VOLUME ["/app/onto_dir"]
VOLUME ["/app/config_dir"]
VOLUME ["/app/word2vec"]

CMD [ "owl2vec_star", "standalone-multi", "--config_file", "/app/config_dir/default_multi.cfg" ]
