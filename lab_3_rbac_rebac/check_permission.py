import sys
import json

# Checks whether role inherits one of the targets according to hierarchy
def is_inheriting(role: str, targets: list, hierarchy: dict):
	for target in targets:
		if role in hierarchy[role]: 
			return True		

	# Check for transitive inheritance
	for cand in hierarchy[role]:
		if is_inheriting(cand, targets, hierarchy):
			return True
	return False

# Returns list of roles that a user possesses
def get_roles(usr: str, role_ass: str):
	if usr in role_ass:
		return role_ass[usr]
	else: 
		return []

# Returns roles that are allowed to access the given resource
def get_targets(res: str, perm_ass: str):
	for r in perm_ass:
		if r["name"] == res:
			return r["pa"]

# Returns boolean, indicating whether a user has the permission to access the object
def has_permission(usr: str, res: str, perms: dict):
	roles = get_roles(usr, perms["roleassignment"])
	targets = get_targets(res, perms["permissionassignment"])

	for role in roles:
		if is_inheriting(role, targets):
			return True
	return False

def main():
    assert len(sys.argv) == 3
	usr = sys.argv[1]
	res = sys.argv[2]
	with open("./rbac.json") as f:
		perms = json.load(f)
		print(has_permission(usr, res, perms))

if __name__ == "__main__":
    main()


