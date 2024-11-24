import pickle
import io, os, sys
import pandas as pd
from src.configuration.s3_config import s3_bucket_connection
from src.configuration.monodb_connection import connect_to_mongo
from src.exception import CustomException
from src.logger import logging
from flask import jsonify
from settings import folder_name


bucket_name = os.getenv("AWS_BUCKET")

# Load from S3
def load_from_s3(file_name):
    try:
        s3_client = s3_bucket_connection()
        full_path = f"{folder_name}/{file_name}"
        file_stream = io.BytesIO()
        s3_client.download_fileobj(bucket_name, full_path, file_stream)
        file_stream.seek(0)
        return pickle.load(file_stream)
    except Exception as e:
        return None



def db_data_frame():
    """
    Load data from the MongoDB collection into a DataFrame.
    """
    try:
        # Connect to MongoDB
        collection = connect_to_mongo()
        
        # Fetch all documents
        data = list(collection.find())
        
        if not data:
            raise CustomException("No data found in the MongoDB collection.", sys)
        
        # Convert to DataFrame
        return pd.DataFrame(data)
    except Exception as e:
        logging.error(f"Error loading data from MongoDB: {str(e)}")
        raise CustomException(str(e), sys)


# Lazy loading of database
class DataLoader:
    def __init__(self):
        self.dataframe = None
        self.mongo_data = None

    def load_dataframe(self):
        if self.dataframe is None:
            self.dataframe = db_data_frame()
        return self.dataframe

    def load_mongo_data(self):
        if self.mongo_data is None:
            collection = connect_to_mongo()
            self.mongo_data = list(collection.find())
        return self.mongo_data

data_loader = DataLoader()

class Access_Data:
    def __init__(self):
        self.loaded_resources = {}

    def get_resource(self, variable, resource_name):
        if variable not in self.loaded_resources:
            try:
                logging.error(f"Loading resource: {resource_name}")
                self.loaded_resources[variable] = load_from_s3(resource_name)
            except Exception as e:
                logging.error(f"Error in {str(e)}")
                self.loaded_resources[variable] = None
        return self.loaded_resources[variable]

    def find_similar_genre(self, input_genre, book_id, top_n=5):
        try:
            self.genre_vectorizer = self.get_resource('genre_vectorizer','genre_vectorizer.pkl')
            self.genre_knn = self.get_resource('genre_knn','genre_knn.pkl')
            if not input_genre:
                return jsonify({'message': 'Genre is None for this book'}), 400

            if not self.genre_vectorizer or not self.genre_knn:
                raise CustomException("Models not initialized.", sys)

            # Transform the genre into a vector
            genre_matrix = self.genre_vectorizer.transform([input_genre])
            distances, indices = self.genre_knn.kneighbors(genre_matrix, n_neighbors=top_n)

            # Use data loader
            dataframe = data_loader.load_dataframe()

            # Get the recommended book indices
            results = indices.flatten()

            # Fetch recommended books
            results = dataframe.iloc[results].copy()

            # Add similarity score
            results['similarity'] = 1 - distances.flatten()[:len(results)]

            # Filter out results with 0 similarity
            results = results[results['similarity'] > 0]

            # Exclude the given book_id
            results = results[results['book_id'] != book_id]

            # If no results found after filtering, return a message
            if results.empty:
                return jsonify({"message": "No results found"}), 404

            results_json = []
            for _, row in results.iterrows():
                book_data = {
                    "Title": row.get("Title", "Unknown Title"),
                    "Author": row.get("Author", "Unknown Author"),
                    "Publisher": row.get("Publisher", "Unknown Publisher"),
                    "similarity": row["similarity"],
                    "book_id": int(row.get("book_id", 0)),
                    "Genre": row.get("Genre", "Unknown Genre"),
                }
                results_json.append(book_data)

            return results_json
        except Exception as e:
            logging.error(f"Error finding genres: {e}")
            raise CustomException(str(e), sys)

        
    def search_book(self, query, top_n=5):
        try:
            self.title_vectorizer = self.get_resource('title_vectorizer','title_vectorizer.pkl')
            self.title_knn = self.get_resource('title_knn','title_knn.pkl')
            if not self.title_vectorizer or not self.title_knn:
                raise CustomException("Models not initialized.", sys)

            # Transform the query into a vector
            query_vector = self.title_vectorizer.transform([query])
            # Get distances and indices for the nearest neighbors
            distances, indices = self.title_knn.kneighbors(query_vector, n_neighbors=top_n)

            dataframe = data_loader.load_dataframe()

            results = dataframe.iloc[indices.flatten()].copy()
            results['similarity'] = 1 - distances.flatten()
            # Filter out results with 0 similarity
            results = results[results['similarity'] > 0]

            # If no results found after filtering, return a message
            if results.empty:
                return jsonify({"message": "No results found"}), 404
            
            results_json = []
            for _, row in results.iterrows():
                book_data = {
                    "Title": row.get("Title", "Unknown Title"),
                    "Author": row.get("Author", "Unknown Author"),
                    "Publisher": row.get("Publisher", "Unknown Publisher"),
                    "similarity": row["similarity"],
                    "book_id": int(row.get("book_id", 1)),
                    "Genre": row.get("Genre", "Unknown Genre")
                }
                results_json.append(book_data)

            return results_json

        except Exception as e:
            logging.error(f"Error searching books: {str(e)}")
            raise CustomException(str(e), sys)



    def Cookie_Recommend(self, book_id, top_n=5):
        try:
            self.title_vectorizer = self.get_resource('title_vectorizer','title_vectorizer.pkl')
            self.title_knn = self.get_resource('title_knn','title_knn.pkl')
            # Load MongoDB data once
            mongo_data = data_loader.load_mongo_data()
            
            # Find book by ID
            book_document = next((book for book in mongo_data if book.get("book_id") == book_id), None)
            

            if not book_document:
                return False

            book_title = book_document.get("Title", None)
            if not book_title:
                return False

            if not self.title_vectorizer or not self.title_knn:
                return False

            title_vector = self.title_vectorizer.transform([book_title])
            distances, indices = self.title_knn.kneighbors(title_vector, n_neighbors=top_n)

            dataframe = data_loader.load_dataframe()

            results = dataframe.iloc[indices.flatten()].copy()
            results['similarity'] = 1 - distances.flatten()
            # Filter out results with 0 similarity
            results = results[results['similarity'] > 0]

            # If no results found after filtering, return a message
            if results.empty:
                return False
            
            results_json = []
            for _, row in results.iterrows():
                book_data = {
                    "Title": row.get("Title", "Unknown Title"),
                    "Author": row.get("Author", "Unknown Author"),
                    "Publisher": row.get("Publisher", "Unknown Publisher"),
                    "similarity": row["similarity"],
                    "book_id": int(row.get("book_id", 1)),
                    "Genre": row.get("Genre", "Unknown Genre")
                }
                results_json.append(book_data)

            return results_json
        except Exception as e:
            logging.error(f"{str(e)}")
            return False





AccessData = Access_Data()