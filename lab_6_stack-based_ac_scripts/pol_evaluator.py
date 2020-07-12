import sys
from collections import deque

class Script:
    stack = deque()

    def __init__(self, f):
        self.f = f

    def push_data(self, data: str): 
        self.stack.append(data)

    def is_equal(self) -> bool:
        a = self.pop_data()
        b = self.pop_data()
        eval = (a==b)
        print(f"Eval: {eval}")
        self.push_data(eval)
        return eval 

    def pop_data(self) -> str:
        return self.stack.pop()

    def split_line(self, line: str) -> (callable, str):
        elems = line.split()
        return self.OPS.get(elems[0]), " ".join(elems[1:])

    def no_op(self, *_):
        pass
 
    def exec(self) -> str:
        for line in self.f.readlines():
            cb, args = self.split_line(line)
            cb(self, args) if args else cb(self) 

    OPS = dict({
        ("ISEQUAL", is_equal),
        ("PUSHDATA", push_data),
        ("#", no_op)
    })

class Policy(Script): 
    def exec(self) -> str:
        pass

# class Request(Script):

def main():
    if not len(sys.argv) == 3:
        raise Exception(f"expected 3 arguments, got {len(sys.argv)}")

    rs = sys.argv[1]
    ps = sys.argv[2]
    with open(f"./{rs}") as rf:
        with open(f"./{ps}") as pf:
           r = Script(rf) 
           r.exec()
           p = Script(pf) 
           p.exec()
           print(f"final stack: {Script.stack}")

if __name__ == "__main__":
    main()


