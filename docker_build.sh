docker build -f docker/Dockerfile.NonogramServer -t nonogram_server .
docker build -f docker/Dockerfile.ApiServer -t api_server .
docker image prune -f