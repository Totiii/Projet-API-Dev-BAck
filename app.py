# -*- coding: utf-8 -*-
import base64
import json
import random
import re
import uuid

import dateparser
from datetime import datetime, date

from flask import Flask, g, request, jsonify
from flask_httpauth import HTTPTokenAuth
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, exc
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc, Integer, ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'CeCiLeEnCiEu'
token_serializer = Serializer(app.config['SECRET_KEY'], expires_in=900)

auth = HTTPTokenAuth('Bearer')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.email

#Get all users
users = User.query.all()

class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    release_date = db.Column(db.String(10), nullable=True)
    type = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return '<Book %r>' % self.name


@auth.verify_token
def verify_token(token):
    g.user = None
    try:
        data = token_serializer.loads(token)
    except:
        return False
    if 'username' in data:
        g.user = data['username']
        return True
    return False


# Books

# Add book
@app.route('/book/new/', methods=['POST'])
@auth.login_required
def new_book():
    isbn = request.args.get("isbn") or None
    name = request.args.get("name") or None
    release_date = request.args.get("release_date") or None
    type = request.args.get("type") or None
    author = request.args.get("author") or None

    if isbn and name and register and type and author:
        release_date = dateparser.parse(request.args.get("release_date"))
        book = Book(isbn=isbn, author=author, name=name, release_date=release_date, type=type)
        db.session.add(book)

        try:
            db.session.commit()
            return jsonify({"status": True, 'bookID': book.id, 'bookISBN': book.isbn}), 201
        except exc.IntegrityError as e:
            return jsonify({"status": False, "error": "book_already_register", 'error_msg': "A book with the same ISBN is already register in database"}), 409
        except exc.SQLAlchemyError as e:
            print(e)
            return jsonify({"status": False})
    else:
        return jsonify({"status": False, 'error': "missing_arg"}), 410


# Delete book by isbn
@app.route('/book/delete/', methods=['DELETE'])
@auth.login_required
def del_book():
    isbn = request.args.get("isbn")
    if not (re.search('' +
                      '^(?:ISBN(?:-1[03])?:?●)?(?=[0-9X]{10}$|(?=(?:[0-9]+[-●]){3})' +
                      '[-●0-9X]{13}$|97[89][0-9]{10}$|(?=(?:[0-9]+[-●]){4})[-●0-9]{17}$)' +
                      '(?:97[89][-●]?)?[0-9]{1,5}[-●]?[0-9]+[-●]?[0-9]+[-●]?[0-9X]$', isbn)):
        return jsonify({"status": False, "error": "isbn format not good, try isbn type 10 or type 13"}), 406

    if (Book.query.filter_by(isbn=isbn).count() >= 1):
        try:
            book = Book.query.filter_by(isbn=isbn).first()
            db.session.delete(book)
            db.session.commit()
            return jsonify({"status": True}), 200
        except exc.SQLAlchemyError as e:
            print(e)
            return jsonify({"status": False})

    else:
        return jsonify({"status": False, "error": "isbn_not_found"}), 410



#Get book info by isbn
@app.route('/book/info/', methods=['GET'])
def get_book():

    isbn = request.args.get("isbn")
    if not (re.search(''+
                        '^(?:ISBN(?:-1[03])?:?●)?(?=[0-9X]{10}$|(?=(?:[0-9]+[-●]){3})'+
                        '[-●0-9X]{13}$|97[89][0-9]{10}$|(?=(?:[0-9]+[-●]){4})[-●0-9]{17}$)'+
                        '(?:97[89][-●]?)?[0-9]{1,5}[-●]?[0-9]+[-●]?[0-9]+[-●]?[0-9X]$', isbn)):
        return jsonify({"status": False, "error": "isbn format not good, try isbn type 10 or type 13"}), 406

    if (Book.query.filter_by(isbn=isbn).count() >= 1):
        try:
            book = Book.query.filter_by(isbn=isbn).first()
        except exc.SQLAlchemyError as e:
            print(e)
            return jsonify({"status": False})

        return jsonify({"status": True, "isbn": book.isbn, "name": book.name, "author": book.author,
                        "release_date": book.release_date}), 200

    else:
        return jsonify({"status": False, "error" : "isbn_not_found"}), 410

#Get all books
@app.route('/book/all/', methods=['GET'])
def get_all_books():
    books = []
    try:
        res = Book.query.all()
        for book in res:
            books.append({"isbn": book.isbn, "name": book.name, "author": book.author,
                        "release_date": book.release_date})
    except exc.SQLAlchemyError as e:
        print(e)
        return jsonify({"status": False})

    return jsonify(books), 200



#Edit book info by isbn
@app.route('/book/edit/', methods=['PATCH'])
def edit_book():

    isbn = request.args.get("isbn")
    req_name = request.args.get("name") or None
    req_release_date = request.args.get("release_date") or None
    req_type = request.args.get("type") or None
    req_author = request.args.get("author") or None

    if not (re.search(''+
                        '^(?:ISBN(?:-1[03])?:?●)?(?=[0-9X]{10}$|(?=(?:[0-9]+[-●]){3})'+
                        '[-●0-9X]{13}$|97[89][0-9]{10}$|(?=(?:[0-9]+[-●]){4})[-●0-9]{17}$)'+
                        '(?:97[89][-●]?)?[0-9]{1,5}[-●]?[0-9]+[-●]?[0-9]+[-●]?[0-9X]$', isbn)):
        return jsonify({"status": False, "error": "isbn format not good, try isbn type 10 or type 13"}), 406

    if (Book.query.filter_by(isbn=isbn).count() >= 1):
        try:
            book = Book.query.filter_by(isbn=isbn).first()
        except exc.SQLAlchemyError as e:
            print(e)
            return jsonify({"status": False})

        if req_name:
            book.name = req_name
        if req_release_date:
            book.release_date = dateparser.parse(req_release_date)
        if req_type:
            book.type = req_type
        if req_author:
            book.author = req_author

        db.session.commit()

        return jsonify({"status": True, "isbn": book.isbn, "name": book.name, "author": book.author,
                        "release_date": book.release_date})

    else:
        return jsonify({"status": False, "error" : "isbn_not_found"}), 410

# Get count all book
@app.route('/book/count/', methods=['GET'])
@auth.login_required
def get_nb_book():
    try:
        book = Book.query.count()
    except exc.SQLAlchemyError as e:
        print(e)
        return jsonify({"status": False})

    return jsonify({"result": book})

#Get count all book by category/type
@app.route('/book/count/', methods=['GET'])
def get_nb_book_by_categ():
    type = request.args.get("category")
    try:
        book = Book.query.filter_by(type=type).count()
    except exc.SQLAlchemyError as e:
        print(e)
        return jsonify({"status": False})

    return jsonify({"result": book}), 200


# Users


# Auth user
@app.route('/auth/login', methods=['POST'])
def login():
    mail = request.args.get("mail")
    password = request.args.get("password")

    if(User.query.filter_by(email=mail).count() >= 1):
        user = User.query.filter_by(email=mail).first()
        login = check_password_hash(user.password, password)
        if login == True:
            token = token_serializer.dumps({'username': user.email}).decode('utf-8')
            return jsonify({"status": True, "token": token}), 202
        else:
            return jsonify({"status": False, 'error': 'bad_password'}), 401
    else:
        return jsonify({"status": False, 'error': 'bad_login'}), 410

# Register user
@app.route('/auth/register', methods=['POST'])
def register():
    mail = request.args.get("mail")
    password = request.args.get("password")
    hashed_password = generate_password_hash(password)

    user = User(email=mail, password=hashed_password)
    db.session.add(user)

    try:
        db.session.commit()
        return jsonify({"status": True, 'userID': user.id}), 201
    except exc.SQLAlchemyError as e:
        print(e)
        if(type(e).__name__):
            return jsonify({"status": False, "error": "email_already_exists" }), 406
        else:
            return jsonify({"status": False, "error": type(e).__name__ }), 410

# Get user by id
@app.route('/user/get/', methods=['GET'])
@auth.login_required
def get_user():
    id = request.args.get("id")

    if (User.query.filter_by(id=id).count() >= 1):
        try:
            user = User.query.filter_by(id=id).first()
        except exc.SQLAlchemyError as e:
            print(e)
            return jsonify({"status": False})

        return jsonify({"status": True, "id": user.id, "email": user.email}),200
    else:
        return jsonify({"status": False, "error": "user_not_found"}), 410


if __name__ == '__main__':
    app.run()
