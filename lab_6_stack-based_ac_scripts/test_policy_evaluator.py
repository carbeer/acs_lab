import unittest
from pol_evaluator import Script

class PolEvaluatorTest(unittest.TestCase):

    def test_t1(self):
        tests = [
            ("pw", "otherpw", False),
            ("pw", "pw", True)
            ]
        
        for test in tests:
            rs = [
                    f"PUSHDATA {test[0]}",
                    "# READ"
                    ]
            ps = [
                    f"PUSHDATA {test[1]}",
                    "ISEQUAL"
                    ]

            self.exec(rs, ps, test[2]) 
    
        

    def test_t2(self):
        tests = [
               (["pw1", "pw2"],["pw1", "pw2", "pw3"], "3 2", "2", True),
               (["pwwhatever", "pw2"], ["pw1", "pw2", "pw3"], "3 2", "2", False)
                ]
        for test in tests: 
            rs = [
                    f"PUSHDATA {test[0][0]}",
                    f"PUSHDATA {test[0][1]}",
                    "# READ"
                ]
            ps = [
                    f"PUSHDATA {test[1][0]}",
                    f"PUSHDATA {test[1][1]}",
                    f"PUSHDATA {test[1][2]}",
                    f"COUNTPASSWORDS {test[2]}",
                    f"ISGREATEREQUAL {test[3]}"
                ]
        
            self.exec(rs, ps, test[4])


    def test_t3(self):
        tests = [
               (["pw1", "pw2", None],["mpw", "pw1", "pw2", "pw3"], "3 2", "2", True),
               (["pwwhatever", "pw2", None], ["mpw", "pw1", "pw2", "pw3"], "3 2", "2", False),
               ([None, None, "mpw"], ["mpw","pw1", "pw2", "pw3"], "3 2", "2", True),
               ([None, None, "somempw"], ["mpw","pw1", "pw2", "pw3"], "3 2", "2", False)
                ]
        
        for test in tests:
            rs = [
                    f"PUSHDATA {test[0][0]}",
                    f"PUSHDATA {test[0][1]}",
                    f"PUSHDATA {test[0][2]}",
                    "# READ"
                ]

            rs = []
            for pw in test[0]:
                rs.append(f"PUSHDATA {pw}")
            rs.append("# READ")

            ps = [
                    f"PUSHDATA {test[1][0]}",
                    f"ISEQUAL",
                    f"ROTATE",
                    f"PUSHDATA {test[1][1]}",
                    f"PUSHDATA {test[1][2]}",
                    f"PUSHDATA {test[1][3]}",
                    f"COUNTPASSWORDS {test[2]}",
                    f"ISGREATEREQUAL {test[3]}",
                    "OR"
            ]
            
            self.exec(rs, ps, test[4])


    def test_t4(self):
        tests = [
                ("pw", 231, True),
                ("pw",Script.fake_hash("pw") , True),
                ("pw",Script.fake_hash("whatever") , False)
                ]

        for test in tests:
            rs = [
                    f"PUSHDATA {test[0]}",
                    "# READ"
                ]
            ps = [
                    "HASH",
                    f"PUSHDATA {test[1]}",
                    "ISEQUAL"
                ]

            self.exec(rs, ps, test[2])

    def test_t5(self):
        tests = [
                ("somepw", "someotherpw", False),
                ("somepw", "pwsome", True),
                ("somepw", "somepw", False)
                ]
        ps = [
                    "DUP",
                    "HASH",
                    "ROTATE",
                    "ROTATE",
                    "DUP",
                    "ROTATE",
                    "HASH",
                    "ISEQUAL",
                    "ROTATE",
                    "ISEQUAL",
                    "NOT",
                    "AND"
                ]

        for test in tests:
            rs = [
                    f"PUSHDATA {test[0]}",
                    f"PUSHDATA {test[1]}",
                    "# READ"
                ] 

            self.exec(rs, ps, test[2])

    def exec(self, rs, ps, expected):
            s = Script()
            s.exec(rs)
            print(s.stack)
            s.exec(ps)
            print(s.stack)
            self.assertEqual(s.stack[-1], expected)
                    
            
        
        


