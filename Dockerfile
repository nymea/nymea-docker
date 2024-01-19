FROM debian:12
LABEL maintainer "nymea GmbH <developer@nymea.io>"

# Environment
ENV DEBIAN_FRONTEND noninteractive
ENV LANGUAGE en_US

# Add repository
RUN apt-get update
RUN apt-get install -y gnupg apt-utils wget
RUN echo "deb http://repository.nymea.io bookworm main non-free" > /etc/apt/sources.list.d/nymea.list
RUN echo "#deb repository.nymea.io/landing-silo bookworm main non-free" >> /etc/apt/sources.list.d/nymea.list
RUN echo "#deb repository.nymea.io/experimental-silo bookworm main non-free" >> /etc/apt/sources.list.d/nymea.list
RUN wget -O /etc/apt/trusted.gpg.d/nymea.gpg https://repository.nymea.io/nymea.gpg

RUN mkdir -p /etc/nymea/
COPY nymead.conf /etc/nymea/nymead.conf

# Install packages
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y nymea nymea-plugin-networkdetector avahi-daemon

RUN echo '#!/bin/bash -e' > /bin/docker-entrypoint.sh && \
    echo '' >> /bin/docker-entrypoint.sh && \
    echo 'ip addr' && \
    echo '/usr/bin/nymead -n -d Application -d LogEngine' >> /bin/docker-entrypoint.sh && \
    echo 'sleep infinity' >> /bin/docker-entrypoint.sh

RUN chmod +x /bin/docker-entrypoint.sh

ENTRYPOINT ["/bin/docker-entrypoint.sh"]
