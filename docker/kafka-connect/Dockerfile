# pull official base image
FROM confluentinc/cp-kafka-connect:latest

COPY ./docker/kafka-connect/connectors /kafka/plugins
COPY ./docker/kafka-connect/init-connectors.sh /kafka/init-connectors.sh
