from collections import OrderedDict
from operator import itemgetter
from threading import Timer

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


def set_key(params):
    if (len(params) < 4 and len(params) != 2) or (len(params) > 2 and len(params) != 4):
        return "Incorrect parameters! Usage:\nSET key value [EX seconds]"

    if str(params[1]).strip() == "":
        return "Incorrect parameters! Usage:\nSET key value [EX seconds]"

    key = str(params[0])
    value = params[1]
    validity = 0
    if len(params) > 2:
        if str.upper(params[2]) != "EX":
            return "Incorrect parameters! Usage:\nSET key value [EX seconds]"
        if not params[3].replace('.', '', 1).isdigit():
            return "Incorrect parameters! Usage:\nSET key value [EX seconds]"
        validity = float(params[3])

    data[key] = Entry(key, value, validity)
    return "OK"


def get(params):
    if len(params) != 1:
        return "Incorrect parameters! Usage:\nGET key"

    key = str(params[0])
    if key not in data:
        return None

    entry = data[key]
    return entry.value


def delete(params):
    if len(params) < 1:
        return "Incorrect parameters! Usage:\nDEL key [key ...]"

    count = 0
    for key in params:
        if key in data:
            del data[key]
            count += 1

    return count


def db_size():
    return len(data.keys())


def incr(params):
    if len(params) != 1:
        return "Incorrect parameters! Usage:\nINCR key"

    key = params[0]
    if key not in data:
        data[key] = Entry(key, 0, 0)
        value = 0
    else:
        entry = data[key]
        value = entry.value

    if type(value) is str and not value.replace('.', '', 1).isdigit():
        return "This entry does not have a numeric value!"

    value = float(value)
    value += 1
    return value


def z_add(params):
    if len(params) < 3 or len(params[1::]) % 2 != 0:
        return "Incorrect parameters! Usage:\nZADD key score member [score member ...]"

    key = params[0]

    if key not in data:
        dictio = {params[pos+1]: params[pos] for pos in range(1, len(params)-1, 2)}
        data[key] = OrderedDict(sorted(dictio.items(), key=itemgetter(1, 0)))
        return len(data[key])

    if type(data[key]) is not OrderedDict:
        return "The typed key does not hold the type expected by this command!"

    sorted_dictionary = data[key]
    count = 0
    for pos in range(1, len(params)-1, 2):
        member = params[pos+1]
        score = params[pos]
        if member not in sorted_dictionary:
            count += 1
        sorted_dictionary[member] = score

    sorted_dictionary = OrderedDict(sorted(sorted_dictionary.items(), key=itemgetter(1, 0)))
    data[key] = sorted_dictionary
    return count


def z_card(params):
    if len(params) != 1:
        return "Incorrect parameters! Usage:\nZCARD key"

    key = params[0]
    if key not in data or type(data[key]) is not OrderedDict:
        return 0

    return len(data[key].values())


def z_rank(params):
    if len(params) != 2:
        return "Incorrect parameters! Usage:\nZRANK key member"

    key = params[0]
    member = params[1]
    if key not in data or member not in data[key]:
        return None

    sorted_dictionary = data[key]
    return list(sorted_dictionary.keys()).index(member)


def z_range(params):
    if len(params) != 3 or not params[1].replace("-", "", 1).isdigit() or not params[2].replace("-", "", 1).isdigit():
        return "Incorrect parameters! Usage:\nZRANGE key start stop"

    key = params[0]
    start = int(params[1])
    stop = int(params[2])
    if key not in data:
        return "Incorrect parameters! Usage:\nZRANGE key start stop"
    sorted_dictionary = data[key]
    size = len(sorted_dictionary)
    if (start > size - 1) or start > 0 > stop:
        return []

    if start < 0:
        start = size + start
    if stop < 0:
        stop = size + stop

    if start > stop:
        return []

    response = []
    keys = list(sorted_dictionary.keys())
    for pos in range(max(0, start), min(size, stop+1)):
        response.append(keys[pos])

    return response


def main():
    while True:
        args = input("Type a command: ")
        args = args.split(" ")
        command = str.upper(args[0])
        if command == "SET":
            print(set_key(args[1::]))
        elif command == "GET":
            print(get(args[1::]))
        elif command == "DEL":
            print(delete(args[1::]))
        elif command == "DBSIZE":
            print(db_size())
        elif command == "INCR":
            print(incr(args[1::]))
        elif command == "ZADD":
            print(z_add(args[1::]))
        elif command == "ZCARD":
            print(z_card(args[1::]))
        elif command == "ZRANK":
            print(z_rank(args[1::]))
        elif command == "ZRANGE":
            print(z_range(args[1::]))


if __name__ == '__main__':
    main()
