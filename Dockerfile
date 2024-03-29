# Using lightweight alpine image
FROM python:3.7-alpine

# Installing packages
RUN apk update
RUN pip install --no-cache-dir pipenv

# Defining working directory and adding source code
WORKDIR /usr/src/app
COPY Pipfile Pipfile.lock start-task.sh ./
COPY app ./app 

# Install API dependencies
RUN pipenv install

# Start app
EXPOSE 5100
ENTRYPOINT ["/usr/src/app/start-task.sh"]
