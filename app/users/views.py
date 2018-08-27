from flask import Blueprint, request, abort, make_response, jsonify
from app.books.helper_funcs import check_admin
from app.auth.helper_funcs import token_required
from app.models import Book, User, BorrowedBook
from app.books.helper_funcs import check_admin, response, response_for_book, response_for_created_book, response_with_pagination, get_user_book_list
from cerberus import Validator
from app import db

users = Blueprint('users', __name__)

pagination_schema = {
	'limit': {
		'type': 'string',
		'required': True
	},
	'page': {
		'type': 'string',
		'required': True
	},
	'returned': {
		'type': 'string',
		'required': True
	},
	'user_id': {
		'type': 'string',
		'required': False,
		'empty': False
	}
}

validate_pagination_schema = Validator(pagination_schema)


@users.route('')
@token_required
def api_books_not_returned_or_history(current_user):
	"""
	handles books not returned by user or books borrowed history
	:param current_user:
	:return:
	"""

	req_args = request.args

	# check if args exists. This will deal with books not returned
	if req_args:
		if validate_pagination_schema.validate(req_args) and req_args.get('returned') == 'false':
			try:
				borrowed_books = None
				page_limit = req_args.get('limit', None, int)
				page_number = req_args.get('page', None, int)

				# if username in args check if it's admin
				if 'user_id' in req_args:
					check_admin(current_user)

					user_id = int(req_args.get('user_id'))

					borrowed_books = BorrowedBook.query.filter(
						db.and_(
							BorrowedBook.return_date == None,
							BorrowedBook.user_id == user_id
						)
					).all()

				else:
					# find the book in the borrowed book table
					borrowed_books = BorrowedBook.query.filter(
						db.and_(
							BorrowedBook.return_date == None,
							BorrowedBook.user_id == current_user.id
						)
					).paginate(per_page=page_limit, page=page_number)

				books_list = []

				# match all the books borrowed ID's to the books table
				for single_book in borrowed_books.items:
					match_book = Book.query.filter_by(id=single_book.book_id).first()
					books_list.append(match_book)

				# check if book_results is empty return 204
				if len(books_list) < 1:
					return make_response(jsonify({'': ''})), 204

				return make_response(
					jsonify({
						"books": [book.serialize() for book in books_list],
						"has_next": borrowed_books.has_next,
						"has_prev": borrowed_books.has_prev,
						"next_page_num": borrowed_books.next_num,
						"prev_page_num": borrowed_books.prev_num,
						"total_pages": borrowed_books.pages,
						"current_page": borrowed_books.page
					})
				)
			except Exception as e:
				return make_response(
					jsonify(
						{
							# 'error': str(e)
							'error': "something went wrong"
						}
					)
				), 400

		return make_response(jsonify({'error': validate_pagination_schema.errors})), 400

	else:  # find user's book borrowing history
		try:
			# query for all borrowed books history
			borrowed_books = BorrowedBook.query.filter(
				db.and_(
					BorrowedBook.return_date != None,
					BorrowedBook.user_id == current_user.id
				)
			).all()

			books_list = []

			for single_book in borrowed_books:
				match_book = Book.query.filter_by(id=single_book.book_id).first()
				book_data = None
				if match_book:
					book_data = {
						'id': match_book.id,
						'title': match_book.title,
						'isbn': match_book.isbn,
						'borrow_date': single_book.borrow_date,
						'return_date': single_book.return_date
					}
					books_list.append(book_data)

			# check if book_results is empty return 204
			if len(books_list) < 1:
				return make_response(jsonify({'': ''})), 204

			return make_response(
				jsonify({
					"books": books_list
				})
			)
		except Exception as e:
			return make_response(
				jsonify(
					{
						'error': str(e)
					}
				)
			), 400


@users.route('/<book_id>', methods=['POST'])
@token_required
def api_borrow_book(current_user, book_id):
	"""
	handler for borrowing a book
	:param current_user:
	:param book_id:
	:return:
	"""

	try:  # check if book id is integer
		int(book_id)
	except ValueError:  # if it's not integer raise an error
		return response('error', 'please provide a book id. ID must be integer', 400)
	else:
		book_instance = Book.query.filter_by(id=book_id).first()  # find book in the database

		# if book doesn't exists return 404
		if not book_instance:
			return response('error', f"book with ID {book_id} not found", 404)

		# check if book is borrowed
		if book_instance.is_borrowed:
			return response('message', f'book with ID no.{book_id} is currently unavailable', 400)

		# if book exists user can borrow it
		borrow_book = BorrowedBook()
		borrow_book.user_id = current_user.id
		borrow_book.book_id = book_instance.id
		book_instance.is_borrowed = True

		# add borrowed book to the borrow database
		db.session.add(borrow_book)
		db.session.commit()

		return response('success', f'book with ID no.{book_id} has been borrowed', 200)


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
