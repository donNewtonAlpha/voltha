. env.sh
make cli
#docker tag voltha-cli docker-repo.dev.atl.foundry.att.com:5000/voltha-cli:${1}
#docker push docker-repo.dev.atl.foundry.att.com:5000/voltha-cli:${1}

docker tag voltha-cli docker-repo.dev.atl.foundry.att.com:5000/voltha-cli:msz
docker push docker-repo.dev.atl.foundry.att.com:5000/voltha-cli:msz