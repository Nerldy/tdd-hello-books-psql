from flask import Blueprint, request, abort, make_response, jsonify
from app.books.helper_funcs import check_admin
from app.auth.helper_funcs import token_required
from app.models import Book, User, BorrowedBook
from app.books.helper_funcs import check_admin, response, response_for_book, response_for_created_book, response_with_pagination, get_user_book_list
from cerberus import Validator
from app import db

users = Blueprint('users', __name__)


@users.route('/<book_id>', methods=['POST'])
@token_required
def api_borrow_book(current_user, book_id):
	"""
	handler for borrowing a book
	:param current_user:
	:param book_id:
	:return:
	"""
	print(book_id)
	try:  # check if book id is integer
		int(book_id)
	except ValueError:  # if it's not integer raise an error
		return response('error', 'please provide a book id. ID must be integer', 400)
	else:
		book_instance = Book.query.filter_by(id=book_id).first()  # find book in the database

		# if book doesn't exists return 404
		if not book_instance:
			return response('error', "book not found", 404)

		# check if book is borrowed
		if book_instance.is_borrowed:
			return response('message', f'book with id {book_id} is currently unavailable', 204)

		# if book exists user can borrow it
		borrow_book = BorrowedBook()
		borrow_book.user_id = current_user.id
		borrow_book.book_id = book_instance.id
		book_instance.is_borrowed = True

		# add borrowed book to the borrow database
		db.session.add(borrow_book)
		db.session.commit()

		return response('success', 'book has been borrowed', 200)


@users.route('/<book_id>', methods=['PUT'])
@token_required
def api_return_book(current_user, book_id):
	"""
	handler for returning a book
	:param current_user:
	:param book_id:
	:return:
	"""
	try:  # check if book id is integer
		int(book_id)
	except ValueError:  # if it's not integer raise an error
		return response('error', 'please provide a book id. ID must be integer', 400)
	else:
		book_borrowed = Book.query.filter_by(id=book_id).first()  # find book in the database
		book_return = BorrowedBook.query.filter(db.and_(
			BorrowedBook.book_id == book_id,
			BorrowedBook.user_id == current_user.id,
			BorrowedBook.return_date == None
		)).first()

		# if book doesn't exists return 404
		if not book_borrowed:
			return response('error', "book not found", 404)

		# check if book is borrowed
		if book_borrowed.is_borrowed:
			book_borrowed.is_borrowed = False
			book_return.return_date = db.func.current_timestamp()
			db.session.commit()
			return response('success', f'book with id {book_id} has been returned', 200)

		return response('message', f'you did not borrow book with id {book_id}', 403)
