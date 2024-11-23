import sys, os
from flask import Flask, request, jsonify, render_template, make_response
from src.exception import CustomException
from src.logger import logging
from src.configuration.monodb_connection import connect_to_mongo
from src.upload_to_db import UploadCSVtoDB
from src.components.data_validation import validator
from src.components.model_trainer import run_train_model
from src.data_access.access_script import AccessData
from src.utils.fetch_render_book import FetchBook
from src.utils.description_generator import GenerateDescription
from settings import folder_name

app = Flask(__name__)

# home page 
@app.route('/', methods=['GET'])
def home_page():
    try:
        result = FetchBook.FetchForHomePage(Page=1)
        books = result['books']
        is_more_page = result['isMorePage']

        # check if customer visit any page and that stored in cookie
        last_visit_id = request.cookies.get('last_visit', None)
        inspired_books_for_you = False
        if last_visit_id:
            inspired_books_for_you = AccessData.Cookie_Recommend(int(last_visit_id))

        
        return render_template('index.html', BooksForHome=books, is_more_page=is_more_page, inspired_books_for_you=inspired_books_for_you)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# pagination api
@app.route('/home', methods=['post'])
def PaginationOnHomePage():
    try:
        data = request.get_json()
        current_page = data.get('currentPage')
        result = FetchBook.FetchForHomePage(current_page)
        books = result['books']
        is_more_page = result['isMorePage']
        return jsonify({'books': books, 'is_more_page': is_more_page})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# search page 
@app.route('/search', methods=['GET'])
def search():
    try:
        query = request.args.get('s', '')
        if query:
            search_result = AccessData.search_book(query)
            # return search_result
            return render_template('search.html', books=search_result, query=query)
        return jsonify({"message": "No query provided"}), 400
    except Exception as e:
        return jsonify({'error': str(e)})
    

# book details page 
@app.route('/book_detail/<book_id>', methods=['GET'])
def book_detail(book_id):
    try:
        book_id = int(book_id)
        # Fetch book details and similar books
        BookResult = FetchBook.FetchByBookID(book_id)
        Similar_books = AccessData.find_similar_genre(BookResult['Genre'], book_id)

        # Create a response object
        response = make_response(render_template('book_detail.html', book=BookResult, similar_books=Similar_books))
        
        # Set a cookie to store the last visited book ID
        response.set_cookie('last_visit', str(book_id), max_age=864000)

        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# generate description 
@app.route('/generate_description', methods=['POST'])
def Genrate_Book_Description():
    try:
        data = request.get_json()
        prompt = data.get('generate_for', None)
        if prompt:
            Description = GenerateDescription(prompt)
            return jsonify({'description': Description})
        
        return jsonify({'error': 'Unable to generate'})
    
    except Exception as _:
        return jsonify({'error': str(_)})

# upload  
@app.route('/upload', methods=['GET', 'POST'])
def UploadCSV():
    try:
        if request.method == 'POST':
            if 'file' not in request.files:
                return jsonify({'error': 'No file was provided'}), 400
            
            file = request.files['file']

            # Validate the file using the Validation class
            file_validate = validator.FileValidation(file)
            if not file_validate.get('success', False):
                return jsonify(file_validate), 400

            # Upload the CSV to DB
            Uploading = UploadCSVtoDB(file)
            if not Uploading.get('success', False):
                return jsonify(Uploading), 500
            
            # Automatically train the model after a successful upload
            train_model_result = run_train_model()
            if not train_model_result.get('success', False):
                return jsonify({'message': 'File uploaded but training failed', 'train_error': train_model_result}), 500
            
            return jsonify({'message': 'File uploaded and model trained successfully'}), 200

        return render_template('upload_csv.html')

    except Exception as e:
        logging.error(f"Unexpected error in UploadCSV: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/train', methods=['POST'])
def TrainModel():
    try:
        logging.info("Starting to train model")
        train_model_result = run_train_model()
        
        if not train_model_result.get('success', False):
            return jsonify(train_model_result), 400
        
        logging.info("Model trained and PKL files created and saved to S3 bucket")
        return jsonify({'success': True, 'message': 'Model trained and PKL files saved to S3 bucket'})
    
    except Exception as e:
        logging.error(f"Error while training the model: {str(e)}")
        return jsonify({'success': False, 'error': f'Error while model training {str(e)}'}), 500

    



# dynamic serve static file from s3 - setup
bucket_name = os.getenv("AWS_BUCKET")
app.config['STATIC_URL'] = f'https://{bucket_name}.s3.amazonaws.com/{folder_name}/'

@app.context_processor
def inject_s3_url():
    return {'static_url': app.config['STATIC_URL']}



# run app 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
