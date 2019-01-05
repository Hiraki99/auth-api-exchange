from AuthAPI import main
from AuthAPI import celery

from AuthAPI.initdb import db_session
from AuthAPI.model.permission import Permission
from AuthAPI.model.role import Role
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i","--init", help="fully automatized upgrade", action="store_true",default=None)

def initData():
    list_role = ["trader","guest", "admin"]
    with db_session() as session:
        for role in list_role:
            new_role = Role(role, "Role for %s account"%role)
            session.add(new_role)
            session.flush()
            new_permission = Permission(new_role.id, role)
            session.add(new_permission)

if __name__ == "__main__":
    results = parser.parse_args()

    if(results.init is not None):
        initData()
    else:
        main()
