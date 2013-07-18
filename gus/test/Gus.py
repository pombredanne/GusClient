'''
Created on Jul 18, 2013

@author: scrosby
'''
import unittest
from ..Gus import Client

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testInit(self):
        Client()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testInit']
    unittest.main()