wget https://gitlab.inria.fr/moex/alignapi/-/archive/version-4.10/alignapi-version-4.10.zip
unzip alignapi-version-4.10.zip

rm alignapi-version-4.10/build.xml
cp build.xml alignapi-version-4.10/build.xml

cd alignapi-version-4.10/
cp lib/ontosim/ontosim.jar lib/ontosim.jar
cp lib/ontosim/ontosim.pom lib/ontosim.pom
ant mavenize