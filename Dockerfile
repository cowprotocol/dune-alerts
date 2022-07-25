FROM python:alpine
RUN apk add --update gcc libc-dev linux-headers

WORKDIR /app

COPY requirements/* requirements/
RUN pip install -r requirements/prod.txt
COPY ./src ./src
COPY logging.conf .

ENTRYPOINT [ "python3", "-m" , "src.slackbot"]
