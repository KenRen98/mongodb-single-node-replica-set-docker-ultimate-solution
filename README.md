# MongoDB Docker Single Node ReplicaSet
This is a simple guide to set up the mongodb docker compose with only one node inside the replica set to enable the ACID transaction function.

## 1.Setup
### w/ Auth
When you have username and password set for the mongodb service, the instance will be asking for a keyfile that used for replica set internal connection (NOT the client/code/server connection to the DB). The key is a 756 byte random value in base64 format and stored in a plain text file. I have attached a simple python script to generate the keyfile for you. Simply run the script and copy the output to a file name it to `replica.key` in the same directory.

```cmd
python3 generate-key.py
```

The following is the example of the docker-compose file with the keyfile setup.

```yaml
  mongodb:
    image: mongo:latest
    ports: 
      - "27017:27017"
    healthcheck:
      test: echo "try { rs.status() } catch (err) { rs.initiate({_id:'rs01',members:[{_id:0,host:'mongodb:27017'}]}) }" | mongosh "mongodb://<username>:<password>@mongodb:27017" --authenticationDatabase admin --quiet
      interval: 5s
      timeout: 30s
      start_period: 0s
      start_interval: 1s
      retries: 3
    volumes:
      - ./dockervolumes/mongodb:/data/db
      - ./dockervolumes/replica.key:/data/replica.key
    environment:
      MONGO_INITDB_ROOT_USERNAME: <username>
      MONGO_INITDB_ROOT_PASSWORD: <password>
    entrypoint:
      - bash
      - -c
      - |
          chmod 400 /data/replica.key
          chown 999:999 /data/replica.key
          exec docker-entrypoint.sh $$@ 
    command: "mongod --bind_ip_all --replSet rs01 --keyFile /data/replica.key"
```
I will explain each part of the docker-compose file.
- `healthcheck`: This health check is a very stupid way to initiate the replica set if it is not initiated. It will try to get the replica set status, if it fails, it will initiate the replica set with the name `rs01` and the host `mongodb:27017`. This is a very stupid way to do it, but it works. Otherwise you have to manually initiate the replica set. This essentially automates the process without needing you to manually enter the mongo shell to initiate the replica set. The downside is that it will always try to initiate the replica set every time the container restarts. and keep connecting to the mongo shell. But it works with no performance impact. **This method is thanks to [this post](https://anthonysimmon.com/the-only-local-mongodb-replica-set-with-docker-compose-guide-youll-ever-need/).**
- `volumes`: The volume is mounted to the host machine to store the database data and the keyfile. The keyfile is mounted to the `/data/replica.key` in the container. You could try :ro to make it read-only. But it depends on where you put the file and what OS you are using. The mongodb may not be able load the keyfile since the permission copied into the container MIGHT not be correct.
- `environment`: The username and password for the root user. This is the username and password for the database connection. NOT the replica set connection. Once you set this, the keyfile is mandatory.
- `entrypoint`: This is a workaround to set the permission for the keyfile. The keyfile must be set to 400 permission and owned by the mongodb user. The entrypoint will set the permission and the owner of the keyfile before executing the original entrypoint. The `$$@` is the original entrypoint command. **Thanks to [rrriki's issue here](https://github.com/docker-library/mongo/issues/475#issuecomment-845317707)**. You can try to remove this, but it breaks on some OS and some folder permission settings. It is better to have it than not. It wont affect anything.

### w/o Auth
As I have stated above, the keyfile is only required when you have the username and password set for the mongodb service. If you don't have the username and password set, you can simply remove the keyfile part from the docker-compose file, as well as the entrypoint workaround.

```yaml
  mongodb:
    image: mongo:latest
    ports: 
      - "27017:27017"
    healthcheck:
      test: echo "try { rs.status() } catch (err) { rs.initiate({_id:'rs01',members:[{_id:0,host:'mongodb:27017'}]}) }" | mongosh "mongodb://mongodb:27017" --quiet
      interval: 5s
      timeout: 30s
      start_period: 0s
      start_interval: 1s
      retries: 3
    volumes:
      - ./dockervolumes/mongodb:/data/db
    command: "mongod --bind_ip_all --replSet rs01"
```

## 2. Connect
- The connection string for the replica set is `mongodb://<username>:<password>@<host>:<port>,<host>:<port>,<host>:<port>/<database>?replicaSet=rs01&authSource=admin`. The `authSource` is the database that the user is stored. The `replicaSet` is the name of the replica set. The `<host>:<port>` is the host and port of the mongodb instance. You can add more host and port to the connection string if you have more than one node in the replica set.`<username>:<password>@` is optional, if you don't have the username and password set, you can remove it from the connection string.
- The host must be whatever you set in `{ rs.initiate({_id:'rs01',members:[{_id:0,host:'mongodb:27017'}]}) }` in the healthcheck command. I.E. `mongodb` would be the host in the connection string. You can modify the host file in your OS to point `mongodb` to 127.0.0.1 and this is **MANDATORY**. Otherwise the mongodb instance will give you a host not found error.
- When you have replica set on, the create database will requrie a collection inside, which is normal. Unless you use mongosh `use <database>` to create the database. Anyway it will not show up in the `show dbs` command, until you have a collection inside. But dont worry, using code to connect to the database will create the database if it is not exist. So your code will not break and need no modification.

## 3. Star this repo
**If you find this repo helpful, please give it a star. If there are any other issues, please open an issue. I will try to help you as much as I can.**