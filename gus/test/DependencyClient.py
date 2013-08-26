'''
Created on Aug 26, 2013

@author: scrosby
'''
import unittest
from ..DependencyClient import DependencyGrapher, Dependency, Work

class Test(unittest.TestCase):

    def setUp(self):
        dep = {
               'Id': '1',
               'Name': 'TD-test',
               'Deliverable__c': 'test dependency',
               'Dependency_Status__c': 'New',
               'Providing_User_Story__c': '1',
               'Depending_User_Story__c': '2',
               'Provider_Team__c': 'a',
               'Dependent_Team__c': 'b',
               'Target_Build__c': 'x',
               }
        
        work1 = {
                'Id':'1',
                'Name':'W-Work1',
                'Status__c':'Triaged',
                'Subject__c':'Stuff to do',
                 }
        work2 = {
                'Id':'2',
                'Name':'W-Work2',
                'Status__c':'QA In Progress',
                'Subject__c':'Stuff to get done',
                 }
        
        self.dep = Dependency(dep, 'release x')
        self.dep.set_my_work(Work(work1, 'team a'))
        self.dep.set_their_work(Work(work2, 'team b'))

    def test_simple_graph(self):
        grapher = DependencyGrapher()
        grapher.graph_dependencies([self.dep], 'test')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()