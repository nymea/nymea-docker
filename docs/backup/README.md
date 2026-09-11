# Backup and restore

Stop nymea before copying the entire data folder so databases and configuration are consistent. Substitute your configured host path and a new backup filename:

```sh
docker compose stop
sudo tar -C ./data -czf nymea-backup.tar.gz nymea cache
docker compose start
```

Restore into an **empty** folder, preserving ownership:

```sh
docker compose stop
sudo mkdir -p /srv/nymea-restored
sudo tar -C /srv/nymea-restored -xzf nymea-backup.tar.gz
# Set NYMEA_DATA_DIR=/srv/nymea-restored in .env.
docker compose up -d --force-recreate --wait --wait-timeout 120
```

Keep backups outside the checkout; they include user credentials and private certificates.
