echo "" > /root/.ssh/known_hosts
. env.sh
docker-compose -f compose/docker-compose-system-test.yml down
docker-compose -f compose/docker-compose-auth-test.yml down
docker-compose -f compose/docker-compose-system-test.yml up -d
docker-compose -f compose/docker-compose-auth-test.yml up -d