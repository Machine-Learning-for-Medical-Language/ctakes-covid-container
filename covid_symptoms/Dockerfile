FROM openjdk:8-alpine

ENV HTTP_PROXY="http://10.41.13.6:3128"
ENV HTTPS_PROXY="http://10.41.13.6:3128"
ENV FTP_PROXY="http://10.41.13.6:3128"
  
RUN apk update && apk add ca-certificates openssl wget unzip subversion maven
RUN apk upgrade

RUN apk add --no-cache nss
## Download apache-tomcat and extract:
RUN wget -q https://archive.apache.org/dist/tomcat/tomcat-9/v9.0.21/bin/apache-tomcat-9.0.21.zip
RUN unzip -q apache-tomcat-9.0.21.zip

## Check out version of ctakes with best working web-rest module
## Then compile with maven
RUN svn export https://svn.apache.org/repos/asf/ctakes/trunk@1894987 ctakes

WORKDIR /
COPY covid_symptoms_ctakes.bsv /ctakes/resources/org/apache/ctakes/dictionary/lookup/fast/covid.bsv
COPY covid_symptoms.xml /ctakes/ctakes-web-rest/src/main/resources/org/apache/ctakes/dictionary/lookup/fast/
COPY pom.xml /ctakes

## Copy hsql dictionary descriptor into right location
RUN wget -q -O dict.zip  https://sourceforge.net/projects/ctakesresources/files/snorx_2021aa.zip/download
RUN mkdir -p /ctakes/resources/org/apache/ctakes/dictionary/lookup/fast/
RUN unzip -o dict.zip -d /ctakes/ctakes-web-rest/src/main/resources/org/apache/ctakes/dictionary/lookup/fast/

COPY CovidPipelineContext.piper /ctakes/ctakes-web-rest/src/main/resources/pipers/Default.piper

# recompile, hopefully this part takes less time
WORKDIR /ctakes

# Optimized for container size:
# RUN mvn compile -pl '!ctakes-distribution' -pl '!ctakes-temporal' -pl '!ctakes-dictionary-lookup-res' -pl '!ctakes-dependency-parser-res-clear' -pl '!ctakes-lvg-res' -DskipTests
# RUN mvn install -pl '!ctakes-distribution' -pl '!ctakes-temporal' -pl '!ctakes-dictionary-lookup-res' -pl '!ctakes-dependency-parser-res-clear' -pl '!ctakes-lvg-res' -DskipTests

# works on systems with prohibitions on downloading SNAPSHOT jars:
RUN mvn compile -pl '!ctakes-distribution' -DskipTests
RUN mvn install -pl '!ctakes-distribution' -DskipTests

WORKDIR /
RUN mv /ctakes/ctakes-web-rest/target/ctakes-web-rest.war /apache-tomcat-9.0.21/webapps/

RUN rm -rf /root/.m2

ENV TOMCAT_HOME=/apache-tomcat-9.0.21
ENV CTAKES_HOME=/ctakes

EXPOSE 8080

WORKDIR $TOMCAT_HOME
RUN chmod u+x bin/*.sh

CMD bin/catalina.sh run
