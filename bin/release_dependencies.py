#!/usr/bin/env python

from gus.DependencyClient import DependencyClient, DependencyGrapher
import sys

gus = DependencyClient()
grapher = DependencyGrapher()

def main():
    if len(sys.argv) > 1:
        build = gus.find_build_id(sys.argv[1])
        data = gus.get_release_dependency_tree(build)
        grapher.graph_dependencies(data, sys.argv[1])
    else:
        print "Specify a release label"

if __name__ == '__main__':
    main()
    
