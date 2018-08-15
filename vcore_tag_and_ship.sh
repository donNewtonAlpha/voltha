. env.sh
make voltha
docker tag voltha-voltha docker-repo.dev.atl.foundry.att.com:5000/voltha-voltha:kafkatest_msz
docker push docker-repo.dev.atl.foundry.att.com:5000/voltha-voltha:kafkatest_msz
