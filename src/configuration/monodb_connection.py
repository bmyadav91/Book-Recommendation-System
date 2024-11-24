import os
import sys
from src.exception import CustomException
from src.logger import logging
from pymongo import MongoClient

mongo_client = os.getenv("MONGO_DB_URL")
database_name = "pw-practice"
collection_name = "book-recommendation"

LoadedMongoConnection = None

def connect_to_mongo():
    global LoadedMongoConnection
    if LoadedMongoConnection is None:
        try:
            client = MongoClient(mongo_client)
            db = client[database_name]
            LoadedMongoConnection = db[collection_name]
            logging.info("Successfully connected to MongoDB.")
        except Exception as e:
            logging.error(f"Error connecting to MongoDB: {e}")
            raise CustomException(f"Failed to connect to MongoDB: {str(e)}", sys)
    return LoadedMongoConnection


