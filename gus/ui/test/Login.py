'''
Created on Aug 8, 2013

@author: scrosby
'''
import unittest
from ..Login import Factory

class Test(unittest.TestCase):


    def test_cli_login(self):
        #login = Factory().get_login()
        #username = login.get_username()
        #print username
        pass
        
    def test_gui_login(self):
        login = Factory().get_login(login_type='GUI')
        username = login.get_username()
        print username

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_login']
    unittest.main()