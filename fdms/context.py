""" FDMS Context """
from fdms.services import TENANT_ACES
from pprint import pformat

class Context:

    def __init__(self, user):
        if user.get("tenant_id") == "*":
            user["is_fdms_admin"] = True
            user["is_tenant_admin"] = True
            self.acls = TENANT_ACES
        else:
            user["is_fdms_admin"] = False
            if user.get("is_tenant_admin"):
                user["is_tenant_admin"] = False
            else:
                user["is_tenant_admin"] = False
            #TODO: calculate ACLs
            self.acl = [ "group:admin"]

        self.user = user

    def __str__(self):
        return pformat(self.user)

    def is_fdms_admin(self):
        return self.user["is_fdms_admin"]

    def is_tenant_admin(self):
        return self.user["is_tenant_admin"]

    def getId(self):
        return self.user["user_id"]

