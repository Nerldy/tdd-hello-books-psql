from flask import Blueprint, request, abort, make_response, jsonify
from app.books.helper_funcs import check_admin
from app.auth.helper_funcs import token_required, format_inputs
from app.models import Book, User
from app.books.helper_funcs import check_admin, response, response_for_book, response_for_created_book, response_with_pagination, get_user_book_list
from cerberus import Validator

# schemas
book_schema = {
	'title': {
		'type': 'string',
		'required': True,
		'empty': False
	},
	'isbn': {
		'type': "string",
		'required': True
	}
}

update_book_schema = {
	'title': {
		'type': 'string',
		'required': True,
		'empty': False
	}
}

pagination_schema = {
	'limit': {
		'type': 'string',
		'required': True
	},
	'page': {
		'type': 'string',
		'required': True
	}
}

# schema validations
validate_book_schema = Validator(book_schema)
validate_update_book_schema = Validator(update_book_schema)
validate_pagination_schema = Validator(pagination_schema)

# intialize blueprint
books = Blueprint('books', __name__)


@books.route('')
@token_required
def api_get_all_books(current_user):
	"""
	retrieve all books in the database
	:return:
	"""

	all_books = Book.get_all()
	books_result = []
	req_args = request.args

	# check if pagination args are provided
	if req_args:
		if validate_pagination_schema.validate(req_args):
			try:
				page_limit = int(request.args.get('limit'))
				page_number = int(request.args.get('page'))

				book_pagination = Book.query.paginate(
					per_page=page_limit,
					page=page_number,
					error_out=True
				)

				books_result = get_user_book_list(book_pagination.items)

				return make_response(
					jsonify({
						'current_page': book_pagination.page,
						'pages': book_pagination.pages,
						"books": books_result
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

		return make_response(jsonify({'error': validate_pagination_schema.errors})), 400

	for single_book in all_books:
		book_obj = single_book.serialize()
		books_result.append(book_obj)

	return make_response(
		jsonify(
			{
				'books': books_result
			}
		)
	)


@books.route('', methods=['POST'])
@token_required
def api_create_book(current_user):
	"""
	create a book from json data
	:param current_user:
	:return:
	"""

	check_admin(current_user)
	req_data = request.get_json()

	if request.content_type == 'application/json':
		if validate_book_schema.validate(req_data):
			try:
				title = format_inputs(req_data.get('title'))
				isbn = format_inputs(req_data.get('isbn'))

				if len(isbn) != 10:
					return jsonify({'error': "isbn length must be 10"}), 400

				if isbn.isnumeric():
					new_book = Book(title=title, isbn=isbn)
					new_book.save()

					return response('success', {'book created': new_book.serialize()}, 201)

				return response('error', 'isbn must only include numbers', 400)

			except Exception as e:
				return response('error', str(e), 400)

		return response('error', validate_book_schema.errors, 400)

	return response('error', 'Content-type must be json', 202)


@books.route('/<book_id>')
@token_required
def api_get_book_with_id(current_user, book_id):
	"""
	retrieves a book with id
	:param current_user:
	:param book_id:
	:return:
	"""

	try:
		int(book_id)
	except ValueError:
		return response('error', 'please provide a book id. ID must be integer', 400)
	else:
		single_book = Book.query.filter(Book.id == book_id).first()

		if single_book:
			return response_for_book(single_book.serialize())
		return response('error', 'book not found', 404)


@books.route('/<book_id>', methods=['PUT'])
@token_required
def api_update_book(current_user, book_id):
	"""
	update a book via it's id. Updates title only
	:param current_user:
	:param book_id:
	:return:
	"""

	check_admin(current_user)
	req_data = request.get_json()

	if request.content_type == 'application/json':
		if validate_update_book_schema.validate(req_data):
			try:
				int(book_id)
			except ValueError:
				return response('error', 'please provide a book id. ID must be integer', 400)

			book_update = Book.query.filter(Book.id == book_id).first()
			title = format_inputs(req_data.get('title'))

			if book_update:
				book_update.title = title
				book_update.save()
				return response_for_created_book(book_update, 201)
			return response('error', f"book with id {book_id} does not exist", 404)

		return response('error', f"Nothing was changed: {validate_update_book_schema.errors}", 400)
	return response('error', 'Content-type must be json', 202)


@books.route('/<book_id>', methods=['DELETE'])
@token_required
def api_delete_book(current_user, book_id):
	"""
	delete a book
	:param current_user:
	:param book_id:
	:return:
	"""
	check_admin(current_user)
	try:
		int(book_id)
	except ValueError:
		return response('error', 'please provide a book id. ID must be integer', 400)
	del_book = Book.query.filter(Book.id == book_id).first()

	if not del_book:
		abort(404)
	del_book.delete()
	return response('success', f'book with id {book_id} has been deleted', 200)
