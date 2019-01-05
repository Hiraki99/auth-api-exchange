from itsdangerous import URLSafeTimedSerializer
import os
def obj_to_dict(item, force=False):
    """[Convert from class to Dict(). The idea is the same as bean in java]

    Arguments:
        item {[class]} -- [any type of class have __dict__ readable]

    Returns:
        [dict] -- [contain all method self.* of class]
    """
    obj = dict()
    for key in item.__dict__.keys():
        try:
            if isinstance(item.__getattribute__(key), str) or isinstance(item.__getattribute__(key), int) or isinstance(item.__getattribute__(key), float) or isinstance(item.__getattribute__(key), dict) or isinstance(item.__getattribute__(key), list):
                obj[key] = item.__getattribute__(key)
            elif item.__getattribute__(key) is None:
                obj[key] = None
            elif force:
                obj[key] = str(item.__getattribute__(key))
        except:
            continue
    return obj
def getFullAttr(row):
    data = obj_to_dict(row)
    data["createAt"] = row.createAt
    data["updateAt"] = row.updateAt
    return data

def get_key(path):
    """get text in file"""
    with open(path, 'r') as myfile:
        data = myfile.read()
        return data
def checkBlacklist(array, token):
    for val in array:
        if(token == val):
            return True
    return False

def saveListImage(listimage,folder,username):
    list_name = []
    list_prefix = ["_front.jpg","_selfie.jpg","_with_exchange.jpg","_alternative.jpg"]
    for i in range(0, len(listimage)):
        listimage[i].save(os.path.join(folder,username+list_prefix[i]))
        list_name.append(os.path.join(folder,username+list_prefix[i]).replace("/AuthAPI/static",""))
    return list_name
