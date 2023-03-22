# Maintainer notes

## Publishing to Dockerhub

In order to deploy to dockerhub, first make sure your local docker client has been authed with an account that has permissions to publish to the docker organization (in our case, this is `smartonfhir`)

The following buildx command will update the containers published on dockerhub (update the major/minor/patch versions as appropriate):
```bash
export MAJOR=1
export MINOR=0
export PATCH=0
export PLATFORMS=linux/amd64,linux/arm/v8,linux/arm/v7,linux/arm64

docker buildx build \
--push --platform $PLATFORMS \
--tag smartonfhir/ctakes-covid:$MAJOR.$MINOR.$PATCH .
```

Once you've tested the image, you can copy the tag of this release to the coarser grained tags with the following commands:
```bash
docker tag martonfhir/ctakes-covid:$MAJOR.$MINOR.$PATCH smartonfhir/ctakes-covid:$MAJOR.$MINOR
docker tag martonfhir/ctakes-covid:$MAJOR.$MINOR.$PATCH smartonfhir/ctakes-covid:$MAJOR
docker tag martonfhir/ctakes-covid:$MAJOR.$MINOR.$PATCH smartonfhir/ctakes-covid:latest
```