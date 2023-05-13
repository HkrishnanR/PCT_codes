import pandas as pd
import networkx as nx
from collections import defaultdict
import random
from tqdm import tqdm
import json
import sys
import networkx.algorithms.community as nx_comm

centralityMeasures={}

centrality=lambda x: centralityMeasures.setdefault(x.__name__,x) # Can be Rewritten as: def centrality(func):
                                                                  #                          centralityMeasures[func.__name__]= func;
                                                                  #  func--> pointer to function; func.__name__ --> name of function 
                                                                  # Where centralityMeasures is a dict


@centrality # calling the decorator to decorate the below defined function
def linkdensity(Graph):
    try:
       return nx.density(Graph)
    except:
       return None    


@centrality
def transitivity(Graph):
    try:
       return nx.transitivity(Graph)
    except:
       return None

@centrality
def assortativity(Graph):
    try:
      return nx.degree_assortativity_coefficient(Graph)
    except:
      return None 

@centrality
def diameter(Graph):
    try:
      return nx.diameter(Graph)
    except:
      return None 

@centrality
def maximumdegree(Graph):
    try:
       return sorted(Graph.degree, key=lambda x: x[1], reverse=True)[0]
    except:
       return None

@centrality
def smallworldness(Graph): # defined as sigma = (C/Cr)/(L/Lr) --> C --> Avg clust coeff, Cr ---> Avg clust coeff of equivalent random graph. L, Lr --> Similarly shortest path
    try:
        return nx.sigma(Graph)
    except:
       return None

@centrality
def efficiency(Graph):
    try:
       return nx.global_efficiency(Graph)
    except:
       return None

@centrality
def modularity(Graph):
    try:
       return nx_comm.modularity(Graph, nx_comm.label_propagation_communities(Graph))
    except:
       return None



def checkFileSanity(fname):
    
    file=pd.read_csv(f"{fname}",sep="\t")

    if file.shape[1]!=2:
        print("Ensure that the file is in the correct format")
        sys.exit()
    
    if file.shape[1]==2:
        file.columns=["InteractorA","InteractorB"]
    return file


#Global topology;  

def NetworkDismantling(Graph,nodelist):       
    # Structure of output(JSON) --> {
    #                               Node1:  {"Cm1": {},"Cm2":{}} .. },
                                    # Node2: {"Cm1": {}},"Cm2":{}} .. } . || Segment based on PCT vs non PCT --> 
    #                                   }

    #outJSON --> Segment into PCT vs NonPCT --> plot 

# Dsitribution (Cm) --> segment the distribution, 

    random.shuffle(nodelist)
    
    scoredict=defaultdict(dict)

    covered=[]
    
    for ind,randomNode in tqdm(enumerate(nodelist),desc=f"Running Network Dismantling for {sys.argv[1]} file"):

        modGraph=Graph.copy()
        modGraph.remove_node(randomNode)
        if randomNode not in covered:          
            for cm in centralityMeasures:
                scoredict[randomNode][cm]=centralityMeasures[cm](modGraph)
            covered.append(randomNode)
        del modGraph

        if len(covered)==len(nodelist):
            print("Covered all nodes")
        else:
            print(f"Covered {len(covered)} out of {len(nodelist)} Nodes")
    return scoredict




def ConstructNetwork():
    
    if len(sys.argv)>1:

        df=checkFileSanity(sys.argv[1])
        print(df)

        nodeList=list(set(df["InteractorA"].unique().tolist() + df["InteractorB"].unique().tolist()))
        edgeList = [elem for elem in list(zip(df["InteractorA"],df["InteractorB"]))]

        G=nx.Graph()
        G.add_nodes_from(nodeList)
        G.add_edges_from(edgeList)
        #print(len(G.nodes()))
        return G , nodeList
    else:
        print("Provide input file:: python net_dismantling.py filename")
        sys.exit()


if __name__=="__main__":
    
    G,nodelist=ConstructNetwork()
    print(len(G.nodes()))

    
    output=NetworkDismantling(G,nodelist)

    with open("Network_dismantling.json","w") as fname:
        json.dump(output,fname)

    print("File Saved!!")











