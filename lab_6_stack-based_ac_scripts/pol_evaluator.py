import sys
import logging
from collections import deque

class Script:

    def __init__(self):
        self.stack = deque()

# Utils

    def split_line(self, line: str) -> (callable, str):
        elems = line.split()
        return self._OPS.get(elems[0]), elems[1:]

    def persist_result(self, s: str):
        logging.info(f"result: {s}")
        self.push_data(s)
        
    def pop_data(self) -> str:
        return self.stack.pop()

    @classmethod
    def no_op(cls, _):
        pass
 
    @classmethod
    def real_hash(cls, s: str):
        return str(hash(s))

    @classmethod
    def fake_hash(cls, s: str):
        return str(sum([ord(x) for x in s])) # collision through reordering 


# Operator implementation

    def push_data(self, data: str): 
        self.stack.append(data)

    def is_equal(self):
        a = self.pop_data() 
        b = self.pop_data()
        self.persist_result(a==b) 

    def is_geq(self, val: str):
        self.persist_result(self.pop_data() >= int(val))
        
    def count_pws(self, m: str, n: str):    
        pws = []
        matches = 0
        for _ in range(0, int(m)):
            pws.append(self.pop_data()) 

        for _ in range(0, int(n)):
            pw = self.pop_data() 
            if pw in pws: 
                pws.remove(pw)  
                matches += 1
        self.push_data(matches)

    def rotate(self):
        self.stack.rotate()
        
    def is_and(self):
        el1 = self.pop_data()
        el2 = self.pop_data()
        self.persist_result(el1 and el2)

    def is_or(self):
        el1 = self.pop_data()
        el2 = self.pop_data()
        self.persist_result(el1 or el2)

    def hash_elem(self):
        el = self.pop_data()
        self.push_data(self._HASH(el))

    def duplicate(self):
        el = self.pop_data()
        self.push_data(el)
        self.push_data(el)

    def is_not(self):
        el = self.pop_data()
        self.push_data(not el)

# Entry point

    def exec(self, lines):
        for line in lines: 
            cb, args = self.split_line(line)
            cb(self, *args) if args else cb(self) 

    _OPS = dict({
        ("ISEQUAL", is_equal),
        ("PUSHDATA", push_data),
        ("COUNTPASSWORDS", count_pws),
        ("ISGREATEREQUAL", is_geq),
        ("ROTATE", rotate),
        ("DUP", duplicate),
        ("OR", is_or), 
        ("HASH", hash_elem), 
        ("AND", is_and),
        ("NOT", is_not),
        ("#", no_op.__func__)
    })

    _HASH = fake_hash.__func__ # real_hash as alternative, will break tests due to missing collisions

def main():
    if not len(sys.argv) == 3:
        raise Exception(f"expected 3 arguments, got {len(sys.argv)}")

    rs = sys.argv[1]
    ps = sys.argv[2]
    with open(f"./{rs}") as rf:
        with open(f"./{ps}") as pf:
           script = Script() 
           script.exec(rf.readlines())
           script.exec(pf.readlines()) 
           print(f"final stack: {script.stack}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()


