"""
Shortest path and related algorithm
"""
import copy
import sys
import heapq
from graphs import Node

def mst(graph,src):
    """
    Construct a MST from a src point on a graph
    
    @return 2-tuple of (backtrack of mst,weights : the cost from src to another node)
    """
    
    if isinstance(src,int):
        src_id = src
        src = graph.get_node(src_id)
    else:
        src_id = src.id

    count = graph.get_node_count()
    
    # The weights from src to any point
    weights = [sys.maxint] * count
    visited = [ False ] * count
    
    weights[src_id] = 0
    
    # For arc back tracking that rect the node. (Used to construct MST)
    backtrack = [None ] * count
    heap = [ (0,src_id) ]
            
    while len(heap) > 0:
        
        active = -1 # The index of current processing node
        while len(heap) > 0:
            (w,index) = heapq.heappop(heap)
            if visited[index] == False:
                visited[index] = True
                active = index
                break;
                
        if active < 0:
            break
            
        arcs = graph.get_arcs_from_src(active)
        for arc in arcs:
            new_weight = arc.weight + weights[active]
            if new_weight < weights[arc.dest.id]:
                weights[arc.dest.id] = new_weight;
                backtrack[arc.dest.id] = arc     
                heapq.heappush(heap, (new_weight,arc.dest.id))
        
    return backtrack,weights
