FROM python:3.7-slim-buster

WORKDIR batchjob
# Download the ModelOp Center CLI
RUN apt-get update
RUN apt-get install curl -y
RUN curl -o moc https://modelop-go-cli.s3.us-east-2.amazonaws.com/release/latest/linux/moc
RUN chmod +x moc

# App code
COPY src .

# Python requirements
COPY requirements.txt .
RUN pip3 install -r requirements.txt
