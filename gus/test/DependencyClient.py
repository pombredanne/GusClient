'''
Created on Aug 26, 2013

@author: scrosby
'''
import unittest
from ..DependencyClient import DependencyGrapher, Dependency, Work

class Test(unittest.TestCase):

    def setUp(self):
        self.deps = []
        for i in range(1,10):
            self.deps.append(self.create_dep(str(i)))
            
        self.deps[3].their_work().__status__ = 'Never'
        
    def create_dep(self, label):
        dep = {
               'Id': label,
               'Name': 'TD-test%s' % label,
               'Deliverable__c': 'Deliverable %s' % label,
               'Dependency_Status__c': 'New',
               'Providing_User_Story__c': 'PROVIDE%s' % label,
               'Depending_User_Story__c': 'DEPEND%s' % label,
               'Provider_Team__c': 'Providing Team',
               'Dependent_Team__c': 'Depending Team',
               'Target_Build__c': 'Release x',
               }
        
        work1 = {
                'Id':'1%s' % label,
                'Name':'W-Work1%s' % label,
                'Status__c':'New',
                'Subject__c':'Work for %s' % label,
                'Sprint__c': 'Sprint 1',
                'Priority_Rank__c': '1',
                 }
        work2 = {
                'Id':'2%s' % label,
                'Name':'W-Work2%s' % label,
                'Status__c':'QA In Progress',
                'Subject__c':'Stuff to get done for %s' % label,
                'Sprint__c': 'Sprint 2',
                'Priority_Rank__c': '2',
                 }
        out = Dependency(dep, target='Release x')
        out.set_my_work(Work(work1, 'Team 1'))
        out.set_their_work(Work(work2, 'Team 2'))
        
        return out

    def test_simple_graph(self):
        grapher = DependencyGrapher()
        grapher.graph_dependencies(self.deps, 'test')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()