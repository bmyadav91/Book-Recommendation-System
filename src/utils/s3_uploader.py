import pickle
import io
import os, sys
from src.logger import logging
from src.exception import CustomException
from src.configuration.s3_config import s3_bucket_connection
from settings import folder_name



# if working on single s3 bucket 
bucket_name = os.getenv("AWS_BUCKET")

def upload_file_to_s3(file_path, object_name=None):
    try:
        s3_client = s3_bucket_connection()
        if object_name is None:
            object_name = os.path.basename(file_path)
        object_name = f"{folder_name}/{object_name}"
        s3_client.upload_file(file_path, bucket_name, object_name)

        logging.info(f"File '{file_path}' successfully uploaded to '{bucket_name}/{object_name}'.")
        return True
    except Exception as e:
        logging.error(f"Failed to upload file: {str(e)}")
        raise CustomException(f"Error while uploading {str(e)}", sys)



# stream file then upload 
class StreamFiles:

    def pickle_file_stream(self, model, file_name):
        try:
            s3_client = s3_bucket_connection()
            file_stream = io.BytesIO()
            pickle.dump(model, file_stream)
            file_stream.seek(0)

            # Append folder name to the file path
            object_name = f"{folder_name}/{file_name}"

            # Upload to S3 with folder
            s3_client.upload_fileobj(file_stream, bucket_name, object_name)

            logging.info(f"Model '{file_name}' uploaded to '{bucket_name}/{object_name}'")
        except Exception as e:
            logging.error(f"Error uploading to S3: {e}")
            raise CustomException(f"Error uploading {file_name} to S3: {str(e)}", sys)



StreamFile = StreamFiles()