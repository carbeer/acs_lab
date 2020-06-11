import sys
import json

# Checks whether role inherits one of the targets according to hierarchy
def is_inheriting(role: str, targets: list, hierarchy: dict) -> bool:
    visited = {role: True}
    cands = [role]

    while len(cands) != 0:
        cand = cands.pop()
        for t in targets:
            if t in hierarchy[cand]: 
                return True     

        for el in hierarchy[cand]:
            if el not in visited:
                visited[el] = True
                cands.append(el)
    return False

# Returns list of roles that a user possesses
def get_roles(usr: str, role_ass: str) -> list:
    if usr in role_ass:
        return role_ass[usr]
    else: 
        return []

# Returns roles that are allowed to access the given resource
def get_targets(res: str, perm_ass: str) -> list:
    for r in perm_ass:
        if r["name"] == res: 
            return r["pa"]
    raise Exception(f"resource {res} does not exist")

# Returns boolean, indicating whether a user has the permission to access the object
def has_permission(usr: str, res: str, perms: dict) -> bool:
    roles = get_roles(usr, perms["roleassignment"])
    targets = get_targets(res, perms["permissionassignment"])

    for role in roles:
        if is_inheriting(role, targets, perms["rolehierarchy"]):
            return True
    return False

def main():
    if not len(sys.argv) == 3:
        raise Exception(f"expected 3 arguments, got {len(sys.argv)}")

    usr = sys.argv[1]
    res = sys.argv[2]
    with open("./rbac.json") as f:
        perms = json.load(f)
        print(has_permission(usr, res, perms))

if __name__ == "__main__":
    main()


