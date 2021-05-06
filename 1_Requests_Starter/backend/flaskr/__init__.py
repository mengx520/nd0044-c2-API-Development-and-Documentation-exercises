import os
from flask import Flask, request, abort, jsonify, abort
from flask_sqlalchemy import SQLAlchemy #, or_
from flask_cors import CORS
import random

from models import setup_db, Book

BOOKS_PER_SHELF = 8

def paginate_books(request, book_query):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * BOOKS_PER_SHELF
    end = start + BOOKS_PER_SHELF

    books = [book.format() for book in book_query]
    current_books = books[start:end]

    return current_books

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  # CORS Headers 
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  @app.route('/books')
  def retrive_books():
    book_query = Book.query.order_by(Book.id).all()
    current_books = paginate_books(request, book_query)
    if len(current_books) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'books': current_books,
      'total_books': len(Book.query.all())
    })

  # TEST: When completed, you will be able to click on stars to update a book's rating and it will persist after refresh
  @app.route('/books/<int:book_id>', methods=['PATCH'])
  def update_rating(book_id):
    body = request.get_json()
    try:
      book = Book.query.filter(Book.id == book_id).one_or_none()
      if book is None:
        abort(404)
      if 'rating' in body:
        book.rating = int(body.get('rating'))
      body.update()

      return jsonify({
        'success':True,
        'id': book.id
      })
    except:
      abort(400)

  # TEST: When completed, you will be able to delete a single book by clicking on the trashcan.
  @app.route('/books/<int:book_id>', methods=['DELETE'])
  def delete_book(book_id):
    try:
      book = Book.query.filter(Book.id == book_id).one_or_none()
      if book is None:
        abort(404)
        
      book.delete()

      book_query = Book.query.order_by(Book.id).all()
      current_books = paginate_books(request, book_query)

      return jsonify({
        'success': True,
        'deleted': book_id,
        'books': current_books,
        'total_books': len(Book.query.all())
      })
    except:
      abort(422)

  # TEST: When completed, you will be able to a new book using the form. Try doing so from the last page of books. 
  #       Your new book should show up immediately after you submit it at the end of the page. 
  @app.route('/books', methods=['POST'])
  def create_book():
    body = request.get_json()

    new_title = body.get('title', None)
    new_author = body.get('author', None)
    new_rating = body.get('rating', None)

    try:
      book = Book(title=new_title, author=new_author, rating=new_rating)
      book.insert()

      book_query = Book.query.order_by(Book.id).all()
      current_books = paginate_books(request, book_query)

      return jsonify({
        'success': True,
        'created': book.id,
        'books': current_books,
        'total_books': len(Book.query.all())
      })
    except:
      abort(422)

  return app

    