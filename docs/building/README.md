# Building and publishing

## Building locally

```sh
docker compose build
```

This builds the image tagged `nymea-local:trixie` (see `docker-compose.yml`), for the local host architecture only. Use this while developing, and validate with the [health check and smoke test](../health/README.md#smoke-test) before publishing.

## Publishing to Docker Hub

Images are published to the `nymea` organization on Docker Hub as [`nymea/nymea`](https://hub.docker.com/r/nymea/nymea). An older image already lives there under that same repository — publishing a new release adds tags to it rather than creating a new repository.

Tag each release with the nymea daemon version it bundles, plus a floating `latest` tag. `packages.txt`/the Dockerfile don't pin an exact nymea version — they always pull whatever is currently in the stable Trixie repository — so after building, confirm the version actually bundled via `/usr/share/nymea-container/installed-packages.txt` inside the image before deciding the tag. This release is **1.16.0**.

### One-time setup

- `docker login` with an account that has push access to the `nymea` organization on Docker Hub.
- A `buildx` builder that supports multi-platform output (recent Docker Engine versions ship one by default; check with `docker buildx ls`, or create one explicitly):

  ```sh
  docker buildx create --name nymea-container-builder --use --bootstrap
  ```

### Build and push a release

Multi-arch images can't be built with `--load` into the local Docker daemon — build and push in one step directly to Docker Hub:

```sh
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag nymea/nymea:1.16.0 \
  --tag nymea/nymea:latest \
  --push \
  .
```

Pushing `latest` moves that tag from whatever the old container currently points to onto this build — anyone pulling `nymea/nymea:latest` gets the new image on their next pull. The previous version's own tag (if it was pushed with one) stays in place on Docker Hub, so users pinned to it are unaffected.

Verify both platforms were published:

```sh
docker buildx imagetools inspect nymea/nymea:1.16.0
```

### Before publishing

Always validate a release build before pushing:

1. Build for the local architecture only: `docker compose build`.
2. Run the [smoke test](../health/README.md#smoke-test): `python3 tests/smoke.py`.
3. Do a manual LAN acceptance pass with nymea:app (see [Health and validation](../health/README.md#lan-acceptance-testing)).

Record the image ID and keep a data backup before rolling a production host onto a new tag — see [Backup and restore](../backup/README.md).
