FROM openjdk:latest

ARG FILE_NAME
ENV file_entry=$FILE_NAME
COPY . /usr/app/

WORKDIR /usr/app

ENTRYPOINT java -jar $file_entry