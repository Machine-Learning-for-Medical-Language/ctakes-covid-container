FROM eclipse-temurin:8-jdk

# Set to your proxies if necessary to build behind firewalls:
#ENV HTTP_PROXY="http://10.41.13.6:3128"
#ENV HTTPS_PROXY="http://10.41.13.6:3128"
#ENV FTP_PROXY="http://10.41.13.6:3128"

RUN apt-get update && apt-get install -y ca-certificates openssl wget unzip subversion maven

RUN apt-get install -y libnss3

## Check out version of ctakes with best working web-rest module
## Then compile with maven
RUN svn export https://svn.apache.org/repos/asf/ctakes/trunk@1894987 ctakes

WORKDIR /tmp
## Copy hsql dictionary descriptor into right location
RUN wget -q -O dict.zip  https://sourceforge.net/projects/ctakesresources/files/snorx_2021aa.zip/download
RUN mkdir -p /ctakes/resources/org/apache/ctakes/dictionary/lookup/fast/
RUN unzip -o dict.zip -d /ctakes/ctakes-web-rest/src/main/resources/org/apache/ctakes/dictionary/lookup/fast/

COPY CovidPipelineContext.piper /ctakes/ctakes-web-rest/src/main/resources/pipers/Default.piper

# Copy in latest dictionary info
COPY covid_symptoms_ctakes.bsv /ctakes/resources/org/apache/ctakes/dictionary/lookup/fast/covid.bsv
COPY covid_symptoms.xml /ctakes/ctakes-web-rest/src/main/resources/org/apache/ctakes/dictionary/lookup/fast/
COPY pom.xml /ctakes

# recompile, hopefully this part takes less time
WORKDIR /ctakes

# Optimized for container size:
# RUN mvn compile -pl '!ctakes-distribution' -pl '!ctakes-temporal' -pl '!ctakes-dictionary-lookup-res' -pl '!ctakes-dependency-parser-res-clear' -pl '!ctakes-lvg-res' -DskipTests
# RUN mvn install -pl '!ctakes-distribution' -pl '!ctakes-temporal' -pl '!ctakes-dictionary-lookup-res' -pl '!ctakes-dependency-parser-res-clear' -pl '!ctakes-lvg-res' -DskipTests

# works on systems with prohibitions on downloading SNAPSHOT jars:
RUN mvn compile -pl '!ctakes-distribution' -DskipTests
RUN mvn install -pl '!ctakes-distribution' -DskipTests

FROM tomcat:9.0.70-jre8-temurin
COPY --from=0 /ctakes/ctakes-web-rest/target/ctakes-web-rest.war $CATALINA_HOME/webapps/
ENV CTAKES_HOME=/ctakes
CMD ["catalina.sh", "run"]