#!/usr/bin/env python

from gus.DependencyClient import DependencyClient, DependencyGrapher
import sys

gus = DependencyClient()
grapher = DependencyGrapher()

def graph_team_release(build, teamid, teamname):
    data = gus.get_team_release_dependency_tree(build, teamid)
    label = "%s-%s" % (sys.argv[1], teamname)
    grapher.graph_dependencies(data, label)
    
def usage():
    print "Incorrect usage:\n%s build_name [team_id]" % sys.argv[0]

def main():
    if len(sys.argv) > 1:
        build = gus.find_build_id(sys.argv[1])
        
        if len(sys.argv) == 3:
            team = gus.get_team_record(sys.argv[2])
            graph_team_release(build, team['Id'], team['Name'])
        elif len(sys.argv) == 2:
            userid = gus.get_current_user_id()
            teams = gus.get_scrum_teams_for_user(userid)
            for team in teams:
                graph_team_release(build, team[0], team[1])
        else:
            usage()
    else:
        usage()

if __name__ == '__main__':
    main()
    
