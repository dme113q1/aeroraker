FROM ubuntu:17.04
RUN apt-get update && apt-get install -y \
    python3-tornado \
    protobuf-compiler \
    python3-protobuf \
    git
RUN apt-get clean

ENV PROJECT_HOME /home/project

RUN git clone https://github.com/dme113q1/aeroraker.git ${PROJECT_HOME}
RUN protoc --python_out=${PROJECT_HOME}/fetcher --proto_path=${PROJECT_HOME}/protobuf ${PROJECT_HOME}/protobuf/messages.proto

RUN useradd --create-home user1
USER user1
WORKDIR ${PROJECT_HOME}/fetcher
CMD ["python3", "server.py"]
