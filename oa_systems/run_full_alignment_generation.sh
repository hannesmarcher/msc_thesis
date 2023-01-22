#mkdir ./ontoconnect/cpc2ccs_full
#mkdir ./ontoconnect/cpc2cso_full
#
#cp ../ontologies/full_ontologies/cpc2ccs/source.owl ./ontoconnect/cpc2ccs_full/target.owl # for some reason it has to be in the other direction
#cp ../ontologies/full_ontologies/cpc2ccs/target.owl ./ontoconnect/cpc2ccs_full/source.owl
#cp ../ontologies/full_ontologies/cpc2cso/source.owl ./ontoconnect/cpc2cso_full/target.owl
#cp ../ontologies/full_ontologies/cpc2cso/target.owl ./ontoconnect/cpc2cso_full/source.owl
#sed -i 's/–/-/g' ./ontoconnect/cpc2cso_full/source.owl # OntoConnect cannot handle –, instead use -
#sed -i 's/–/-/g' ./ontoconnect/cpc2cso_full/target.owl # OntoConnect cannot handle –, instead use -
#sed -i 's/–/-/g' ./ontoconnect/cpc2ccs_full/source.owl # OntoConnect cannot handle –, instead use -
#sed -i 's/–/-/g' ./ontoconnect/cpc2ccs_full/target.owl # OntoConnect cannot handle –, instead use -

docker compose -f ./docker-compose-generate-full-alignment.yml up
./measure_execution_time.sh ./docker-compose-generate-full-alignment.yml > runtimes_full_alignment.txt

#rm ./ontoconnect/cpc2ccs_full/source.owl
#rm ./ontoconnect/cpc2ccs_full/target.owl
#mv ./ontoconnect/cpc2ccs_full/result_*.rdf ./ontoconnect/cpc2ccs_full/references.rdf
#rm ./ontoconnect/cpc2cso_full/source.owl
#rm ./ontoconnect/cpc2cso_full/target.owl
#mv ./ontoconnect/cpc2cso_full/result_*.rdf ./ontoconnect/cpc2cso_full/references.rdf


