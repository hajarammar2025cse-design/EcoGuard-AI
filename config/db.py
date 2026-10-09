"""
MongoDB Connection and Database Management Layer
Provides robust client connection, collection references, index initialization,
and document serialization utilities.
"""
import os
import pymongo
from bson import ObjectId
from datetime import datetime
from django.conf import settings

_client = None
_db = None

def get_db():
    """
    Returns the active MongoDB database instance.
    Utilizes lazy singleton connection pooling.
    """
    global _client, _db
    if _db is not None:
        return _db

    mongo_uri = getattr(settings, 'MONGO_URI', os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
    db_name = getattr(settings, 'MONGO_DB_NAME', os.getenv('MONGO_DB_NAME', 'environmental_monitoring_db'))

    try:
        _client = pymongo.MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=3000,
            connectTimeoutMS=3000,
            maxPoolSize=50
        )
        # Verify connection
        _client.admin.command('ping')
        _db = _client[db_name]
        return _db
    except Exception as e:
        # Re-raise so calling views/services can handle gracefully
        raise ConnectionError(f"Unable to connect to MongoDB at {mongo_uri}: {str(e)}")

def check_db_connection():
    """
    Health check utility to verify MongoDB operational status.
    Returns (is_connected: bool, message: str)
    """
    try:
        db = get_db()
        db.command('ping')
        return True, "MongoDB connected successfully"
    except Exception as e:
        return False, str(e)

# Collection Accessors
def get_users_col():
    return get_db()['users']

def get_locations_col():
    return get_db()['locations']

def get_env_data_col():
    return get_db()['environmental_data']

def get_hazards_col():
    return get_db()['hazards']

def get_predictions_col():
    return get_db()['predictions']

def get_alerts_col():
    return get_db()['alerts']

def init_mongo_indexes():
    """
    Ensures optimal indexes exist across all required collections.
    """
    try:
        db = get_db()
        # Users
        db['users'].create_index([('username', pymongo.ASCENDING)], unique=True)
        db['users'].create_index([('email', pymongo.ASCENDING)])

        # Locations
        db['locations'].create_index([('location_name', pymongo.ASCENDING)], unique=True)
        db['locations'].create_index([('status', pymongo.ASCENDING)])

        # Environmental Data
        db['environmental_data'].create_index([('location', pymongo.ASCENDING), ('timestamp', pymongo.DESCENDING)])
        db['environmental_data'].create_index([('timestamp', pymongo.DESCENDING)])

        # Hazards
        db['hazards'].create_index([('status', pymongo.ASCENDING), ('hazard_type', pymongo.ASCENDING)])
        db['hazards'].create_index([('detected_time', pymongo.DESCENDING)])

        # Predictions
        db['predictions'].create_index([('hazard_type', pymongo.ASCENDING), ('timestamp', pymongo.DESCENDING)])
        db['predictions'].create_index([('location', pymongo.ASCENDING)])

        # Alerts
        db['alerts'].create_index([('status', pymongo.ASCENDING), ('timestamp', pymongo.DESCENDING)])
        db['alerts'].create_index([('severity', pymongo.ASCENDING)])
        return True
    except Exception as e:
        print(f"Index initialization warning: {e}")
        return False

def serialize_doc(doc):
    """
    Converts MongoDB document to JSON-serializable Python dictionary,
    converting ObjectId to string and formatting datetimes.
    """
    if doc is None:
        return None
    res = dict(doc)
    if '_id' in res:
        res['id'] = str(res['_id'])
        del res['_id']
    for k, v in res.items():
        if isinstance(v, ObjectId):
            res[k] = str(v)
        elif isinstance(v, datetime):
            res[k] = v.strftime('%Y-%m-%d %H:%M:%S')
    return res

def serialize_docs(docs):
    """
    Converts an iterable of MongoDB documents to a list of serialized dictionaries.
    """
    return [s for d in docs if (s := serialize_doc(d)) is not None]
