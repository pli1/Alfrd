import datetime
import pymongo
import config

_client = None
_db = None


def _get_db():
    global _client, _db
    if _db is None:
        _client = pymongo.MongoClient(config.MONGODB_URI)
        _db = _client.dev
    return _db


def _get_all(collection):
    return list(collection.find())


def _insert_status(weight, obj):
    _get_db().status.insert_one({
        "timestamp": datetime.datetime.now(),
        "weight": weight,
        "object": obj if isinstance(obj, list) else [obj],
    })


def _find_diff(list1, list2):
    return list(set(list1) - set(list2))


def _identify_change(all_status):
    last = all_status[-1]
    previous = all_status[-2]
    last_objs = last["object"]
    prev_objs = previous["object"]

    if len(last_objs) > len(prev_objs):
        added = _find_diff(last_objs, prev_objs)[0]
        weight = last["weight"] - previous["weight"]
        return ("Added", added, weight)
    elif len(last_objs) == len(prev_objs):
        return ("quantity changed", None, None)
    else:
        removed = _find_diff(prev_objs, last_objs)[0]
        weight = previous["weight"] - last["weight"]
        return ("Removed", removed, weight)


def _find_in_catalog(obj_name, catalog):
    for item in catalog:
        if item["object"] == obj_name:
            return item
    return None


def populate_3_tables(weight, obj):
    _insert_status(weight, obj)

    db = _get_db()
    all_status = _get_all(db.status)
    all_catalog = _get_all(db.catalog)

    if len(all_status) == 1:
        db.inventory.insert_one({"weight": weight, "object": obj[0]})
        db.catalog.insert_one({"object": obj[0], "max_weight_captured": weight, "inventory_level": 100})
        return

    change_type, this_obj, change_weight = _identify_change(all_status)

    if change_type == "Added":
        db.inventory.insert_one({"weight": change_weight, "object": this_obj})
        catalog_entry = _find_in_catalog(this_obj, all_catalog)
        if catalog_entry:
            max_w = catalog_entry["max_weight_captured"]
            if change_weight > max_w:
                db.catalog.update_one(
                    {"object": this_obj},
                    {"$set": {"max_weight_captured": change_weight, "inventory_level": 100}},
                )
            else:
                level = float(change_weight) / float(max_w) * 100
                db.catalog.update_one({"object": this_obj}, {"$set": {"inventory_level": level}})
        else:
            db.catalog.insert_one({"object": this_obj, "max_weight_captured": change_weight, "inventory_level": 100})

    elif change_type == "Removed":
        db.inventory.delete_one({"object": this_obj})
        db.catalog.update_one({"object": this_obj}, {"$set": {"inventory_level": 0}})
