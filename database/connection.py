from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError,ConnectionFailure
from pymongo.database import Database
import typing

global db_instance
db_instance = None

def connect_db(uri:str="mongodb://mongo:27017")->Database:

    global db_instance

    if db_instance is None:
        try:
            client = MongoClient(uri,serverSelectionTimeoutMS=6000)
            db_instance = client["chat-server"]

        except ServerSelectionTimeoutError:
            raise ConnectionFailure("MongoDB server is not reachable, ensure docker container is running")

        except ConnectionFailure as e:
            raise ConnectionFailure(f"Failed to connect to MongoDB{e}")


    return db_instance


def return_db():

    if db_instance is None:
        return connect_db()

    return db_instance


def get_db(uri="mongodb://mongo:27017", db_name="chat-server"):
    """Get database connection (alias for compatibility)."""
    return connect_db(uri)