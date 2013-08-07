'''
Created on Jul 18, 2013

@author: scrosby
'''
import unittest
from ..Gus import Client

class Test(unittest.TestCase):


    def test_get_scrum_teams(self):
        gus = Client()
        userid = gus.get_current_user_id()
        teams = gus.get_scrum_teams_for_user(userid)
        
        print teams
        
    def test_get_user_email(self):
        gus = Client()
        userid = gus.get_current_user_id()
        email = gus.get_user_email(userid)
        print email

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testInit']
    unittest.main()