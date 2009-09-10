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

    def to_entity(self):
        """
       Convert the arc to entity format
        """
        
        src = None
        dest = None
        if self.src:
            src = self.src.id
        
        if self.dest:
            dest = self.dest.id
        
        entity = {
            "src" : src, # Save the ID instead of the instance
            "dest" : dest,
            "weight" : self.weight,
        }
        return entity
        
    def from_entity(self,graph,entity):
        """
        Set from entity
        """
        self.arcs = []
        
        src = graph.get_node(entity["src"])
        dest = graph.get_node(entity["dest"])
        self.weight = entity["weight"]
        self.link(src,dest)

class Node:
    def __init__(self,name = None, data = None):
        """
        @param name The name of the node
        """
        self.name = name
        self.data = None
        self.arcs = []
        
        # The id is the index of node in the graph , which will be 
        # assigned by graph.
        self.id = None
        
    def __eq__(self,other):
        if other == None:
            return False
        if self.id == other.id:
            return True
        return False
        
    def __cmp__(self,other):
        if self.id > other.id:
            return 1
        elif self.id == other.id:
            return 0
        return -1
        
    def to_entity(self):
        """
       Convert the node to entity format
       
       >>> print Node(name = "Test" ).to_entity()
       {'name': 'Test', 'id': None}
        """
        entity = {
            "name" : self.name,
            "id" : self.id,
        }
        return entity
        
    def from_entity(self,entity):
        """
        Set from entity
        """
        self.arcs = []
        self.name = entity["name"]
        self.id = entity["id"]

class Graph:
    
    def __init__(self):
        
        # An array of 3-tuple( node, arc with source equal to the node(outgoing) , 
        # arc with dest equal to the node (incoming))
        self.nodes = []
        
    def clear(self):
        """
        Clear the graph
        """
        self.nodes = []
        
    def add_node(self,node):
        """
        Add a node to the graph
        """
        node.id = len(self.nodes)
        self.nodes.append( (node,[],[]) )

        return node.id
        
    def add_node_by_id(self,node,id):
        self.nodes[id] = (node,[],[])
        
    def get_node(self,id):
        (ret,s,d) = self.nodes[id]
        return ret
        
    def get_node_detail(self,id):
        """
        Return the 3-tuple internal data storage of a node with ID
        """
        return self.nodes[id]
        
    def get_node_count(self):
        return len(self.nodes)
        
    def get_all_nodes(self):
        """
        Get all the nodes
        """
        return [node for (node,out_arcs,in_arcs) in self.nodes]
        
    def add_arc(self,arc):
       
        (src, src_arcs, tmp) = self.get_node_detail(arc.src.id)
        (dest, tmp, dest_arcs) = self.get_node_detail(arc.dest.id)
        
        src_arcs.append(arc)
        dest_arcs.append(arc)
        
    def search_arcs(self,src,dest):
        """
        Search arcs by giving the ID/Node instance of source and dest node
        
        @type src int
        @type src Node
        """
        ret = []
        if isinstance(dest,int):
            dest = self.get_node(int)
        
        arcs = self.get_arcs_from_src(src)
        for arc in arcs:
            if arc.dest == dest:
                ret.append(arc)
                
        return ret
        
    def search_node(self,name):
        """
       Search node by name
        """
        ret = None
        for t in self.nodes:
            (node,out_arcs,in_arcs) = t
            if node.name == name:
                return node
        
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

    def get_all_arcs(self):
        """
        Get all the nodes
        """
        arcs = []
        for (node,out_arcs,in_arcs) in self.nodes:
            arcs += out_arcs
        return arcs
        
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
        
    def to_entity(self):
        """
       Convert the graph to entity format
        """
        
        nodes = self.get_all_nodes()
        arcs = self.get_all_arcs()
        
        nodes_entity = [node.to_entity() for node in nodes]
        arcs_entity = [arc.to_entity() for arc in arcs]
        
        return {
            "nodes" : nodes_entity,
            "arcs" : arcs_entity
        }
        
    def from_entity(self,entity,arcClass = Arc):
            
        self.clear()
        
        nodes_entity = entity["nodes"]
        arcs_entity = entity["arcs"]
        
        nodes = []
        for entity in nodes_entity:
            node = Node()
            node.from_entity(entity)
            nodes.append(node)
        
        self.nodes = [None] * len(nodes)
        for node in nodes:
            self.add_node_by_id(node,node.id)
            
        for entity in arcs_entity:
            arc = arcClass()
            arc.from_entity(self,entity)
            self.add_arc(arc)

if __name__ == "__main__":
	import doctest
	doctest.testmod(verbose=True)
