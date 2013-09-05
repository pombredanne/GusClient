from .Gus import Client

class DependencyClient(Client):
    '''
    Tools for tracking down team and work dependencies
    '''
    def find_active_dependencies_on_team(self, teamid):
        '''
        Returns a list of Ids of Dependencies on a specified team that are not Closed
        '''
        result = self.sf_session.query("Select Id from ADM_Team_Dependency__c where Provider_Team__c='%s' and Dependency_Status__c not in('Completed','Never')" % teamid)
        return result['records']
    
    def find_active_team_dependencies(self, teamid):
        '''
        Returns a list of Ids of Dependencies that a specified team has on others that are not Closed
        '''
        result = self.sf_session.query("Select Id from ADM_Team_Dependency__c where Dependent_Team__c='%s' and Dependency_Status__c not in('Completed','Never')" % teamid)
        return result['records']
    
    def find_release_dependencies(self, buildid):
        '''
        Returns a list of Ids of Dependencies that have been targeted to a specified release
        '''
        result = self.sf_session.query("Select Id from ADM_Team_Dependency__c where Target_Build__c='%s'" % buildid)
        return result['records']
    
    def find_team_release_dependencies(self, buildid, teamid):
        '''
        Returns a list of dependencies in a specific release that a team has on other teams
        '''
        result = self.sf_session.query("Select Id from ADM_Team_Dependency__c where Target_Build__c='%s' and Dependent_Team__c='%s'" % (buildid, teamid))
        return result['records']
    
    def find_release_dependencies_on_team(self, buildid, teamid):
        '''
        Returns a list of dependencies in a specific release that are on a specified team
        '''
        result = self.sf_session.query("Select Id from ADM_Team_Dependency__c where Target_Build__c='%s' and Provider_Team__c='%s'" % (buildid, teamid))
        return result['records']

    def find_work_dependencies(self, work_id):
        '''
        Returns a list of Ids of Dependencies on a specified work item
        '''
        try:
            result = self.sf_session.query("Select Id from ADM_Team_Dependency__c where Dependent_User_Story__c='%s'" % work_id)
            out = result['records']
        except:
            out = []
            
        return out
    
    def find_dependencies_on_work(self, work_id):
        '''
        Returns a list of ids of dependencies that need to be satisfied for a specified work item
        '''
        try:
            result = self.sf_session.query("Select Id from ADM_Team_Dependency__c where Provider_User_Story__c='%s'" % work_id)
            out = result['records']
        except:
            out = []
            
        return out
    
    def find_work_requiring_dependency(self, dependency_id):
        '''
        Retrieves the work record for the dependent work for a specified dependency
        '''
        dep = self.get_dependency_record(dependency_id)
        return self.get_work_record(dep['Dependent_User_Story__c'])
    
    def find_work_for_dependency(self, dependency_id):
        '''
        Retrieves the work record for the provider work for a specified dependency
        '''
        dep = self.get_dependency_record(dependency_id)
        return self.get_work_record(dep['Provider_User_Story__c'])
    
    def get_dependency_data(self, dependency_id, loop_detector=None):
        '''
        Creates a graph of all the work and related work of a specified dependency
        '''
        if loop_detector is None:
            ld = []
        else:
            ld = loop_detector
        my_dep = self.get_dependency_record(dependency_id)

        my_work = self.find_work_requiring_dependency(dependency_id)
        their_work = self.find_work_for_dependency(dependency_id)
        
        if my_work is not None:
            my_sprint = self.get_sprint_for_work(my_work['Id'])
        
        if their_work is not None:
            their_sprint = self.get_sprint_for_work(their_work['Id'])
        
        provider = self.get_team_record(my_dep['Provider_Team__c'])
        dependent = self.get_team_record(my_dep['Dependent_Team__c'])
        
        if my_dep['Target_Build__c'] is not None:
            build = self.get_build_record(my_dep['Target_Build__c']);
            build_name=build['Name']
        else:
            build_name=''
            
        dep = Dependency(my_dep, target=build_name)
            
        if my_work is not None:
            if my_sprint is not None:
                sprint = my_sprint['Name']
            else:
                sprint = None
            dep.set_my_work(Work(my_work, dependent['Name'], sprint))
            
            work_for_deps = self.find_dependencies_on_work(my_work['Id'])
            for d in work_for_deps:
                if d['Id'] not in ld:
                    ld.append(d['Id'])
                    dep.add_parent(self.get_dependency_data(d['Id'], ld))
                
        if dep.name() not in ld:
            ld.append(dep.name())
            if their_work is not None:
                if their_sprint is not None:
                    sprint = their_sprint['Name']
                else:
                    sprint = None
                dep.set_their_work(Work(their_work, provider['Name'], sprint))
                
                deps_on_their_work = self.find_work_dependencies(their_work['Id'])
                for d in deps_on_their_work:
                    dep.add_child(self.get_dependency_data(d['Id'], loop_detector=ld))
            
        return dep
    
    def get_team_dependency_tree(self, teamid):
        '''
        Creates an array of dependencies related to a specified team with related dependencies
        '''
        deps = self.find_active_dependencies_on_team(teamid)
        needs = self.find_active_team_dependencies(teamid)
        out = []
        ld = []
        for dep in deps:
            out.append(self.get_dependency_data(dep['Id'], loop_detector=ld))
            
        for dep in needs:
            out.append(self.get_dependency_data(dep['Id'], loop_detector=ld))
            
        return out
    
    def get_release_dependency_tree(self, buildid):
        '''
        Creates an array of dependencies targeted to a specified build with related dependencies
        '''
        deps = self.find_release_dependencies(buildid)
        out = []
        ld = []
        for dep in deps:
            out.append(self.get_dependency_data(dep['Id'], loop_detector=ld))
            
        return out
    
    def get_team_release_dependency_tree(self, buildid, teamid):
        '''
        Creates an array of dependencies targeted for a specified release for a specified team
        '''
        deps = self.find_team_release_dependencies(buildid, teamid)
        needs = self.find_release_dependencies_on_team(buildid, teamid)
        out = []
        ld = []
        for dep in deps:
            out.append(self.get_dependency_data(dep['Id'], loop_detector=ld))
            
        for dep in needs:
            out.append(self.get_dependency_data(dep['Id'], loop_detector=ld))
            
        return out

class Dependency:
    '''
    Data Structure for dependencies
    '''
    def __init__(self, dep, target=None):
        self.id = dep['Id']
        self.__name__ = dep['Name']
        self.__deliverable__ = dep['Deliverable__c']
        self.__status__ = dep['Dependency_Status__c']
        self.__target__ = target
        self.__children__ = []
        self.__parents__ = []
        self.__my_work__ = None
        self.__their_work__ = None
        
    def name(self):
        '''
        The dependency name (ie TD-xxx)
        '''
        return self.__name__
    
    def set_my_work(self, work):
        '''
        Sets the work instance that needs the depencency
        '''
        self.__my_work__ = work
        
    def my_work(self):
        '''
        Returns the work that needs the dependency
        '''
        return self.__my_work__
    
    def set_their_work(self, work):
        self.__their_work__ = work
    
    def their_work(self):
        return self.__their_work__
    
    def deliverable(self):
        return self.__deliverable__
    
    def target(self):
        return self.__target__
    
    def status(self):
        return self.__status__
    
    def add_child(self, dep):
        self.__children__.append(dep)
    
    def children(self):
        return self.__children__
    
    def add_parent(self, dep):
        self.__parents__.append(dep)
        
    def parents(self):
        return self.__parents__
    
class Work:
    def __init__(self, work, team, sprint=None):
        self.id = work['Id']
        self.__name__ = work['Name']
        self.__label__ = work['Subject__c']
        self.__status__ = work['Status__c']
        self.__team__ = team
        self.__sprint__ = sprint
        self.__rank__ = work['Priority_Rank__c']
        self.parent_work = []
        self.child_work = []
    
    def name(self):
        return self.__name__
    
    def team(self):
        return self.__team__
    
    def status(self):
        return self.__status__
    
    def label(self):
        return self.__label__
    
    def sprint(self):
        return self.__sprint__
    
    def rank(self):
        return self.__rank__

    
