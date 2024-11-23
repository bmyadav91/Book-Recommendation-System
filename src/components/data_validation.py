import os
from src.logger import logging
from werkzeug.utils import secure_filename


# form data validation 
class Validation:
    def FileValidation(self, file, file_extensions=['.csv', '.jpg']):
        try:
            logging.info(f"Validating file: {file.filename}")

            # Validate file extension
            file_extension = os.path.splitext(file.filename)[1].lower()
            if file_extension not in file_extensions:
                logging.info(f"Invalid file extension. Allowed extensions are: {', '.join(file_extensions)}")
                return {'error': f"Invalid file extension. Allowed extensions are: {', '.join(file_extensions)}", 'success': False}

            # If file name is not alphanumeric, generate a unique filename
            file.filename = secure_filename(file.filename)  # sanitize the filename

            logging.info(f"File {file.filename} validated successfully")
            return {'success': True, 'file': file}

        except Exception as Fe:
            logging.error(f"Error while validating file: {str(Fe)}")
            return {'success': False, 'file': file}

validator = Validation()