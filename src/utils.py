def batch(list, batch_size):
    list_size = len(list)
    batch_size = batch_size if batch_size > 0 else list_size
    pages_total = int(list_size / batch_size)
    for page_index, offset in enumerate(range(0, list_size, batch_size)):
        page = page_index + 1
        yield (list[offset:min(offset + batch_size, list_size)], page, pages_total)