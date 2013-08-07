import unittest
from ..BacklogClient import BacklogClient

class Test(unittest.TestCase):
    def testClient(self):
        gus = BacklogClient()
        buildid = gus.find_build_id('MC_185')
        self.assertEqual(len(buildid), 18, 'Not a build id, buildids are 18 characters long')

    def test_get_my_work(self):
        gus = BacklogClient()
        my_work = gus.get_open_work_for_user('amerritt@salesforce.com')
        print my_work

    def test_work_for_tasks(self):
        gus = BacklogClient()
        user_id = gus.get_user_id_for_email('amerritt@salesforce.com')
        work = gus.get_work_with_active_tasks_for_user(user_id)
        print 'work with tasks: ' + str(work)
        if 'W-1108172' in [x[0] for x in work]:
            print 'found it'
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()