# pull official base image
FROM python:3.8.0-alpine

# set work directory to be the `Bank-DDD-CQRS-ES` directory
WORKDIR /home/max/software/projects/Bank-DDD-CQRS-ES

# expose the port we will listen on
EXPOSE $ACCOUNTS_PORT

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
# set the right path for the requirements.txt file
RUN pip install --upgrade pip
COPY requirements.txt ./
RUN apk update && \ 
    apk add postgresql-dev && \
    apk add --virtual build-deps gcc python-dev musl-dev libffi-dev make
RUN pip install --no-cache-dir -r requirements.txt

COPY . .