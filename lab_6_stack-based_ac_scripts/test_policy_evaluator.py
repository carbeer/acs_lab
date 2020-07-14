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

            s = Script()
            s.exec(rs)
            s.exec(ps)
            self.assertEqual(s.stack[-1], test[2])
        
    
        

    def test_t2(self):
        tests = [
               (["pw1", "pw2"],["pw1", "pw2", "pw3"], "3 2", "2", True),
               (["pwwhatever", "pw2"], ["pw1", "pw2", "pw3"], "3 2", "2", False)
                ]
        for test in tests: 
            rs = []
            ps = []

            for pw in test[0]:
                rs.append(f"PUSHDATA {pw}") 
            rs.append("# READ")

            for pw in test[1]:
                ps.append(f"PUSHDATA {pw}")
            ps.append(f"COUNTPASSWORDS {test[2]}")
            ps.append(f"ISGREATEREQUAL {test[3]}")

            s = Script()
            s.exec(rs)
            print(s.stack)
            s.exec(ps)
            print(s.stack)
            self.assertEqual(s.stack[-1], test[4])


            
                    
            
        
        


