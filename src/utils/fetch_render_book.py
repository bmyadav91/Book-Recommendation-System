import sys
from src.exception import CustomException
from src.logger import logging
from src.configuration.monodb_connection import connect_to_mongo
from flask import jsonify


class Fetch_book:
    def FetchForHomePage(self, Page=1, number_of_books=15):
        try:
            MongoCollection = connect_to_mongo()
            skip = (Page - 1) * number_of_books
            books = list(MongoCollection.find().skip(skip).limit(number_of_books))

            # Check if there are more books
            is_more_page = len(books) == number_of_books

            # Prepare books data with truncate_title
            for book in books:
                if 'Title' in book:
                    book['truncate_title'] = book['Title'][:45] + '...' if len(book['Title']) > 45 else book['Title']
                else:
                    book['truncate_title'] = 'No Title Available'  # Default if Title is missing
                book['_id'] = str(book['_id'])
            
            return {
                'books': books,
                'isMorePage': is_more_page
            }
        except Exception as e:
            logging.error(f"Error fetching books for homepage: {str(e)}")
            raise CustomException(str(e), sys)
        
    def FetchByBookID(self, Book_id):
        try:
            MongoCollection = connect_to_mongo()
            # Fetch the book by book_id from the collection
            book = MongoCollection.find_one({"book_id": {"$eq": Book_id}})
            
            # Check if the book is found
            if not book:
                return jsonify({"message": "Book not found"}), 404
            
            # Prepare the response with the required fields
            book_detail = {
                "Title": book.get("Title", ""),
                "Genre": book.get("Genre", None),
                "Publisher": book.get("Publisher", ""),
                "Author": book.get("Author", "")
            }

            return book_detail
        
        except Exception as e:
            logging.error(f"Error fetching books for book details page: {str(e)}")
            return {'error': 'Error fetching books for book details page'}

        

FetchBook = Fetch_book()
