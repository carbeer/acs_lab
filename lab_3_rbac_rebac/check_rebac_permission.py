import sys
import math
import json
import re
import operator
import logging

# 0 for assignment 2.1, 1 for assignment 2.2
version = 0 

ops = {
        "<": operator.lt,
        ">": operator.gt,
        "=": operator.eq,
    }

def get_neighbors(node: str, usr_graph: dict) -> list:
    if not node in usr_graph:
        raise Exception(f"user {node} does not exist")
    if not isinstance(usr_graph[node], list):
        raise Exception("expected list as input, check the formatting of your usergraph")
    return usr_graph[node]

def get_coworkers(node: str, usr_graph: dict) -> list: 
    if not node in usr_graph:
        raise Exception(f"user {node} does not exist")   
    if usr_graph[node] is None:
        return []
    if not isinstance(usr_graph[node], dict):
        raise Exception(f"expected dict as input, check the formatting of your usergraph, got {type(usr_graph[node])}: {usr_graph[node]}")
    ret = (usr_graph[node]["coworkers"] if "coworkers" in usr_graph[node] else [])
    return ret

def get_friends(node: str, usr_graph: dict) -> list:
    if not node in usr_graph:
        raise Exception(f"user {node} does not exist")
    if usr_graph[node] is None:
        return []
    if not isinstance(usr_graph[node], dict):
        raise Exception(f"expected dict as input, check the formatting of your usergraph, got {type(usr_graph[node])}: {usr_graph[node]}")
    ret = (usr_graph[node]["friends"] if "friends" in usr_graph[node] else [])
    return ret 


pat = [
        [
            (re.compile('h(>|<|=)([0-9])'), get_neighbors),
        ],
        [
            (re.compile('f(>|<|=)([0-9])'), get_friends),
            (re.compile('c(>|<|=)([0-9])'), get_coworkers),
        ],
    ]

config = [
        "./rebac.json",
        "./rebac_extended.json",
    ]


# Returns the policies with the corresponding user as a list of tuples of structure (policy, user)
def get_policy_per_user(usr: str, res: str, perm: dict) -> list:
    
    ctrl, targets = (None, []) 
    for r in perm["resources"]:
        if r["name"] == res:
            ctrl, targets = r["controller"], r["target"]
            break
    if ctrl is None:
        raise Exception("recource does not exist")

    pol_user = [(perm["policies"][ctrl]["trp"], ctrl)]

    for t in targets:
        pol_user.append((perm["policies"][t]["tup"], t))

    for el in pol_user: logging.debug(el) 
    return pol_user 

# Returns the shortest path from source to sink using BFS
def shortest_path(source: str, sink: str, cb: callable, usrs: list, usr_graph: dict) -> int:
    if source == sink:
        logging.debug("User is the target")
        return 0

    visited = dict.fromkeys(usrs) 
    curr_nodes = [source] 

    for i in range(1, len(usrs)):
        next_nodes = [] 
        for node in curr_nodes:
            if sink in cb(node, usr_graph):
                logging.debug(f"Shortest path to {sink} is {i}")
                return i
            for el in cb(node, usr_graph):
                if not visited[el]:
                    next_nodes.append(el)
                    visited[el] = True
        curr_nodes = next_nodes
    logging.info(f"no path between {source} and {sink} using {cb.__name__}")
    return math.inf 

# Evaluates an (atomic) part of a single policy 
def eval_partial_policy(usr: str, tgt: str, limit: int, op: callable, cb: callable, perm: dict) -> bool:   
    d =  shortest_path(usr, tgt, cb, perm["users"], perm["usergraph"])
    # Evaluates whether distance *operator (</>/=)* *value defined by policy*
    logging.debug(f"partial policy for target {tgt} with {op.__name__} {limit} evaluated to {op(d,limit)}")
    return op(d, limit)

# Evaluates a single policy. A single policy is only True is all of its atomic parts are True.
def eval_policy(pol: str, usr: str, tgt: str, perm: dict) -> bool:
    parts = pol.split(" & ")
    for pt in parts: 
        evaled = False
        for p, cb in pat[version]:
            m = p.match(pt)
            if m and len(m.groups()) == 2:
                evaled = True
                op, limit = m.groups() 
                if not eval_partial_policy(usr, tgt, int(limit), ops[op], cb, perm):
                    return False
        if not evaled:
            raise Exception(f"invalid policy formatting: {pt}")
    logging.debug(f"policy {pol} evaluated to True")
    return True

# Evaluates whether usr should have access to res. Uses op to resolve conflicting policy decisions.
def has_permission(usr: str, res: str, op: str, perm: dict) -> bool: 
    break_cond = (True if op == "ANY" else False) 
    for pol, tgt in get_policy_per_user(usr, res, perm):
        if eval_policy(pol, usr, tgt, perm) == break_cond:
            return break_cond
    return not break_cond 

def main():
    logging.basicConfig(level=logging.DEBUG)
    if not len(sys.argv) == 4:
        raise Exception(f"expected 4 arguments, got {len(sys.argv)}")
    usr = sys.argv[1]
    res = sys.argv[2]
    op = sys.argv[3].upper()
    if not op in ["ALL", "ANY"]:
        raise Exception(f"last argument must be ANY or ALL, got {op}")

    with open(config[version]) as f:
        perm = json.load(f)
        dec = has_permission(usr, res, op, perm)
        print("*****Access Decision*****")
        print(dec)

if __name__ == "__main__":
    main()
