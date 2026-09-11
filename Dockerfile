FROM debian:trixie-slim

LABEL org.opencontainers.image.title="nymea" \
      org.opencontainers.image.description="nymea with LAN discovery and host-persisted settings"

ENV TZ=Etc/UTC

# Prevent Debian package scripts from starting services during the build.
RUN printf '#!/bin/sh\nexit 101\n' > /usr/sbin/policy-rc.d \
    && chmod +x /usr/sbin/policy-rc.d \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       ca-certificates curl tzdata \
    && curl --fail --show-error --silent --location \
       https://repository.nymea.io/repository.gpg -o /usr/share/keyrings/nymea.gpg \
    && printf 'deb [signed-by=/usr/share/keyrings/nymea.gpg] https://repository.nymea.io trixie main non-free\n' \
       > /etc/apt/sources.list.d/nymea.list \
    && rm -rf /var/lib/apt/lists/*

COPY packages.txt /usr/share/nymea-container/packages.txt
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       nymead nymea-data nymea-zeroconf-plugin-avahi \
       nymea-apikeysprovider-plugin-community nymea-cli dbus avahi-daemon supervisor \
    && xargs -r -a /usr/share/nymea-container/packages.txt \
       env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    # Drop nymead's NET_ADMIN file capability (outside Docker's default bounding set) so exec succeeds; see README's Networking section.
    && setcap -r /usr/bin/nymead \
    && dpkg-query -W > /usr/share/nymea-container/installed-packages.txt \
    && rm -rf /var/lib/apt/lists/* \
    && rm -f /etc/machine-id /var/lib/dbus/machine-id \
    && rm -f /usr/sbin/policy-rc.d

COPY container/ /usr/local/lib/nymea-container/
RUN chmod +x /usr/local/lib/nymea-container/*.py /usr/local/lib/nymea-container/entrypoint.sh

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD ["/usr/local/lib/nymea-container/healthcheck.py"]

ENTRYPOINT ["/usr/local/lib/nymea-container/entrypoint.sh"]
