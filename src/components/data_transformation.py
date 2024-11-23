import sys
import pandas as pd
from src.exception import CustomException
from src.logger import logging


class DataTrans_formation:
    def CSVdataPrepare(self, file):
        try:
            logging.info(f"Starting dataset validation for {file}")
            df = pd.read_csv(file)
            
            # Checking if required columns are present
            if not all(col in df.columns for col in ['Title', 'Author', 'Genre', 'Height', 'Publisher']):
                raise CustomException("CSV does not contain required columns", sys)
            
            # Validate book_id
            if 'book_id' not in df.columns:
                df['book_id'] = range(1, len(df) + 1)  # Add book_id column starting from 1
            else:
                if not df['book_id'].apply(lambda x: isinstance(x, int)).all():
                    raise ValueError("book_id should be an integer")
            
            # Remove rows where 'Title' or 'Genre' is blank, null, or None
            df = df.dropna(subset=['Title', 'Genre'])
            df = df[df['Title'].str.strip() != '']
            df = df[df['Genre'].str.strip() != '']

            # Fill missing 'Author' and 'Publisher' with 'Unknown Author' and 'Unknown Publisher'
            df['Author'] = df['Author'].fillna('Unknown Author').replace({None: 'Unknown Author', '': 'Unknown Author'})
            df['Publisher'] = df['Publisher'].fillna('Unknown Publisher').replace({None: 'Unknown Publisher', '': 'Unknown Publisher'})

            logging.info("Dataset validation passed.")
            
            return df
        
        except Exception as e:
            logging.error(f"Error while validating CSV: {str(e)}")
            raise CustomException(str(e), sys)

        
DataTransformation = DataTrans_formation()