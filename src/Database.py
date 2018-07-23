'''
Created on Jul 20, 2018

@author: Vishruth
'''
from pymongo import MongoClient

class Database(object):
    '''
    classdocs
    '''
    username = "root"
    password = "ACDRCbAEh8PJ"
    ip = "35.197.117.131"
    port = "27017"
    dbname = "gt-1"
    collectionname = "annotations"
    annotations = None
    
    @staticmethod
    def connect_to_db():
        client = MongoClient('mongodb://%s:%s@%s:%s/' % (Database.username, Database.password, Database.ip, Database.port))
        db = client[Database.dbname]
        Database.annotations = db[Database.collectionname]
    
    @staticmethod
    def add_document_to_db(video_id, timestamp_ms, class_name, object_id, xmin, xmax, ymin, ymax):
        '''
        returns: whether or not DB operation was successful
        '''
        if Database.annotations == None:
            Database.connect_to_db()
        
        if not Database.annotations:
            return False
        
        annotation = {"video_id": video_id,
                      "timestamp_ms": timestamp_ms,
                      "class_name": class_name,
                      "object_id": object_id,
                      "xmin": xmin,
                      "xmax": xmax,
                      "ymin": ymin,
                      "ymax": ymax}
        
        Database.annotations.insert_one(annotation)
    
    @staticmethod
    def list_all_video_ids():
        if Database.annotations == None:
            Database.connect_to_db()
        
        if Database.annotations:
            return Database.annotations.distinct("video_id")
        else:
            return None
    
    @staticmethod
    def get_all_segments_for_object(class_name):
        if Database.annotations == None:
            Database.connect_to_db()
        
        if Database.annotations:
            return Database.annotations.find({"class_name": class_name})
        else:
            return None
    
    @staticmethod
    def get_all_segments_by_time(video_id, start_time, end_time):
        if Database.annotations == None:
            Database.connect_to_db()
        
        start_time_ms, end_time_ms = start_time*1000, end_time*1000
        
        if Database.annotations:
            return Database.annotations.find({"video_id": video_id, "timestamp_ms": {"$gte": start_time_ms, "$lte": end_time_ms}})
        else:
            return None
    
    @staticmethod
    def clear_all_documents_from_db():
        if Database.annotations == None:
            Database.connect_to_db()
        
        if Database.annotations:
            Database.annotations.drop()
            return True
        else:
            return False