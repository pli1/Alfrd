import pymongo
connection_string="mongodb://pinjia-li:Lpj2423!@alfrddev-shard-00-00-bovbg.mongodb.net:27017,alfrddev-shard-00-01-bovbg.mongodb.net:27017,alfrddev-shard-00-02-bovbg.mongodb.net:27017/test?ssl=true&replicaSet=alfrddev-shard-0&authSource=admin"
client=pymongo.MongoClient(connection_string)
db=client.test
#db.my_collection.insert_one({'test':000}).inserted_id