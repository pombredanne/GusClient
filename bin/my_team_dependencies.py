#!/usr/bin/env python

from gus.DependencyClient import DependencyClient, DependencyGrapher
import sys

gus = DependencyClient()
grapher = DependencyGrapher()

def graph_all_my_teams():
    userid = gus.get_current_user_id()
    teams = gus.get_scrum_teams_for_user(userid)
    for team in teams:
        data = gus.get_team_dependency_tree(team[0])
        grapher.graph_team(gus, data, team[1])
            
def main():
    if len(sys.argv) > 1:
        team = gus.get_team_record(sys.argv[1])
        data = gus.get_team_dependency_tree(team['Id'])
        grapher.graph_team(data, team['Name'])
    else:
        graph_all_my_teams()

if __name__ == '__main__':
    main()
    
