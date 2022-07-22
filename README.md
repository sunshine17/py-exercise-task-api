# 1. Run with the manaul way(non-container)

## Start tha server

```shell
start-task.sh
```

# 2. Run with the docker way

## Build the image locally

docker build -t task-api .

## Run the container in port 5100

```shell
docker run --name task-api \
    -d -p 5100:5100 \
    task-api 
```

# 3. After the server is up, run some casual tests

## Get tasks

curl http://localhost:5100/tasks/

## Helper shell script for testing

```shell
./test-fun.sh
```

# 4. Using a shell script to interact with the server

``` shell

# Add a task
./tasks add "some title" 21/08/2019

# List all tasks
./tasks list

# List tasks expiring today
# tasks list --expiring-today


# Toggle task done
./tasks done 3
```

# 5. unittest

Here we use pytest for unit testing framework.

```shell
pipenv install
pipenv shell
pytest -v -l app
```
