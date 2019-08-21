""" Helper functions for documents """

def ensure_aces(local_acl, aces):
    """ Ensures that base aces are in the local_acl """
    if local_acl is None:
        local_acl = []
    for ace in aces:
        if ace not in local_acl:
            local_acl.append(ace)
    return local_acl

def as_term_filter(query):
    filt = []
    for key in query:
        filt.append({"term":{key: query[key]}})
    return {"bool":{"filter": filt}}

