def batch(list, batch_size):
    list_size = len(list)
    for idx in range(0, list_size, batch_size):
        yield list[idx:min(idx + batch_size, list_size)]