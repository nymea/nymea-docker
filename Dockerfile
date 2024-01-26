FROM debian:12
LABEL maintainer "nymea GmbH <developer@nymea.io>"

# Environment
ENV DEBIAN_FRONTEND noninteractive
ENV LANGUAGE en_US
ENV TZ=Etc/UTC

# Add repository
RUN apt-get update
RUN apt-get install -y gnupg apt-utils wget tzdata
RUN echo "deb http://repository.nymea.io bookworm main non-free" > /etc/apt/sources.list.d/nymea.list
RUN echo "#deb http://repository.nymea.io/landing-silo bookworm main non-free" >> /etc/apt/sources.list.d/nymea.list
RUN echo "deb http://repository.nymea.io/experimental-silo bookworm main non-free" >> /etc/apt/sources.list.d/nymea.list
RUN wget -O /etc/apt/trusted.gpg.d/nymea.gpg https://repository.nymea.io/nymea.gpg
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install packages
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y tzdata avahi-daemon

# Install nymea packages
RUN apt-get install -y --no-install-recommends \
nymea \
nymea-data \
nymea-system-plugin-systemd \
nymea-zeroconf-plugin-avahi \
nymea-apikeysprovider-plugin-community

# Install nymea plugins
# List all plugins: apt-cache search --names-only nymea-plugin-* | grep -v -e -dbgsym | cut -f1 -d ' '
RUN apt-get install -y \
nymea-plugin-alphainnotec \
nymea-plugin-amperfied \
nymea-plugin-anel \
nymea-plugin-aqi \
nymea-plugin-avahimonitor \
nymea-plugin-awattar \
nymea-plugin-bgetech \
nymea-plugin-bluos \
nymea-plugin-bose \
nymea-plugin-bosswerk \
nymea-plugin-coinmarketcap \
nymea-plugin-daikinairco \
nymea-plugin-datetime \
nymea-plugin-daylightsensor \
nymea-plugin-denon \
nymea-plugin-doorbird \
nymea-plugin-drexelundweiss \
nymea-plugin-dweetio \
nymea-plugin-easee \
nymea-plugin-elgato \
nymea-plugin-eq-3 \
nymea-plugin-evbox \
nymea-plugin-fastcom \
nymea-plugin-flowercare \
nymea-plugin-fronius \
nymea-plugin-garadget \
nymea-plugin-generic-buttons \
nymea-plugin-generic-energy \
nymea-plugin-generic-garages \
nymea-plugin-generic-heatingcooling \
nymea-plugin-generic-irrigation \
nymea-plugin-generic-lights \
nymea-plugin-generic-sensors \
nymea-plugin-generic-shading \
nymea-plugin-generic-thing \
nymea-plugin-goecharger \
nymea-plugin-harmankardon \
nymea-plugin-homeconnect \
nymea-plugin-httpcommander \
nymea-plugin-huawei \
nymea-plugin-idm \
nymea-plugin-inepro \
nymea-plugin-keba \
nymea-plugin-kodi \
nymea-plugin-kostal \
nymea-plugin-lifx \
nymea-plugin-mailnotification \
nymea-plugin-mecelectronics \
nymea-plugin-mennekes \
nymea-plugin-meross \
nymea-plugin-modbuscommander \
nymea-plugin-mqttclient \
nymea-plugin-mtec \
nymea-plugin-mypv \
nymea-plugin-mystrom \
nymea-plugin-nanoleaf \
nymea-plugin-netatmo \
nymea-plugin-networkdetector \
nymea-plugin-notifyevents \
nymea-plugin-nuki \
nymea-plugin-openuv \
nymea-plugin-openweathermap \
nymea-plugin-philipshue \
nymea-plugin-phoenixconnect \
nymea-plugin-powerfox \
nymea-plugin-pushbullet \
nymea-plugin-pushnotifications \
nymea-plugin-reversessh \
nymea-plugin-schrack \
nymea-plugin-senic \
nymea-plugin-sennheiser \
nymea-plugin-serialportcommander \
nymea-plugin-shelly \
nymea-plugin-sma \
nymea-plugin-solarlog \
nymea-plugin-solax \
nymea-plugin-somfytahoma \
nymea-plugin-sonos \
nymea-plugin-spothinta \
nymea-plugin-stiebeleltron \
nymea-plugin-sunspec \
nymea-plugin-systemmonitor \
nymea-plugin-tado \
nymea-plugin-tasmota \
nymea-plugin-tcpcommander \
nymea-plugin-telegram \
nymea-plugin-tempo \
nymea-plugin-texasinstruments \
nymea-plugin-tmate \
nymea-plugin-tplink \
nymea-plugin-tplink \
nymea-plugin-tuya \
nymea-plugin-udpcommander \
nymea-plugin-unifi \
nymea-plugin-unipi2 \
nymea-plugin-usbrelay \
nymea-plugin-usbrly82 \
nymea-plugin-vestel \
nymea-plugin-wakeonlan \
nymea-plugin-wattsonic \
nymea-plugin-webasto \
nymea-plugin-wemo \
nymea-plugin-wheretheissat \
nymea-plugin-ws2812fx \
nymea-plugin-yamahaavr \
nymea-plugins-zigbee \
nymea-plugins-zwave 

RUN echo '#!/bin/bash -e' > /bin/docker-entrypoint.sh && \
    echo '' >> /bin/docker-entrypoint.sh && \
    echo '/usr/bin/nymead -n -d Application -d Server -d Platform' >> /bin/docker-entrypoint.sh

RUN chmod +x /bin/docker-entrypoint.sh

ENTRYPOINT ["/bin/docker-entrypoint.sh"]
