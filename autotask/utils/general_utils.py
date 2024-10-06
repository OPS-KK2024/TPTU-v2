

def find_stop_in_message(stop, message):
    if stop is not None:
        stop_idxs = []
        for s in stop:
            if message.find(s) >= 0:
                stop_idxs.append(message.find(s))
        if len(stop_idxs) == 0:
            stop_idx = len(message)
        else:
            stop_idx = min(stop_idxs)
    else:
        stop_idx = len(message)
    
    return stop_idx