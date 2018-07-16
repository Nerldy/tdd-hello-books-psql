from flask import abort, jsonify, make_response



def check_admin(user):
	"""
	Prevent non-admins from accessing the page
	:return: 403
	:param user: user
	"""
	if not user.is_admin:
		abort(403)


def response_for_book(book):
	"""returns a single books when requested"""
	return make_response(
		jsonify(
			{
				'status': 'success',
				'books': book
			}
		)
	)


def response_for_created_book(book, status_code):
	"""
	returns a response when a books has been created
	:param book:
	:param status_code:
	:return: http response
	"""
	return make_response(jsonify(
		{
			'status': 'success',
			'id': book.id,
			'title': book.title,
			'isbn': book.isbn,
			'date_created': book.date_created,
			'date_modified': book.date_modified
		}
	)), status_code


def response(status, message, code):
	"""
	method returns a http response
	:param status:
	:param message:
	:param code:
	:return: http response
	"""

	return make_response(
		jsonify(
			{
				'status': status,
				'message': message
			}
		)
	), code


def get_user_book_list(books_list):
	"""
	make json objects of the books
	:param books_list:
	:return:
	"""

	books = []
	for book in books_list:
		books.append(book.serialize())
	return books


def get_paginated_list(books, url, start, limit):
	"""
	returns a paginated list of books
	:param books:
	:param url:
	:param start:
	:param limit:
	:return:
	"""
	results = books
	count = len(results)
	if count < start:
		abort(404)

	# make response
	obj = {
		'start': start,
		'limit': limit,
		'count': count
	}

	# make URLs

	# make previous url
	if start == 1:
		obj['previous'] = ''

	else:
		start_copy = max(1, start - limit)
		limit_copy = start - 1
		obj['previous'] = url + f'?page={start_copy}&limit={limit_copy}'

	# make next url
	if start + limit > count:
		obj['next'] = ''
	else:
		start_copy = start + limit
		obj['next'] = url + f'?page={start_copy}&limit={limit}'

	# finally extract result according to bounds
	obj['books'] = results[(start - 1):(start - 1 + limit)]
	return obj


def response_with_pagination(books, previous_page, next_page, count):
	"""
	make http response for books with pagination
	:param books:
	:param previous_page:
	:param next_page:
	:param count:
	:return: http json response
	"""

	return make_response(jsonify(
		{
			'status': 'success',
			'previous': previous_page,
			'next': next_page,
			'count': count,
			"books": books
		}
	)), 200
