FROM openjdk:11

WORKDIR /app/config_dir

RUN wget https://github.com/ernestojimenezruiz/logmap-matcher/releases/download/logmap-matcher-july-2021/logmap-matcher-standalone-july-2021.zip -P ../
RUN unzip ../logmap-matcher-standalone-july-2021.zip -d ../

VOLUME ["/app/output_dir"]
VOLUME ["/app/onto_dir"]
VOLUME ["/app/config_dir"]

#CMD ["ls", "../"]
CMD [ "java", "-jar", "../logmap-matcher-4.0.jar", "LITE", "file:///app/onto_dir/source.owl", "file:///app/onto_dir/target.owl", "/app/output_dir/" ]
