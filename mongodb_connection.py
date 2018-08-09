import pymongo
import datetime
now=datetime.datetime.now()
connection_string="mongodb://pinjia-li:Lpj2423!@alfrddev-shard-00-00-bovbg.mongodb.net:27017,alfrddev-shard-00-01-bovbg.mongodb.net:27017,alfrddev-shard-00-02-bovbg.mongodb.net:27017/test?ssl=true&replicaSet=alfrddev-shard-0&authSource=admin"
client=pymongo.MongoClient(connection_string)
db=client.dev
def insert_status(weight,obj):
    if isinstance(obj,list):
        item={'timestamp':now,
              'weight':weight,
              'object':obj}
    else:
        item={'timestamp':now,
              'weight':weight,
              'object':[obj]}
    db.status.insert(item)
    return 0

def get_all_status():
    items=[]
    for each_document in db.status.find():
        items.append(each_document)
    return items

def find_diff(list1,list2):
    return list(set(list1) - set(list2))

def get_item_change(item_list):
    last=len(item_list)-1
    previous=len(item_list)-2
    last_item=item_list[last]['object']
    previous_item=item_list[previous]['object']
    if len(last_item)>len(previous_item):
        print "new item added"
        added=find_diff(last_item,previous_item)
        weight=item_list[last]['weight']-item_list[previous]['weight']
        item={'weight':weight,
              'object':added}
        db.inventory.insert(item)
    elif len(last_item)==len(previous_item):
        print "quanty changed"
    else:
        print "item removed"
        removed=find_diff(previous_item,last_item)
        weight=item_list[previous]['weight']-item_list[last]['weight']
        db.inventory.deleteOne({'object':removed})
    return 0 
        



    