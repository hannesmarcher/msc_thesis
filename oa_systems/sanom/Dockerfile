FROM openjdk:11

WORKDIR /app

ADD ./align_api /app/align_api
ADD ./src /app/src
ADD pom.xml /app/pom.xml

RUN apt-get update && \
    apt-get install -y maven && \
    apt-get  install -y ant;
RUN cd ./align_api && \
    ./init.sh && \
    cd ..;
RUN mvn package

VOLUME ["/app/output_dir"]
VOLUME ["/app/onto_dir"]
VOLUME ["/app/config_dir"]

#CMD ["ls", "/app/onto_dir/"]
CMD [ "java", "-jar", "./target/sanom-custom-1.0-SNAPSHOT-jar-with-dependencies.jar", "--source", "/app/onto_dir/source.owl", "--target", "/app/onto_dir/target.owl", "--output", "/app/output_dir/references.rdf" ]