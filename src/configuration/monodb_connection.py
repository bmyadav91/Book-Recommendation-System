import os
import sys
from src.exception import CustomException
from src.logger import logging
from pymongo import MongoClient

mongo_client = os.getenv("MONGO_DB_URL")
database_name = "pw-practice"
collection_name = "book-recommendation"

def connect_to_mongo():
    try:
        # Connect to MongoDB
        client = MongoClient(mongo_client)
        db = client[database_name]
        collection = db[collection_name]
        return collection
    except Exception as e:
        logging.info(f"Error connecting to MongoDB: {e}")
        raise CustomException(f"Failed to connect to MongoDB: {str(e)}", sys)


