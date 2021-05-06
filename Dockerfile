FROM openjdk:8-alpine
  
RUN apk update && apk add ca-certificates openssl wget unzip subversion maven
RUN apk upgrade


## Download apache-tomcat and extract:
RUN wget -q https://archive.apache.org/dist/tomcat/tomcat-9/v9.0.21/bin/apache-tomcat-9.0.21.zip
RUN unzip -q apache-tomcat-9.0.21.zip

## Check out version of ctakes with best working web-rest module
## Then compile with maven
RUN svn export https://svn.apache.org/repos/asf/ctakes/trunk@1889492 ctakes

WORKDIR /
COPY covid.bsv /ctakes/resources/org/apache/ctakes/dictionary/lookup/fast/
COPY covid.xml /ctakes/ctakes-web-rest/src/main/resources/org/apache/ctakes/dictionary/lookup/fast/
COPY pom.xml /ctakes

COPY CovidPipelineContext.piper /ctakes/ctakes-web-rest/src/main/resources/pipers/Default.piper

# recompile, hopefully this part takes less time
WORKDIR /ctakes

RUN mvn compile -pl '!ctakes-distribution' -pl '!ctakes-temporal' -pl '!ctakes-dictionary-lookup-res' -pl '!ctakes-dependency-parser-res-clear' -pl '!ctakes-lvg-res' -DskipTests
RUN mvn install -pl '!ctakes-distribution' -pl '!ctakes-temporal' -pl '!ctakes-dictionary-lookup-res' -pl '!ctakes-dependency-parser-res-clear' -pl '!ctakes-lvg-res' -DskipTests

WORKDIR /
RUN mv /ctakes/ctakes-web-rest/target/ctakes-web-rest.war /apache-tomcat-9.0.21/webapps/

RUN rm -rf /root/.m2

ENV TOMCAT_HOME=/apache-tomcat-9.0.21
ENV CTAKES_HOME=/ctakes

EXPOSE 8080

WORKDIR $TOMCAT_HOME
RUN chmod u+x bin/*.sh

CMD bin/catalina.sh run
