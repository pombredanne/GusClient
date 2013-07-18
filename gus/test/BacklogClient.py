import unittest
from ..BacklogClient import BacklogClient

class Test(unittest.TestCase):
    def testClient(self):
        gus = BacklogClient()
        buildid = gus.find_build_id('MC_185')
        self.assertEqual(len(buildid), 18, 'Not a build id, buildids are 18 characters long')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()