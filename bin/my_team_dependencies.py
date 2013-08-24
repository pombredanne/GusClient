#!/usr/bin/env python

from gus.DependencyClient import DependencyClient
import pydot, sys

gus = DependencyClient()

def __my_work_node__(dep):
    label = "%s (%s)\n%s" % (dep['my_work'],dep['my_work_status'],dep['dep_depending'])
    return pydot.Node(label)

def __their_work_node__(dep):
    label = "%s (%s)\n%s" % (dep['their_work'],dep['their_work_status'],dep['dep_providing'])
    return pydot.Node(label)

def __add_node__(graph, dep):
        dep_node = pydot.Node('%s (%s)\n%s' % (dep['dep_deliverable'].replace(':','-'), dep['dep_status'], dep['dep_targeted']))
        dep_node.set_shape('rectangle')
        if 'my_work' in dep.keys() and 'their_work' in dep.keys():
            graph.add_edge(pydot.Edge(__my_work_node__(dep), dep_node))
            graph.add_edge(pydot.Edge(dep_node, __their_work_node__(dep)))
        elif 'my_work' in dep.keys():
            graph.add_edge(pydot.Edge(__my_work_node__(dep), dep_node))
        elif 'their_work' in dep.keys():
            graph.add_edge(pydot.Edge(dep_node, __their_work_node__(dep)))
            
        if 'nested_deps' in dep.keys():
            for nest in dep['nested_deps']:
                __add_node__(graph, nest)


def graph_team(team, label):
    data = gus.get_team_dependency_tree(team)
    graph = pydot.Dot(graph_type='digraph', label=label)
    for dep in data:
        __add_node__(graph, dep)
    
    graph.write_png('%s.png' % label)

def graph_all_my_teams():
    userid = gus.get_current_user_id()
    teams = gus.get_scrum_teams_for_user(userid)
    for team in teams:
        graph_team(gus, team[0], team[1])
            
def main():
    if len(sys.argv) > 1:
        team = gus.get_team_record(sys.argv[1])
        graph_team(team['Id'], team['Name'])
    else:
        graph_all_my_teams()

if __name__ == '__main__':
    main()
    
