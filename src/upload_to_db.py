from src.logger import logging
from src.components.data_transformation import DataTransformation
from src.configuration.monodb_connection import connect_to_mongo

# import csv to db 
def UploadCSVtoDB(file):
    try:
        logging.info("Start importing CSV to MongoDB")
        
        # Validate and load CSV into DataFrame
        df = DataTransformation.CSVdataPrepare(file)
        
        # Check for required columns
        required_columns = ['Title', 'Author', 'Genre', 'Height', 'Publisher']
        optional_column = 'book_id'
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return {'success': False, 'error': f"Missing required columns: {', '.join(missing_columns)}"}

        # Add `book_id` if missing
        if optional_column not in df.columns:
            logging.info("'book_id' column is missing. Adding a manual index.")
            df[optional_column] = range(1, len(df) + 1)
        
        # Connect to MongoDB
        collection = connect_to_mongo()

        # Clear the collection
        logging.info("Clearing the collection before uploading new data...")
        collection.delete_many({})

        # Convert DataFrame to a list of dictionaries for MongoDB
        records = df.to_dict(orient='records')
        if not records:
            logging.error("CSV file contains no valid data")
            return {'success': False, 'error': 'CSV file contains no valid data'}
        
        # Insert data into MongoDB
        collection.insert_many(records)
        logging.info(f"Inserted {len(records)} records into MongoDB successfully.")
        return {'success': True}

    except Exception as e:
        logging.error(f"Unexpected error in UploadCSVtoDB: {str(e)}")
        return {'success': False, 'error': str(e)}
