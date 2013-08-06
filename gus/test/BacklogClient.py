import unittest
from ..BacklogClient import BacklogClient

class Test(unittest.TestCase):
    def testClient(self):
        gus = BacklogClient()
        buildid = gus.find_build_id('MC_185')
        self.assertEqual(len(buildid), 18, 'Not a build id, buildids are 18 characters long')

    def test_get_my_work(self):
        gus = BacklogClient()
        my_work = gus.get_open_work_for_user('scrosby@salesforce.com')
        print my_work
        
    def test_user_id(self):
        gus = BacklogClient()
        userid = gus.get_current_user_id()
        current_work = gus.get_open_work_for_user_id(userid)
        print current_work

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()