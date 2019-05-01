# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 19:07:44 2019

@author: 34565
"""
from py2neo import Graph, NodeMatcher
from py2neo import Node,Relationship,Subgraph,PropertyDict,Walkable
from py2neo.ogm import *
import numpy as np
import sys
import webbrowser
import pandas as pd


def connectneo4j_datagraph():
    #########   local host/user/password depend on your neo4j server  ########################change here
    data_graph = Graph("http://localhost:7474", user="neo4j", password="19960229")
    return data_graph

def connectneo4j_querygraph():
    #########   local host/user/password depend on your neo4j server  ######################change here    
    querygraph = Graph("http://localhost:11008", user="neo4j", password="19960229")
    return querygraph

def cypher_load_datagraph(text):
    data_graph = connectneo4j_datagraph()
    n = data_graph.run(text).to_ndarray()
    return n

def cypher_load_querygraph(text):
    query_graph = connectneo4j_querygraph()
    n = query_graph.run(text).to_ndarray()
    return n

def datagraph_input():
    #################################################
    webbrowser.open("http://localhost:7474")
    print('Ready to input data graph!')

def datagraph_load():
    data_graph = connectneo4j_datagraph()
    print('number of nodes in data graph: ',len(data_graph.nodes))
    print('number of relationships in data graph: ',len(data_graph.relationships))
    nodes = cypher_load_datagraph("MATCH (n) RETURN n")
    paths = cypher_load_datagraph("MATCH (n) MATCH (n)-[r]-() RETURN r")
    np.savetxt('datagraph_localnodes.txt',nodes,fmt='%s')   
    np.savetxt('datagraph_localpaths.txt',paths,fmt='%s')   
    print('save data graph success!')

def querygraph_input():
    ################################################
    webbrowser.open("http://localhost:11008")
    print('Ready to input query graph!')
    
def querygraph_load():
    query_graph = connectneo4j_querygraph()
    print('number of nodes in data graph: ',len(query_graph.nodes))
    print('number of relationships in data graph: ',len(query_graph.relationships))
    nodes = cypher_load_querygraph("MATCH (n) RETURN n")
    paths = cypher_load_querygraph("MATCH (n) MATCH (n)-[r]-() RETURN r")
    np.savetxt('querygraph_localnodes.txt',nodes,fmt='%s')   
    np.savetxt('querygraph_localpaths.txt',paths,fmt='%s')   
    print('save query graph success!')


def load_graph_localnodes(graph):
    graph_lines = [line.rstrip('\n') for line in open(graph)]
    graph_lines = pd.DataFrame(graph_lines)
    graph_lines = graph_lines.values
    nodes_infos = []
    nodes_ = []
    for line in graph_lines:
        ###  in order to get ID and nodes separately:
        ID_ = str(line).split(':')[0]  
        ID_ = ID_.split('(')[1]         ###### store ID
        nodes_name = str(line).split(':')[1]
        nodes_name = nodes_name.split(' ')[0]     ############ store nodes 
        propertys_ = str(line).split('{')[1]
        propertys_ = propertys_.split('}')[0]
        nodes_info = {}
        nodes_info['ID'] = ID_
        nodes_info['Nodes'] =nodes_name
        nodes_info['Property'] =propertys_
        nodes_infos.append(nodes_info)
        nodes_ID = {}
        _ID = str(line).split(':')[0]  
        _ID = _ID.split('(')[1]        
        name_ = str(line).split(':')[-1]
        name_ = name_.split('}')[0]
        nodes_ID['ID'] = _ID
        nodes_ID['name'] = name_
        nodes_.append(nodes_ID)
    graph_nodes = []

    for node in nodes_infos:
        node_n = node['Nodes']
        graph_nodes.append(node_n)
        single_property = node['Property'].split(',')
    graph_nodes = list(set(graph_nodes))
     
    
    return graph_nodes,nodes_infos,nodes_

def load_graph_localpaths(graph,nodes_infos,nodes_):
    graph_lines = [line.rstrip('\n') for line in open(graph)]
    graph_lines = pd.DataFrame(graph_lines)
    graph_lines = graph_lines.values
    paths_infos = []
    paths_ = []
    graph_relationships = []
    for line in graph_lines:
        start_nodes = str(line).split(')')[0]  
        start_nodes = start_nodes.split('(')[1]
        relationship_ = str(line).split(':')[1]  
        relationship_ = relationship_.split(' ')[0]
        graph_relationships.append(relationship_)
        typeofrelationship = str(line).split('{')[1]
        typeofrelationship = typeofrelationship.split('}')[0]   ######### sometimes type of relationship are empty
        end_nodes_ID = str(line).split('>')[1]
        end_nodes_ID = end_nodes_ID.split('(')[1]
        end_nodes_ID = end_nodes_ID.split(')')[0]
        end_nodes_list = []
        if end_nodes_ID[0]== '_': 
            for node in nodes_:
                if node['ID'] == end_nodes_ID:
                    end_nodes_list.append(node['name'])
        else:
            end_nodes_list.append(end_nodes_ID)
        end_nodes_list = list(set(end_nodes_list))
        paths_info = {}
        path_ = {}
        paths_info['start_nodes'] = start_nodes
        path_['start_nodes'] = start_nodes
        paths_info['relationship'] = relationship_
        path_['relationship'] = relationship_
        paths_info['relationship_type'] = typeofrelationship
        paths_info['end_nodes'] = end_nodes_list
        path_['end_nodes'] = end_nodes_list
        paths_infos.append(paths_info)
        paths_.append(path_)
#    print(paths_)
    graph_relationships = list(set(graph_relationships))
    return graph_relationships, paths_infos,paths_


def subgraph_matching_algorithm():
    datagraph_nodes = 'datagraph_localnodes.txt'
    querygraph_nodes = 'querygraph_localnodes.txt'
    datagraph_nodes,datagraph_nodes_infos,datanodes_ = load_graph_localnodes(datagraph_nodes)
    querygraph_nodes,querygraph_nodes_infos,querynodes_ = load_graph_localnodes(querygraph_nodes)
#    print(querygraph_nodes_infos)
#    print(datagraph_nodes)
#    print(querygraph_nodes)    
    ########  compare nodes infos with datagraph and querygraph: If true, continue. If not 'It's not a subgraph'
    for node in querygraph_nodes:
        if node in datagraph_nodes:
            continue
        else:
            print("Data graph's nodes are: ",datagraph_nodes)
            print("Query graph's nodes are: ",querygraph_nodes)            
            return print('Query graph is not a subgraph of Data graph, query graph have new nodes')
    datagraph_paths = 'datagraph_localpaths.txt'
    querygraph_paths = 'querygraph_localpaths.txt'
    datagraph_relationships, datagraph_paths_infos,datapath_ = load_graph_localpaths(datagraph_paths,datagraph_nodes_infos,datanodes_)
    querygraph_relationships, querygraph_paths_infos,querypath_ = load_graph_localpaths(querygraph_paths,querygraph_nodes_infos,querynodes_)
   ##########  compare relationships with datagraph and querygraph: If true, continue. If not 'It's not a subgraph'
#    print( querygraph_paths_infos)
#    print(datagraph_relationships)
#    print(querygraph_relationships)
    for relationship in querygraph_relationships:
        if relationship in datagraph_relationships:
            continue
        else:
            print("Data graph's relationships are: ",datagraph_relationships)
            print("Query graph's relationships are: ",querygraph_relationships)
            return print('Query graph is not a subgraph of Data graph, query graph have new relationships')         
    for path in querypath_:
        if path in datapath_:
            continue
        else:
            return print('Query graph is not a subgraph of Data graph, query graph have different paths')
    return print('Query graph is a subgraph of Data graph')

funDict = {
    'inputdatagraph' : datagraph_input,
    'inputquerygraph': querygraph_input,
    'loaddatagraph' : datagraph_load,
    'loadquerygraph' : querygraph_load,
    'subgraphmatching' : subgraph_matching_algorithm

}

# get input params 

if (len(sys.argv) >= 2):
    functionName = str(sys.argv[1])
    if functionName in funDict:
        funDict[functionName]()
    else:
        text = "invalid function name %s" % (functionName)