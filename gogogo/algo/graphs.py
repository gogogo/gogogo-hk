import copy
import sys
import heapq

class Arc:
    def __init__ (self, weight=0 , data = None):
        self.src = None
        self.dest = None
        self.weight = weight
        self.data = data
        
    def link(self,src,dest):
        self.src = src
        self.dest = dest
        
        self.src.arcs.append(self)
        self.dest.arcs.append(self)
        
    def reverse(self):
        """
        Construct a reversed arc.
        """
        arc = copy.copy(self)
        tmp = arc.src 
        arc.src = arc.dest
        arc.dest = tmp
        return arc
        
    def copy(self):
        return copy.copy(self)
        
    def dump(self):
        return "%02d => %02d (%0.3f) " % (self.src.id , self.dest.id , self.weight)
        

class Node:
    def __init__(self,name = None, data = None):
        self.name = name
        self.data = None
        self.arcs = []
        
        # The id is the index of node in the graph , which will be 
        # assigned by graph.
        self.id = None

class Graph:
    
    def __init__(self):
        
        # An array of 3-tuple( node, arc with source equal to the node , 
        # arc with dest equal to the node )
        self.nodes = []
        
    def add_node(self,node):
        """
        Add a node to the graph
        """
        node.id = len(self.nodes)
        self.nodes.append( (node,[],[]) )

        return node.id
        
    def get_node(self,id):
        (ret,s,d) = self.nodes[id]
        return ret
        
    def get_node_detail(self,id):
        return self.nodes[id]
        
    def get_node_count(self):
        return len(self.nodes)
        
    def add_arc(self,arc):
       
        (src, src_arcs, tmp) = self.get_node_detail(arc.src.id)
        (dest, tmp, dest_arcs) = self.get_node_detail(arc.dest.id)
        
        src_arcs.append(arc)
        dest_arcs.append(arc)
        
    def clear_arc(self):
        """
        Clear all the arc from the graph
        """
        for (id,t) in enumerate(self.nodes):
            (node , src, dest) = self.nodes[id]
            self.nodes[id] = (node , [] , [])
        
    def get_arcs_from_src(self,src):
        if isinstance(src,int):
            (src, src_arcs, tmp) = self.get_node_detail(src)
        else:
            (src, src_arcs, tmp) = self.get_node_detail(src.id)
        return src_arcs
        
    def get_arcs_from_dest(self,dest):
        if isinstance(dest,int):
            (src, tmp , dest_arcs) = self.get_node_detail(dest)
        else:
            (src, tmp , dest_arcs) = self.get_node_detail(dest.id)
        return dest_arcs
        
    def contains(self,data):
        ret = False
        if isinstance(data,Arc):
            arcs = self.get_arcs_from_src(data.src)
            for arc in arcs:
                if arc == data:
                    ret = True
                    break
        return ret
        
    def reverse(self):
        """
        Construct a reversed graph
        """
        graph = self.copy()
        arcs = []
        
        for (id,t) in enumerate(graph.nodes):
            (node , src_arcs, dest_arcs) = graph.nodes[id]
            
            for arc in src_arcs:
                rarc = arc.reverse()
                arcs.append(rarc)
                
            graph.nodes[id] = (node , [] , [])
            
        for arc in arcs:
            graph.add_arc(arc)
            
        return graph
        
    def copy(self):
        graph = copy.copy(self)
        graph.nodes = copy.copy(self.nodes)

        return graph
        
    def dump(self):
        text = ""
        
        for (id,t) in enumerate(self.nodes):
            (node , src_arcs, dest_arcs) = t
            text += "Node: %s\nTo: " % node.name
            for arc in src_arcs:
                text += "%s (%0.3f) "  % (arc.dest.name , arc.weight)
            text+="\n"
        return text

if __name__ == "__main__":
	import doctest
	doctest.testmod(verbose=True)
