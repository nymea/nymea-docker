# nymea-docker

Docker files for running nymea in a docker container.

# Install docker

Install the docker-ce and docker-compose from the official docker repository

https://docs.docker.com/engine/install/

# Run nymea docker container

In order to run nymea detached in the container you can start the server using:

    docker-compose up -d

You can check if the container is running or not using following command:

> Note: using the default table messes up the view due to the long port list, so we can format the table to have it readable

    docker ps --format "table {{.Image}}\t\t{{.Names}}\t{{.Command}}\t{{.State}}\t{{.Status}}"

If you want to follow the debug output you can run

    docker logs -f nymead

If you want to stop the instace again you can run

    docker-compose down

# Configurations

The configurations, settings and data files will be stored in the config folder of this repository.
