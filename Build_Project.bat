docker pull openapitools/openapi-generator-cli

docker run --rm -v ${PWD}:/local openapitools/openapi-generator-cli generate -i /local/open-api.yaml -g python-fastapi -o /local/backend

docker compose build
docker compose up