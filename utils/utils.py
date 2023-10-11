def tuple_to_str(key):
    return ",".join(str(i) for i in key)


def str_to_tuple(key_str):
    return tuple(key_str.split(","))
