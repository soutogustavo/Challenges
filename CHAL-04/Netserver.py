# -*- coding: utf-8 -*-

import networkx as ntx
from flask import Flask, render_template, request
from flask_restful import Api, Resource
import json
import numpy as np
import operator
import matplotlib.pyplot as plt

app = Flask(__name__)
api = Api(app)

#####################################################################
# VARIABLES AND OTHER FUNCTIONS
#####################################################################
nodes = {}
edges = []
resp = {}
#GPH = ntx.Graph()

# PARSE STR INTO INT ##########
def parser_srt_to_int(s):
    try:
        val = int(s)
        return (val, True)
    except ValueError:
        return (False,False)

# REMOVE NODES THAT DOES NOT HAVE EDGES
def pruneNodes(nlist):
    global nodes
    global edges
    for o in nlist[:]:
        ver = 0
        for e in edges[:]:
            if o in e:
                ver += 1
        if ver == 0:
            del nodes[o]

# COMPUTE CLOSENESS
def comp_closeness(G, nds):
    for n in nds:
        spl = ntx.shortest_path_length(G, source=n).values()
        sum_spl = np.sum(spl)
        spl_mean = np.mean(spl)
        nodes[n] = (1 / float(spl_mean))

#####################################################################
#####################################################################


#####################################################################
# CLASSES
#####################################################################

# ------
# NODES 
# ------
class Nodes(Resource):
    def get(self, node):
        if node in nodes:        
            return json.dumps({"node":nodes[node]})
        else:
            return json.dumps({"node":"This node does not exist!"})
        
    def put(self, node):
        if node not in nodes:
            nodes[node] = request.form['data']
            return json.dumps({"resp":"Node added successfuly!"})
        else:
            return json.dumps({"resp":"This node already exists!"})
            
    def delete(self, node):
        if node in nodes:
            del nodes[node]

            orphans = []
            for i in edges[:]:
                if node in i:
                    edges.remove( [i[0],i[1]] )
                    if node != i[0]:
                        orphans.append(i[0])
                    else:
                        orphans.append(i[1])

            # REMOVE NODES THAT DOES NOT HAVE EDGES
            pruneNodes(orphans)

            return json.dumps({"resp":"Node deleted successfuly!"})          
        else:
            return json.dumps({"resp":"This node does not exist!"})

# ------
# EDGES 
# ------
class Edges(Resource):
    
    def get(self, edge):
        return "Edge ({})---({})".format(edge[0],edge[1])

    def put(self):
        vert1 = request.form['vert1']
        vert2 = request.form['vert2']

        # PARSE VERTICES
        val1, log1 = parser_srt_to_int(vert1)
        val2, log2 = parser_srt_to_int(vert2)

        if [val1, val2] not in edges:

            
            # BEFORE STORING WE MUST VERIFY IF THE VALUES ARE INTEGERS
            if log1: # FIRST VERIFICATION
                if log2: # SECOND VERIFICATION
                    edges.append( [val1, val2] )
                                    
                    if val1 not in nodes:
                        nodes[val1] = 0
                    if val2 not in nodes:
                        nodes[val2] = 0
                        
                    return json.dumps({"resp":"Edge added successfuly!"})
                else:
                    return json.dumps({"resp":"Vertice 2 is not a number!"})  
            else:
                return json.dumps({"resp":"Vertice 1 is not a number!"})
            
        else:
            return "This edge already exists!"
            
    def delete(self):
        
        vert1 = request.form['vert1']
        vert2 = request.form['vert2']
         
        #PARSE VERTICES
        val1,log1 = parser_srt_to_int(vert1)
        val2,log2 = parser_srt_to_int(vert2)
            
        if [val1,val2] in edges:
            edges.remove( [val1, val2] )
            return json.dumps({"resp":"Edge deleted successfuly!"})
        else:
            return json.dumps({"resp":"This edge does not exist!"})        
    
# ----------------
# CLOSENESS 
# ----------------
class Closeness(Resource):

    def get(self):
        global GPH
        if len(nodes) != 0:
            if len(nodes) > 1:
                if len(edges) > 0:

                    pruneNodes(nodes.keys())

                    G = ntx.Graph()
                    G.add_nodes_from(nodes.keys())
                    G.add_edges_from(edges)
                    comp_closeness(G,nodes.keys())
                    ntx.draw_networkx(G)
                    plt.savefig("static/graph.png", format="PNG")
                    #GPH = G

                    sorted_nodes = sorted(nodes.items(), key=operator.itemgetter(1))
                    return sorted_nodes
                else:
                    return json.dumps({"resp": "more"})

            else:
                return json.dumps({"resp": "more"})
        else:
            return json.dumps({"resp": "There are not Nodes!"})

# ----------------
# DELETE ALL NODES 
# ----------------
class DeleteAllNodes(Resource):     
    def delete(self): # deleteAll
        if len(nodes) != 0:
            nodes.clear()
            edges[:] = []
            return json.dumps({"resp":"All nodes were deleted!"})

# ----------------
# DELETE ALL EDGES 
# ----------------
class DeleteAllEdges(Resource):
    global edges
    def delete(self): # deleteAll
        if len(edges) != 0:
            edges[:] = []

            # CLEAR ALSO THE NODES
            nodes.clear()
            return json.dumps({"resp":"All edges were deleted!"})
        else:
            return json.dumps({"resp":"No edges to be deleted!"})

# ----------------
# LIS OF ALL NODES 
# ----------------
class ListNodes(Resource):    
    def get(self):
        return nodes

# ----------------
# LIS OF ALL EDGES 
# ----------------
class ListEdges(Resource):    
    def get(self):
        return edges

#####################################################################

# SHOW THE GRAPH AS AN IMAGE ON BROWSER
@app.route("/graph.html")
def show_graph():
    return render_template("graph.html", name="graph")

# IT PLOTS THE GRAPH BY USING MATPLOTLIB
@app.route("/getgraph")
def getgraph():
    plt.title("Social Network")
    plt.show()
    return json.dumps({"resp":"Plot graph"})

#####################################################################


#####################################################################
# RESOURCES
#####################################################################

# NODES
api.add_resource(Nodes, '/node/<int:node>', endpoint="get_node")
api.add_resource(Nodes, '/node/add/<int:node>', endpoint="add_node")
api.add_resource(Nodes, '/node/del/<int:node>', endpoint="del_node")

# EDGES
api.add_resource(Edges, '/edge/<int:edge>', endpoint="get_edge")
api.add_resource(Edges, '/edge/add/', endpoint="add_edge")
api.add_resource(Edges, '/edge/del/', endpoint="del_edge")

#CLOSSENESS
api.add_resource(Closeness, '/closeness', endpoint="closeness")

# LIST ALL NODES AND EDGES
api.add_resource(ListNodes, '/nodes/')
api.add_resource(ListEdges, '/edges/')

# DELETE ALL NODES AND EDGES
api.add_resource(DeleteAllNodes, '/nodes/delall')
api.add_resource(DeleteAllEdges, '/edges/delall')

#####################################################################
#####################################################################

if __name__ == '__main__':
    app.run(debug=True)
