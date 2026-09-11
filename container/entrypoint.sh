#!/bin/sh
set -eu

if [ ! -f "/usr/share/zoneinfo/$TZ" ]; then
    echo "Unknown timezone: $TZ" >&2
    exit 1
fi
ln -snf "/usr/share/zoneinfo/$TZ" /etc/localtime
printf '%s\n' "$TZ" > /etc/timezone
mkdir -p /run/dbus /run/avahi-daemon /var/lib/nymea /var/cache/nymea
dbus-uuidgen --ensure=/run/machine-id
ln -snf /run/machine-id /etc/machine-id
exec /usr/bin/supervisord -c /usr/local/lib/nymea-container/supervisord.conf
