def id_provider(start: int = 0):
    current_id = start

    def _next_id():
        nonlocal current_id
        next_id = current_id
        current_id = current_id + 1
        return next_id

    return _next_id
