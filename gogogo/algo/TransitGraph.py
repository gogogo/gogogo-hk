# -*- coding: utf-8 -*-

from google.appengine.ext import db
from graphs import Graph , Node , Arc
from gogogo.models import *
from ragendja.dbutils import prefetch_references
import logging
from gogogo.models.loaders import ListLoader , FareStopLoader , TripLoader

class TransitGraph(Graph):
    """
    A graph built by transit information
    """

    def create():
        """
        Try to load a instance from memcache, if not found,
        it will create a new transit graph.
        """
        #TODO - Enable memcache
        graph = TransitGraph()
        graph.load()
        return graph
        
    create = staticmethod(create)

    def __init__(self):
        Graph.__init__(self)
        self.agency_table = {}
        #self.stop_table = {}
        self.cluster_table = {}
        self.route_table = {}
        self.trip_table = {}
        
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
       Load graph from database
        """
        
        route_list = []
        agency_list = []
        cluster_list = []
        trip_list = []
        
        # TODO : Replace by ListLoader
        # For testing
        query = Agency.all().filter("no_service = " ,False)
        
        for agency in query:
            self.agency_table[agency.key().id_or_name()] = agency
            agency_list.append(agency)
        
        # TODO: Dump all route
        #query = Route.all()
        #for route in query:
            #route_list.append(route)
            #self.route_table[route.key().id_or_name() ] = route
            
        #prefetch_references(route_list,"agency",agency_list)

        # Load all the trip
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
                
                if agency["free_transfer"] == False: # Ignore free transfer trip
                    trip_loader_list.append(loader)
                                
            entities = Trip.all(keys_only=True).filter('__key__ >', entities[-1]).fetch(limit)
                        
        prefetch_references(trip_list,"route",route_list)
        
        query = Cluster.all()
        for cluster in query:
            cluster_list.append(cluster)
            cluster_name = cluster.key().id_or_name()
            self.cluster_table[cluster_name] = cluster

            node = Node(name = cluster.key().id_or_name())

            # Cluster to ID matching            
            self.cluster_id [cluster.key().id_or_name()] = self.add_node(node)
            #logging.info(cluster.key().id_or_name())
            
            for key in cluster.members:
                name = key.id_or_name()
                if name in stop_table:
                    self.stop_to_cluster[name] = cluster
        
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
                    arc = Arc(data = (agency,farestop) ,weight = pair["fare"] )
                    arc.link(a,b)
                    self.add_arc(arc)
        
        # Process trip not in agency with free_transfer service
        for loader in trip_loader_list:
            trip = loader.get_trip()
                
            logging.info(trip["id"])                
            cluster_group = {}
            
            for id in trip["stop_list"]:
                logging.info(id)
                try:
                    to_stop = stop_table[id]
                except KeyError:
                    logging.error( "Stop(%s) not found" % id)
                    continue
                
                cluster = self.stop_to_cluster[to_stop["id"]]
                cluster_name = cluster.key().id_or_name()
                if cluster_name not in cluster_group: # ignore self-looping
                    
                    for from_cluster_name in cluster_group:
                        logging.info("%s to %s" % (from_cluster_name ,cluster_name))
                        a  = self.get_node(from_cluster_name)
                        b  = self.get_node(cluster_name)
                        
                        # Ignore weight in testing phase
                        #TODO , don't save entity in graph , reduce the memory usage
                        arc = Arc(data= trip)
                        arc.link(a,b)
                        self.add_arc(arc)       
                    
                    cluster_group[cluster_name] = cluster;
                        

        
