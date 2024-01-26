# nymea-docker

Docker files for running nymea in a docker container. By default most of the integration plugins are installed. If you want to change the list of plugins installed update the list in the [Dockerfile](Dockerfile) and rebuild the image using `docker-compose up -d --build`.  

# Install docker

Install the docker-ce and docker-compose from the official docker repository

https://docs.docker.com/engine/install/

# Run nymea docker container

In order to run nymea detached in the container you can start the server using:

    docker-compose up -d

You can check if the container is running or not using following command:

> Note: using the default table messes up the view due to the long port list, so we can format the table to have it readable

    docker ps --format "table {{.Image}}\t\t{{.Names}}\t{{.Command}}\t{{.State}}\t{{.Status}}\t{{.Size}}"

If you want to follow the debug output you can run

    docker logs -f nymead

If you want to stop the instace again you can run

    docker-compose stop

If you want shut down everything you can run

    docker-compose down

# Configurations

The configurations, settings and data files will be stored in the config folder of this repository.

# Limitations

> Note: if you have a solution in mind which might overcome these limitations please open an Issue or a PR and let us know. 

- The network discovery is not working properly. I have not found yet a way to reach the host LAN from the container by using ARP or Ping. I also tried `sudo sysctl -w net.ipv4.conf.all.proxy_arp=1` on the host running docker without success.
- Some UDP multicasts groups do not work since the container only sees the bridge network.
