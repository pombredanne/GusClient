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
        
        provider = self.get_team_record(my_dep['Provider_Team__c'])
        dependent = self.get_team_record(my_dep['Dependent_Team__c'])
        
        if my_dep['Target_Build__c'] is not None:
            build = self.get_build_record(my_dep['Target_Build__c']);
            build_name=build['Name']
        else:
            build_name=''
            
        dep = Dependency(my_dep, target=build_name)
            
        if dep.name() not in ld:
            ld.append(dep.name())
            if my_work is not None:
                dep.set_my_work(Work(my_work, dependent['Name']))
            if their_work is not None:
                dep.set_their_work(Work(their_work, provider['Name']))
                
                deps_on_their_work = self.find_work_dependencies(their_work['Id'])
                for d in deps_on_their_work:
                    dep.add_child(self.get_dependency_data(d['Id'], loop_detector=ld))
        else:
            print "Loop detected on dependency: %s" % dep.name()
            
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
        deps = self.find_team_release_dependencies(buildid, teamid)
        needs = self.find_release_dependencies_on_team(buildid, teamid)
        out = []
        ld = []
        for dep in deps:
            out.append(self.get_dependency_data(dep['Id'], loop_detector=ld))
            
        for dep in needs:
            out.append(self.get_dependency_data(dep['Id'], loop_detector=ld))
            
        return out

import pydot
            
class DependencyGrapher:
    '''
    Creates a visualization of the team dependency graph
    '''
    def __get_status_color__(self, status):
        status_color = {
                        'New':'red',
                        'Never':'red',
                        'Deferred':'red',
                        'Fixed':'yellow',
                        'Committed':'yellow',
                        'QA In Progress':'yellow',
                        'Completed':'green',
                        'Closed':'green',
                        }
        if status in status_color.keys():
            color = status_color[status]
        else:
            color = 'orange'
            
        return color
        
    
    def __work_node__(self, workid, status, subject):
        label = "%s (%s)\n%s" % (workid,status,subject)
            
        node = pydot.Node(label)
        node.set_style('filled')
        node.set_fillcolor(self.__get_status_color__(status))
        return node
    
    def __my_work_node__(self, dep):
        return self.__work_node__(dep.my_work().name(), dep.my_work().status(), dep.my_work().label())
    
    def __their_work_node__(self, dep):
        return self.__work_node__(dep.their_work().name(), dep.their_work().status(), dep.their_work().label())
    
    def __team_subgraph__(self, graph, team):
        name = 'cluster_%s' % team.replace(' ', '_')
        subgraph = pydot.Subgraph(name)
        subgraph.set_label(team)
        graph.add_subgraph(subgraph)
            
        return subgraph
    
    def __add_node__(self, graph, dep):
            dep_node = pydot.Node('%s (%s)\n%s' % (dep.deliverable().replace(':','-'), dep.status(), dep.target()))
            dep_node.set_shape('rectangle')
            dep_node.set_style('filled')
            dep_node.set_fillcolor(self.__get_status_color__(dep.status()))
            graph.add_node(dep_node)
            
            if dep.my_work() is not None:
                work = self.__my_work_node__(dep)
                subgraph = self.__team_subgraph__(graph, dep.my_work().team())
                subgraph.add_node(work)
                graph.add_edge(pydot.Edge(work, dep_node))
            
            if dep.their_work() is not None:
                work = self.__their_work_node__(dep)
                subgraph = self.__team_subgraph__(graph, dep.their_work().team())
                subgraph.add_node(work)
                graph.add_edge(pydot.Edge(dep_node, work))
                
            for child in dep.children():
                self.__add_node__(graph, child)

    def __plot_graph__(self, data, label):
        '''
        Creates a graph visualization using the label as a filename and the graph data from the client
        '''
        graph = pydot.Dot(graph_type='digraph', label=label, rankdir='LR')
        for dep in data:
            self.__add_node__(graph, dep)
        
        return graph
        
    def graph_dependencies(self, data, label):
        graph = self.__plot_graph__(data, label)

        with open('%s.dot' % label, 'w') as f:
            f.write(graph.to_string())    
            f.close()
        
        graph.write('%s.pdf' % label, format='pdf')
        graph.write('%s.png' % label, format='png')
        
class Dependency:
    def __init__(self, dep, target=None):
        self.__name__ = dep['Name']
        self.__deliverable__ = dep['Deliverable__c']
        self.__status__ = dep['Dependency_Status__c']
        self.__target__ = target
        self.__children__ = []
        self.__my_work__ = None
        self.__their_work__ = None
        
    def name(self):
        return self.__name__
    
    def set_my_work(self, work):
        self.__my_work__ = work
        
    def my_work(self):
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
    
class Work:
    def __init__(self, work, team):
        self.__name__ = work['Name']
        self.__label__ = work['Subject__c']
        self.__status__ = work['Status__c']
        self.__team__ = team
    
    def name(self):
        return self.__name__
    
    def team(self):
        return self.__team__
    
    def status(self):
        return self.__status__
    
    def label(self):
        return self.__label__
    
