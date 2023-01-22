FROM openjdk:11

WORKDIR /app/

RUN wget https://github.com/AgreementMakerLight/AML-Project/releases/download/v3.2/AML_v3.2.zip
RUN unzip AML_v3.2.zip

VOLUME ["/app/output_dir"]
VOLUME ["/app/onto_dir"]

CMD [ "java", "-jar", "./AML_v3.2/AgreementMakerLight.jar", "-s", "/app/onto_dir/source.owl", "-t", "/app/onto_dir/target.owl", "-o", "/app/output_dir/references.rdf", "-a" ]
