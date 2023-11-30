TAG=lore-tsr-container
DOCKERIGNORE=docker/dockerignore
DOCKERFILE=docker/Dockerfile
cp ${DOCKERIGNORE} .dockerignore
docker build -t ${TAG} -f ${DOCKERFILE} .
rm .dockerignore

