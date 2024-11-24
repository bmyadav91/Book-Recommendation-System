from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from src.logger import logging
from src.utils.s3_uploader import StreamFile
from src.configuration.monodb_connection import connect_to_mongo
import pandas as pd

def train_model(books):
    try:
        if 'Title' not in books.columns or 'Genre' not in books.columns:
            return {'error': 'Missing required columns in the DataFrame'}

        # Training for Title
        logging.info("Training model for book titles...")
        title_vectorizer = TfidfVectorizer(stop_words='english')
        title_matrix = title_vectorizer.fit_transform(books['Title'])
        title_knn = NearestNeighbors(metric='cosine', algorithm='brute')
        title_knn.fit(title_matrix)

        # Upload Title model and vectorizer to S3
        StreamFile.pickle_file_stream(title_vectorizer, 'title_vectorizer.pkl')
        StreamFile.pickle_file_stream(title_knn, 'title_knn.pkl')

        # Training for Genre
        logging.info("Training model for book genres...")
        genre_vectorizer = TfidfVectorizer(stop_words='english')
        genre_matrix = genre_vectorizer.fit_transform(books['Genre'])
        genre_knn = NearestNeighbors(metric='cosine', algorithm='brute')
        genre_knn.fit(genre_matrix)

        # Upload Genre model and vectorizer to S3
        StreamFile.pickle_file_stream(genre_vectorizer, 'genre_vectorizer.pkl')
        StreamFile.pickle_file_stream(genre_knn, 'genre_knn.pkl')
        logging.info("Model training complete.")
        return {'success': True}
    except Exception as e:
        logging.error(f"Error during training: {str(e)}")
        return {'error': str(e)}


def run_train_model():
    try:
        collection = connect_to_mongo()
        # Fetch data from the collection
        data = list(collection.find())
        
        # Check if data is empty
        if not data:
            return {'error': 'No data found in the MongoDB collection.'}
        
        # Convert data to DataFrame
        df = pd.DataFrame(data)
        
        # Train the model
        return train_model(df)
    except Exception as e:
        logging.error(str(e))
        return {'error': str(e)}
