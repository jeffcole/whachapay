def get_client_ip(meta):
    """
    !!! FIX: Make client IP tracking more robust. See WikiP link here:
    http://stackoverflow.com/questions/4581789/how-do-i-get-user-ip-address-in-django
    """
    xff = meta.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0]
    else:
        return meta.get('REMOTE_ADDR')

def get_dict(seq, attr, value):
    """Get a dictionary in a sequence according to an attribute value."""
    for d in seq:
        if d[attr] == value:
            return d
    return None

def get_unicode(*items):
    """Get a space-separated unicode string from the given items."""
    return u' '.join(map(unicode, items))
