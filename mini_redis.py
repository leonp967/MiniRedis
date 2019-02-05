import json
from collections import OrderedDict
from operator import itemgetter
from threading import Timer
from constants import INTERVAL_WRITE, PATH_FILE

data = {}


class Entry:
    def __init__(self, key, value, validity):
        self.key = key
        self.value = value
        self.validity = validity
        if validity > 0:
            self.timer = Timer(validity, self.delete)
            self.timer.start()

    def delete(self):
        del data[self.key]


def set_key(key, value, seconds):
    value = value.replace(" ", "")
    if value == "":
        return "The value cannot be empty!"

    if seconds is not None:
        data[key] = Entry(key, value, seconds)
    else:
        data[key] = Entry(key, value, 0)

    return "OK"


def get(key):
    if key not in data:
        return None

    entry = data[key]
    if type(entry) is Entry:
        return entry.value
    else:
        return "The key holds an invalid value!"


def delete(key, keys):
    count = 0
    if key in data:
        del data[key]
        count += 1

    if keys is not None and keys != "":
        array = keys.replace(" ", "").split(",")
        for key in array:
            if key in data:
                del data[key]
                count += 1

    return count


def db_size():
    return len(data.keys())


def incr(key):
    if key not in data:
        data[key] = Entry(key, 0, 0)
        entry = data[key]
        value = 0
    else:
        entry = data[key]
        if type(entry) is not Entry:
            return "This key does not hold a valid value!"
        value = entry.value
        if type(value) is not str or not value.replace('.', '', 1).isdigit():
            return "This entry does not have a numeric value!"

    value = float(value)
    value += 1
    data[key] = Entry(key, value, entry.validity)
    return value


def z_add(key, members, scores):
    members = members.replace(" ", "")
    scores = scores.replace(" ", "")
    if members == "" or scores == "":
        return "You must type at least one member and one score!"

    members = members.split(",")
    scores = scores.split(",")

    if len(members) != len(scores):
        return "The members list must have the same length as the scores list!"

    if not all(score.replace('.', '', 1).isdigit() for score in scores):
        return "The scores list must contain only numbers!"

    if key not in data:
        dictio = {members[pos]: scores[pos] for pos in range(len(members))}
        data[key] = OrderedDict(sorted(dictio.items(), key=itemgetter(1, 0)))
        return len(data[key])

    if type(data[key]) is not OrderedDict:
        return "The typed key does not hold the type expected by this command!"

    sorted_dictionary = data[key]
    count = 0
    for pos in range(len(members)):
        member = members[pos]
        score = scores[pos]
        if member not in sorted_dictionary:
            count += 1
        sorted_dictionary[member] = score

    sorted_dictionary = OrderedDict(sorted(sorted_dictionary.items(), key=itemgetter(1, 0)))
    data[key] = sorted_dictionary
    return count


def z_card(key):
    if key not in data or type(data[key]) is not OrderedDict:
        return 0

    return len(data[key].values())


def z_rank(key, member):
    if member is None or member == "":
        return "Incorrect parameters! Usage:\nZRANK key member"

    if key not in data or member not in data[key]:
        return None

    sorted_dictionary = data[key]
    return list(sorted_dictionary.keys()).index(member)


def z_range(key, start, stop):
    if key not in data:
        return "The specified key does not exist!"
    sorted_dictionary = data[key]
    size = len(sorted_dictionary)
    if (start > size - 1) or start > 0 > stop:
        return ""

    if start < 0:
        start = size + start
    if stop < 0:
        stop = size + stop

    if start > stop:
        return ""

    response = []
    keys = list(sorted_dictionary.keys())
    for pos in range(max(0, start), min(size, stop+1)):
        response.append(keys[pos])

    return ' '.join(member for member in response)


def dict_to_obj(our_dict):
    if "__class__" in our_dict:
        class_name = our_dict.pop("__class__")
        module_name = our_dict.pop("__module__")
        module = __import__(module_name)
        class_ = getattr(module, class_name)
        obj = class_(**our_dict)
    else:
        obj = our_dict
    return obj


def convert_to_dict(obj):
    obj_dict = {
        "__class__": obj.__class__.__name__,
        "__module__": obj.__module__
    }

    obj_dict.update(obj.__dict__)
    return obj_dict


def write_in_disk():
    data_json = json.dumps(data, default=convert_to_dict, indent=4, sort_keys=True)
    file = open(PATH_FILE, 'w')
    file.write(data_json)
    file.close()
    Timer(INTERVAL_WRITE, write_in_disk).start()


try:
    file = open(PATH_FILE, 'r')
    data_json = file.read()
    data = json.loads(data_json, object_hook=dict_to_obj)
    Timer(INTERVAL_WRITE, write_in_disk).start()
except FileNotFoundError:
    Timer(INTERVAL_WRITE, write_in_disk).start()
