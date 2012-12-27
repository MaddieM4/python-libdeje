# Basic well-formedness

MSG_NOT_DICT = {
    'code': 30,
    'explanation':"Recieved non-{} message, dropping",
}

MSG_NO_TYPE = {
    'code': 31,
    'explanation':"Recieved message with no type, dropping",
}

MSG_UNKNOWN_TYPE = {
    'code': 32,
    'explanation':"Recieved message with unknown type (%r)",
} 

# Locking errors

LOCK_HASH_NOT_RECOGNIZED = {
    'code': 40,
    'explanation': "Unknown lock quorum data, dropping (%s)",
}

# Permissions errors

PERMISSION_CANNOT_READ = {
    'code': 50,
    'explanation': "Permissions error: cannot read",
}

PERMISSION_CANNOT_WRITE = {
    'code': 51,
    'explanation': "Permissions error: cannot write",
}

# Checkpoint errors

# Subscription errors


