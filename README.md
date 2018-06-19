[![Build Status](https://travis-ci.org/Nerldy/tdd-hello-books-psql.svg?branch=master)](https://travis-ci.org/Nerldy/tdd-hello-books-psql)
[![codecov](https://codecov.io/gh/Nerldy/tdd-hello-books-psql/branch/master/graph/badge.svg)](https://codecov.io/gh/Nerldy/tdd-hello-books-psql)
# HELLO BOOKS APP
Hello-Books is a simple application that helps manage a library and its processes like stocking, tracking and renting books. With this application users are able to find and rent books. The application also has an admin section where the admin can do things like add books, delete books, increase the quantity of a book etc


## Prerequisites

- Python 3.6.4

## Install

`$ pip install -r requirements.txt `


## Usage

Make sure you're running a **virtual environment**

`$ flask run`

## Running Tests

`nostests`

## API Documentation

https://tddhellobookspsql.docs.apiary.io/#

## Features

| Endpoints                                      | Description                                      |
|------------------------------------------------|--------------------------------------------------|
| POST /api/v2/auth/register                     | Register user                                    |
| POST /api/v2/auth/login                        | Log in user                                      |
| POST /api/v2/auth/logout                       | Log out user                                     |
| POST /api/v2/auth/reset-password               | Reset password                                   |
| POST /api/v2/books                             | Create book                                      |
| GET /api/v2/books                              | Get all books                                    |
| GET /api/v2/books?limit=1&page=1               | Get books with pagination                        |
| GET /api/v2/books?limi=1&page=1&returned=false | Get books not yet returned                       |
| PUT /api/v2/books/{book_id}                    | Update book with id. Id must be integer          |
| GET /api/v2/users/books                        | Get history of books borrowed                    |
| GET /api/v2/books/{book_id}                    | Get a single book with id. Id must be integer    |
| DELETE /api/v2/books/{book_id}                 | Delete a single book with id. Id must be integer |
| POST /api/v2/users/books/{book_id}             | User borrow book with id. Id must be integer     |
| PUT /api/v2/users/books/{book_id}              | User return book with id. Id must be integer     |