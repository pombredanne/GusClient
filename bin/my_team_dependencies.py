#!/usr/bin/env python

from gus.DependencyClient import DependencyClient
import pydot

def my_work_node(dep):
    label = "%s (%s)" % (dep['my_work'],dep['my_work_status'])
    return pydot.Node(label)

def their_work_node(dep):
    label = "%s (%s)" % (dep['their_work'],dep['their_work_status'])
    return pydot.Node(label)

def add_node(graph, dep):
        if 'my_work' in dep.keys() and 'their_work' in dep.keys():
            graph.add_edge(pydot.Edge(my_work_node(dep), their_work_node(dep), label=dep['dep_deliverable']))
        elif 'my_work' in dep.keys():
            graph.add_node(my_work_node(dep))
        elif 'their_work' in dep.keys():
            graph.add_node(their_work_node(dep))
            
        if 'nested_deps' in dep.keys():
            for nest in dep['nested_deps']:
                add_node(graph, nest)

def main():
    gus = DependencyClient()
    userid = gus.get_current_user_id()
    teams = gus.get_scrum_teams_for_user(userid)
    for team in teams:
        data = gus.get_team_dependency_tree(team[0])
        graph = pydot.Dot(graph_type='digraph', label=team[1])
        for dep in data:
            add_node(graph, dep)
            
        graph.write_png('%s.png' % team[1])
            

if __name__ == '__main__':
    main()
    
