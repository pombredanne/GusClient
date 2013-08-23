from .Gus import Client

class DependencyClient(Client):
    def find_active_dependencies_on_team(self, teamid):
        result = self.sf_session.query("Select Id from ADM_Team_Dependency__c where Provider_Team__c='%s' and Dependency_Status__c!='Completed'" % teamid)
        return result['records']
    
    def find_active_team_dependencies(self, teamid):
        result = self.sf_session.query("Select Id from ADM_Team_Dependency__c where Dependent_Team__c='%s' and Dependency_Status__c!='Completed'" % teamid)
        return result['records']

    def find_work_dependencies(self, work_id):
        try:
            result = self.sf_session.query("Select Id from ADM_Team_Dependency__c where Dependent_User_Story__c='%s'" % work_id)
            out = result['records']
        except:
            out = []
            
        return out
    
    def find_work_requiring_dependency(self, dependency_id):
        dep = self.get_dependency_record(dependency_id)
        return self.get_work_record(dep['Dependent_User_Story__c'])
    
    def find_work_for_dependency(self, dependency_id):
        dep = self.get_dependency_record(dependency_id)
        return self.get_work_record(dep['Provider_User_Story__c'])
        
    def get_dependency_record(self, dependency_id):
        result = self.sf_session.ADM_Team_Dependency__c.get(dependency_id)
        return result
    
    def get_work_record(self, work_id):
        if work_id is not None:
            result = self.sf_session.ADM_Work__c.get(work_id)
        else:
            result = None
            
        return result
    
    def get_dependency_data(self, dependency_id, loop_detector=None):
        if loop_detector is None:
            ld = []
        else:
            ld = loop_detector
        my_work = self.find_work_requiring_dependency(dependency_id)
        my_dep = self.get_dependency_record(dependency_id)
        their_work = self.find_work_for_dependency(dependency_id)
        data = {
                'dep_name':my_dep['Name'],
                'dep_status':my_dep['Dependency_Status__c'],
                'dep_deliverable':my_dep['Deliverable__c'],
                'dep_providing':my_dep['Provider_Team__c'],
                'dep_depending':my_dep['Dependent_Team__c'],
                }
        if my_dep['Name'] not in ld:
            ld.append(my_dep['Name'])
            if my_work is not None:
                data['my_work'] = my_work['Name']
                data['my_work_subject'] = my_work['Subject__c']
                data['my_work_status'] = my_work['Status__c']
            if their_work is not None:
                data['their_work'] = their_work['Name']
                data['their_work_subject'] = their_work['Subject__c']
                data['their_work_status'] = their_work['Status__c']
                deps_on_their_work = self.find_work_dependencies(their_work['Id'])
                nested_deps = []
                for d in deps_on_their_work:
                    nested_deps.append(self.get_dependency_data(d['Id'], loop_detector=ld))
                data['nested_deps'] = nested_deps
        else:
            data['error'] = '**Looping Dependency**'
            
        return data
    
    def get_team_dependency_tree(self, teamid):
        deps = self.find_active_dependencies_on_team(teamid)
        out = []
        ld = []
        for dep in deps:
            out.append(self.get_dependency_data(dep['Id'], loop_detector=ld))
        return out
            
