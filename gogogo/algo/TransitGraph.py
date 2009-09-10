# -*- coding: utf-8 -*-

from google.appengine.ext import db
from graphs import Graph , Node , Arc
from gogogo.models import *
from ragendja.dbutils import prefetch_references
import logging
from gogogo.models.loaders import ListLoader , FareStopLoader , TripLoader , AgencyLoader
from google.appengine.api import memcache

# Cache for whole day
#_default_cache_time = 3600 * 24

# Cache for 5 minutes only , for testing purpose
_default_cache_time = 300

class TransitArc(Arc):
    def __init__(self , **kwargs):
        self.agency = None
        self.trip = None
        
        if "agency" in kwargs:
            self.agency = kwargs["agency"]
            del kwargs["agency"]
            
        if "trip" in kwargs:
            self.trip = kwargs["trip"]
            del kwargs["trip"]
            
        Arc.__init__(self,**kwargs)
        
    def to_entity(self):
        entity = Arc.to_entity(self)
        
        if self.agency :
            entity["agency"] = self.agency

        if self.trip :
            entity["trip"] = self.trip         
            
        return entity
        
    def from_entity(self,graph,entity):
        self.agency = None
        self.trip = None
        
        Arc.from_entity(self,graph,entity)
        
        if "agency" in entity:
            self.agency = entity["agency"]
            
        if "trip" in entity:
            self.trip = entity["trip"]

class TransitGraph(Graph):
    """
    A graph built by transit information
    """
    
    cache_key = "gogogo_transit_graph"
    

    def create():
        """
        Try to load a instance from memcache, if not found,
        it will create a new transit graph.
        """
        entity = memcache.get(TransitGraph.cache_key)
        
        graph = TransitGraph()
        if entity == None:
            graph.load()
            memcache.add(TransitGraph.cache_key, graph.to_entity(), _default_cache_time)
        else:
            graph.from_entity(entity)
            
        return graph
        
    create = staticmethod(create)

    def __init__(self):
        Graph.__init__(self)
        
        # stop to cluster matching
        self.stop_to_cluster = {}
        
        # cluster's name to node id matching
        self.cluster_id = {}
        
    def get_node(self,key):
        """
        Override parent's get_node function. (Supported to search by 
        cluster name , key and instance)
        
        @param data The key
        
        @type data db.Key
        @type data int
        @type data basestring The key of cluster
        """
        if isinstance(key,int):
            id = key
        else:
            if isinstance(key,basestring):
                # The name of the cluster
                if isinstance(key,unicode): 
                    cluster = str(key)
                else:
                    cluster = key 
            elif isinstance(key,db.Key):
                cluster = key().id_or_name()
            else:
                cluster = key.key().id_or_name()
                
            id = self.cluster_id[cluster]
            
        return Graph.get_node(self,id)
        
    def get_node_by_stop(self,stop):
        if isinstance(stop,basestring):
           key = stop 
        elif isinstance(stop,db.Key()):
            key = stop.id_or_name()
        else:
            key = stop.key().id_or_name()
            
        return self.get_node(self.stop_to_cluster[key])
        
    def load(self):
        """
       Load graph from bigtable
        """
        
        route_list = []
        agency_list = []
        cluster_list = []
        trip_list = []
        
        query = Agency.all().filter("no_service = " ,False)
        
        for agency in query:
            agency_list.append(agency)
        
        # Load all the trip by using TripLoader
        trip_loader_list = []
        stop_table = {}
        limit = 1000
        entities = Trip.all(keys_only=True).fetch(limit)
        while entities:
            for key in entities:
                loader = TripLoader(key.id_or_name())
                loader.load(stop_table = stop_table)
                
                stop_list = loader.get_stop_list()
                for stop in stop_list:
                    stop_table [stop["id"]] = stop
                
                agency = loader.get_agency()
                
                if agency["free_transfer"] == False: # Ignore agency with free transfer service
                    trip_loader_list.append(loader)
                                
            entities = Trip.all(keys_only=True).filter('__key__ >', entities[-1]).fetch(limit)
                               
        #Load all cluster
        query = Cluster.all()
        for cluster in query:
            cluster_list.append(cluster)
            cluster_name = cluster.key().id_or_name()

            node = Node(name = cluster.key().id_or_name())

            # Cluster to ID matching            
            self.cluster_id [cluster.key().id_or_name()] = self.add_node(node)
            #logging.info(cluster.key().id_or_name())
            
            for key in cluster.members:
                name = key.id_or_name()
                if name in stop_table:
                    self.stop_to_cluster[name] = cluster_name
        
        # Process agency with "free_transfer"
        for agency in agency_list:
            if agency.free_transfer:
                logging.info("Processing " +agency.key().id_or_name())
                query = db.GqlQuery("SELECT __key__ from gogogo_farestop WHERE agency = :1 and default = True limit 1"
                    ,agency)
                key = query.get()
                if key == None:
                    continue
                farestop_loader = FareStopLoader(key.id_or_name())
                farestop_loader.load()
                farestop = farestop_loader.get_farestop()
                
                pair_list = farestop_loader.get_pair_list()
                
                for pair in pair_list:        
                    a = self.get_node_by_stop(pair["from_stop"])
                    b = self.get_node_by_stop(pair["to_stop"])
                    
                    #TODO , don't save entity in graph , reduce the memory usage
                    arc = TransitArc(agency = agency.key().id_or_name() ,weight = pair["fare"] )
                    arc.link(a,b)
                    self.add_arc(arc)
        
        # Process trip not in agency with free_transfer service
        for loader in trip_loader_list:
            trip = loader.get_trip()
            agency = loader.get_agency()
                
            logging.info(trip["id"])                
            cluster_group = {}
            
            faretrip = loader.get_default_faretrip()

            if faretrip == None: # No default faretrip data found
                continue
            
            for id in trip["stop_list"]:
                logging.info(id)
                try:
                    to_stop = stop_table[id]
                except KeyError:
                    logging.error( "Stop(%s) not found" % id)
                    continue
                
                cluster_name = self.stop_to_cluster[to_stop["id"]]
                if cluster_name not in cluster_group: # ignore self-looping
                    
                    for from_cluster_name in cluster_group:
                        logging.info("%s to %s" % (from_cluster_name ,cluster_name))
                        a  = self.get_node(from_cluster_name)
                        b  = self.get_node(cluster_name)
                        
                        # Ignore weight in testing phase
                        #TODO , don't save entity in graph , reduce the memory usage
                        arc = TransitArc(agency=agency["id"],trip = trip["id"] ,weight = loader.calc_fare(
                            cluster_group[from_cluster_name] , id) )
                            
                        arc.link(a,b)
                        self.add_arc(arc)       
                    
                    cluster_group[cluster_name] = id
                        
    def to_entity(self):
        entity = Graph.to_entity(self)
        
        entity["stop_to_cluster"] = self.stop_to_cluster
        entity["cluster_to_node_id"] = self.cluster_id
        return entity
        
    def from_entity(self,entity):
        Graph.from_entity(self,entity,arcClass = TransitArc)
        
        self.stop_to_cluster = entity["stop_to_cluster"]
        self.cluster_id = entity["cluster_to_node_id"]
        
class StopGraph(Graph):
    """
    A graph built by stop for an agency
    """
    
    cache_key = "gogogo_stop_graph_"

    def get_cache_key(id):
        return StopGraph.cache_key + id
        
    get_cache_key = staticmethod(get_cache_key)

    def create(id):
        """
        Try to load a instance from memcache, if not found,
        it will create a new transit graph.
        """
        entity = memcache.get(StopGraph.get_cache_key(id))
        
        graph = StopGraph(id)
        if entity == None:
            graph.load()
            memcache.add(StopGraph.get_cache_key(id), graph.to_entity(), _default_cache_time)
        else:
            graph.from_entity(entity)
            
        return graph
        
    create = staticmethod(create)
    
    def __init__(self,id):
        Graph.__init__(self)
        self.id = id
        
    def load(self):
        """
       Load from database or bigtable
        """
        agency_loader = AgencyLoader(self.id)
        agency_loader.load()
        
        trip_id_list = agency_loader.get_trip_id_list()
        
        trip_loader_list = []
        stop_table = {}
        
        for trip_id in trip_id_list:
            trip_loader = TripLoader(trip_id)
            trip_loader.load(stop_table = stop_table)
            trip_loader_list.append(trip_loader)
            
            prev_node = None
            
            for stop in trip_loader.get_stop_list():
                node = self.search_node(stop["id"])
                if node == None:
                    node = Node(name = stop["id"])
                    self.add_node(node)
                    
                if prev_node:
                    arc = Arc(weight = 1)
                    arc.link(prev_node,node)
                    self.add_arc(arc)
                
                prev_node = node
        
        #TODO support transfer model
            
        
        
        
        
        
        
