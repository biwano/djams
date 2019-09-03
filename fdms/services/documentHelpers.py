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
        filt.append({"term": {key: query[key]}})
    return {"bool": {"filter": filt}}


def path(*args):
    def sanitize(arg):
        if type(arg) == list:
            arg = path(*arg)
        if arg.startswith("/"):
            arg = arg[1:]
        if arg.endswith("/"):
            arg = arg[-1:]
        return arg
    print("---")
    print(args)
    args = [sanitize(arg) for arg in args]
    print(args)
    args = list(filter(lambda arg: len(arg) > 0, args))
    print(args)
    print("---")
    return "/{}".format("/".join(args))


def parent_path(doc_path):
    paths = doc_path.split("/")
    paths = paths[:-1]
    return path(paths)
