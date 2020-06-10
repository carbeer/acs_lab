import sys
import json
import re
import operator
import logging

pat = re.compile('h(>|<|=)([0-9])')
ops = {
        "<": operator.le,
        ">": operator.ge,
        "=": operator.eq,
        }


# Returns the policies with the corresponding user as a list of tuples of structure (policy, user)
def get_policy_per_user(usr: str, res: str, perm: dict) -> list:
    if not usr in perm["policies"]:
        return [(None, None)]
    
    trp, tup = perm["policies"][usr]["trp"], perm["policies"][usr]["tup"]
    ctrl, targets = (None, []) 
    for r in perm["resources"]:
        if r["name"] == res:
            ctrl, targets = r["controller"], r["target"]
            break
    pol_user = list(zip([tup] * len(targets), targets))
    pol_user.append((trp, ctrl))
    for el in pol_user: logging.debug(el) 
    return pol_user 

# Returns the shortest path from source to sink using BFS
def shortest_path(source: str, sink: str, usrs: list,  usr_graph: dict) -> int:
    if source == sink:
        logging.debug("User is the target")
        return 0

    visited = dict.fromkeys(usrs) 
    curr_nodes = [source] 

    for i in range(1, len(usrs)):
        next_nodes = [] 
        for node in curr_nodes:
            if sink in usr_graph[node]:
                logging.debug(f"Shortest path to {sink} is {i}")
                return i
            for neighbor in usr_graph[node]:
                if not visited[neighbor]:
                    next_nodes.append(neighbor)
                    visited[neighbor] = True
        curr_nodes = next_nodes
    return -1

# Evaluates policy pol given a distance dist
def evaluate_policy(pol: str, dist: int) -> bool:   
    if dist == -1:
        return False
    matches = pat.match(pol)
    # Evaluates whether distance *operator (</>/=)* *value defined by policy*
    return (ops[matches.group(1)](dist, int(matches.group(2))))

# Evaluates whether usr should have access to res
def has_permission(usr: str, res: str, op: str, perm: dict) -> bool: 
    # all
    break_cond = False 
    # any
    if op == "ANY":
         break_cond = True 
    pol_user = get_policy_per_user(usr, res, perm)

    for p in pol_user:
        if p[0] is None or p[1] is None:
            return False
        if evaluate_policy(p[0], shortest_path(usr, p[1], perm["users"], perm["usergraph"])) == break_cond:
            return break_cond
    return not break_cond 

def main():
    logging.basicConfig(level=logging.DEBUG)
    assert len(sys.argv) == 4
    usr = sys.argv[1]
    res = sys.argv[2]
    op = sys.argv[3].upper()
    assert op in ["ALL", "ANY"]

    with open("./rebac.json") as f:
        perms = json.load(f)
        dec = has_permission(usr, res, op, perms)
        print("*****Decision*****")
        print(dec)

if __name__ == "__main__":
    main()
