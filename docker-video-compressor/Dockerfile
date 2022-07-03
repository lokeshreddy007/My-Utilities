FROM ubuntu:18.04
LABEL maintainer="lokeshreddy007"
RUN apt-get update \
    && apt-get install -y software-properties-common \
    && apt-get update \
    && apt-get upgrade -y \
    && apt install python -y \
    && apt-get install -y \
        handbrake-cli
ADD handbrake.py .
ADD preset.json .

CMD ["python3", "handbrake.py"]