docker run --name redis -p 6379:6379 -v /host/dir:/data -d redis redis-server --appendonly yes
docker run --name mongo -p 27018:27017 -v /my/own/datadir:/data/db -d mongo --auth
docker exec -it mongo mongo admin
db.createUser({ user: 'shikanon', pwd: 'shikanon', roles: [ { role: "userAdminAnyDatabase", db: "admin" } ] });


docker run -e ARANGO_RANDOM_ROOT_PASSWORD=1 -p 8529:8529 --name arangodb -d arangodb