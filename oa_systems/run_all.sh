PRUNE_ARG=$(echo "--prune_before_running")

if [ "$1" = "$PRUNE_ARG"  ]
then
	echo "pruning..."
	docker system prune -af
fi

echo "--------------------------------"
echo "Preparation..."
echo "  Generating Owl2Vec* multi word embeddings"
docker compose -f ./logmapml/owl2vec_star/docker-compose.yml up >> logs.txt
rm logs.txt
echo "--------------------------------"


echo "executing OntoConnect"
cp ../ontologies/sub_ontologies/cpc2ccs/source.owl ./ontoconnect/cpc2ccs/target.owl # for some reason it has to be in the other direction
cp ../ontologies/sub_ontologies/cpc2ccs/target.owl ./ontoconnect/cpc2ccs/source.owl
cp ../ontologies/sub_ontologies/cpc2cso/source.owl ./ontoconnect/cpc2cso/target.owl
cp ../ontologies/sub_ontologies/cpc2cso/target.owl ./ontoconnect/cpc2cso/source.owl
sed -i 's/–/-/g' ./ontoconnect/cpc2cso/source.owl # OntoConnect cannot handle –, instead use -
cp ../ontologies/sub_ontologies/anatomy/source.owl ./ontoconnect/anatomy/target.owl
cp ../ontologies/sub_ontologies/anatomy/target.owl ./ontoconnect/anatomy/source.owl
docker compose -f ./ontoconnect/docker-compose.yml up >> logs.txt
rm ./ontoconnect/cpc2ccs/source.owl
rm ./ontoconnect/cpc2ccs/target.owl
mv ./ontoconnect/cpc2ccs/result_*.rdf ./ontoconnect/cpc2ccs/references.rdf
rm ./ontoconnect/cpc2cso/source.owl
rm ./ontoconnect/cpc2cso/target.owl
mv ./ontoconnect/cpc2cso/result_*.rdf ./ontoconnect/cpc2cso/references.rdf
rm ./ontoconnect/anatomy/source.owl
rm ./ontoconnect/anatomy/target.owl
mv ./ontoconnect/anatomy/result_*.rdf ./ontoconnect/anatomy/references.rdf

echo "executing LogMap"
docker compose -f ./logmap/docker-compose.yml up >> logs.txt
mv ./logmap/cpc2ccs/logmap2_mappings.rdf ./logmap/cpc2ccs/references.rdf
mv ./logmap/cpc2cso/logmap2_mappings.rdf ./logmap/cpc2cso/references.rdf
mv ./logmap/anatomy/logmap2_mappings.rdf ./logmap/anatomy/references.rdf

mv ./logmap/cpc2ccs_experimental/logmap2_mappings.rdf ./logmap/cpc2ccs_experimental/references.rdf
mv ./logmap/cpc2cso_experimental/logmap2_mappings.rdf ./logmap/cpc2cso_experimental/references.rdf
mv ./logmap/anatomy_experimental/logmap2_mappings.rdf ./logmap/anatomy_experimental/references.rdf

echo "executing AML"
docker compose -f ./aml/docker-compose.yml up >> logs.txt

echo "executing LogMapLt"
docker compose -f ./logmap_lite/docker-compose.yml up >> logs.txt
mv ./logmap_lite/cpc2ccs/logmap-lite-mappings.rdf ./logmap_lite/cpc2ccs/references.rdf
mv ./logmap_lite/cpc2cso/logmap-lite-mappings.rdf ./logmap_lite/cpc2cso/references.rdf
mv ./logmap_lite/anatomy/logmap-lite-mappings.rdf ./logmap_lite/anatomy/references.rdf

echo "executing LogMap-ML"
docker compose -f ./logmapml/docker/docker-compose-c1.yml up >> logs.txt
docker compose -f ./logmapml/docker/docker-compose-c2.yml up >> logs.txt
docker compose -f ./logmapml/docker/docker-compose-c3.yml up >> logs.txt
docker compose -f ./logmapml/docker/docker-compose-c4.yml up >> logs.txt

echo "executing LXLHMeta"
docker compose -f ./meta_matcher/docker/docker-compose.yml up >> logs.txt

echo "executing Baseline"
docker compose -f ./baseline/docker/docker-compose.yml up >> logs.txt

cho "executing Evolutionary"
docker compose -f ./evolutionary_algorithm/docker/docker-compose.yml up >> logs.txt

echo "executing SANOM"
docker compose -f ./sanom/docker/docker-compose.yml up >> logs.txt

echo "executing BERTMAP-US"
docker compose -f ./bertmapunsupervised/docker/docker-compose.yml up >> logs.txt


echo "collecting execution times"
./measure_execution_time.sh ./logmapml/owl2vec_star/docker-compose.yml ./ontoconnect/docker-compose.yml ./logmap/docker-compose.yml ./aml/docker-compose.yml ./logmap_lite/docker-compose.yml ./logmapml/docker/docker-compose-c1.yml ./logmapml/docker/docker-compose-c2.yml ./logmapml/docker/docker-compose-c3.yml ./logmapml/docker/docker-compose-c4.yml ./meta_matcher/docker/docker-compose.yml ./baseline/docker/docker-compose.yml ./sanom/docker/docker-compose.yml ./bertmapunsupervised/docker/docker-compose.yml ./evolutionary_algorithm/docker/docker-compose.yml > runtimes.txt

