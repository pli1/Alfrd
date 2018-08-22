import pymongo
import datetime
connection_string="mongodb://pinjia-li:Lpj2423!@alfrddev-shard-00-00-bovbg.mongodb.net:27017,alfrddev-shard-00-01-bovbg.mongodb.net:27017,alfrddev-shard-00-02-bovbg.mongodb.net:27017/test?ssl=true&replicaSet=alfrddev-shard-0&authSource=admin"
client=pymongo.MongoClient(connection_string)
db=client.dev

def get_items_from_collection(collection):
    items=[]
    for item in collection.find():
        items.append(item)
    return items

def insert_status(weight,obj):
    now=datetime.datetime.now()
    if isinstance(obj,list):
        item={'timestamp':now,
              'weight':weight,
              'object':obj}
    else:
        item={'timestamp':now,
              'weight':weight,
              'object':[obj]}
    db.status.insert_one(item)
    return 0

def find_diff(list1,list2):
    return list(set(list1) - set(list2))

def identify_item_change(obj,all_status):
    last=len(all_status)-1
    previous=len(all_status)-2
    last_item=all_status[last]['object']
    previous_item=all_status[previous]['object']
    if len(last_item)>len(previous_item):
        #print "new item added"
        added=find_diff(last_item,previous_item)[0]
        weight=all_status[last]['weight']-all_status[previous]['weight']
        return ("Added",added,weight)
    elif len(last_item)==len(previous_item):
        #print "quanty changed"
        return ("quanty changed")
    else:
        #print "item removed"
        removed=find_diff(previous_item,last_item)[0]
        weight=all_status[previous]['weight']-all_status[last]['weight']
        return ("Removed",removed,weight)

def get_obj_in_list(this_obj,item_list):
    result_list=[]
    for each_item in item_list:
        if each_item['object']==this_obj:
            result_list.append(True)
            result_item=each_item
        else:
            result_list.append(False)
    if True in result_list:
        return (True,result_item)
    else:
        return (False,0)


def populate_3_tables(weight,obj):
    # Insert status anyway and figure out the inventory and catalog
    insert_status(weight,obj)
    #Get records from 3 tables
    all_status=get_items_from_collection(db.status)
    all_catalog=get_items_from_collection(db.catalog)
    all_inventory=get_items_from_collection(db.invenroty)
    
    # len(all_catalog)==0, initial item
    if len(all_status)==1:
        initial_item=True
    else:
        initial_item=False
    if initial_item:
        this_inventory={'weight':weight,'object':obj[0]}
        db.inventory.insert_one(this_inventory)
        this_catalog={'object':obj[0],'max_weight_captured':weight,'inventory_level':100}
        db.catalog.insert_one(this_catalog)
    #elif, not initial item, need to compare with previous
    else:
        item_change=identify_item_change(obj,all_status)
        change_status=item_change[0]
        this_obj=item_change[1]
        weight=item_change[2]
        # If New item got added, then check if this thing has been added before
        if change_status=="Added":
            # Insert inventory any way
            this_inventory={'weight':weight,'object':this_obj}
            db.inventory.insert_one(this_inventory)
            obj_in_catalog=get_obj_in_list(this_obj,all_catalog)
            # If this item has been added before, check the max_weight_captured and see if the catalog need to be updated 
            if obj_in_catalog[0]:
                max_weight=obj_in_catalog[1]['max_weight_captured']
                # If current weight is bigger, then inventory level should be 100% and max weight needs to be updated
                if weight>max_weight:
                    db.catalog.update_one({'object':this_obj},{'$set':{'max_weight_captured':weight,'inventory_level':100}})
                #Otherwise, current weight is smaller than the max weight, keep the catalog the same and calculate the inventory level
                else:
                    db.catalog.update_one({'object':this_obj},{'$set':{'inventory_level':float(weight)/float(max_weight)*100}})
            # If the item has not been added before, just add it to all 3 tables
            else:
                this_catalog={'object':this_obj,'max_weight_captured':weight,'inventory_level':100}
                db.catalog.insert_one(this_catalog)
        # If an item got removed 
        elif change_status=="Removed":
            db.inventory.delete_one({'object':this_obj})
            db.catalog.update_one({'object':this_obj},{'$set':{'inventory_level':0}})
        # Otherwise, nothing changed, do nothing
        else:
            print "quanty changed"