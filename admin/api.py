from enum import unique
from flask import Flask, json
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, abort, Api, reqparse, fields, marshal_with


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///library.db"
    db.init_app(app)

    return app

app = create_app()
api = Api(app)

userFields = {
    "id": fields.Integer,
    "first_name": fields.String,
    "last_name": fields.String,
    "email": fields.String,
    "book_borrowed": fields.String,
    "days_to_use": fields.Integer,
    "user_type": fields.Integer,
}

class UserModel(db.Model):
    __tablename__ = 'users'

    id  = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    book_borrowed = db.Column(db.String(100), nullable=True)
    days_to_use = db.Column(db.Integer)
    user_type = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f"User(first_name = {self.first_name}, last_name = {self.last_name}, email = {self.email}, book_borrowed = {self.book_borrowed}, days_to_use = {self.days_to_use}, user_type = {self.user_type}"

class Users(Resource):
    @marshal_with(userFields)
    def get(self):
        users = UserModel.query.all()
        return users

class User(Resource):
    @marshal_with(userFields)
    def get(self, id):
        user = UserModel.query.get_or_404(id)
        return user

class UsersAndBooksBorrowed(Resource):
    def get(self):
        users = UserModel.query.all()
        user_books = []
        for user in users:
            borrowed_books = BookModel.query.filter_by(borrowed_by=user.id).all()

            books_info = [{
                "name": book.name,
                "isbn": book.isbn,
                "borrowed_date": book.borrowed_date
            } for book in borrowed_books]

            user_books.append({
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "borrowed_books": books_info 
            })

        return user_books, 200


api.add_resource(Users, "/api/users/")
api.add_resource(User, "/api/user/<int:id>")
api.add_resource(UsersAndBooksBorrowed, "/api/users/books/")

user_args = reqparse.RequestParser()
user_args.add_argument("first_name", type=str, required=True, help="Firstname cannot be blank")
user_args.add_argument("last_name", type=str, required=True, help="Lastname cannot be blank")
user_args.add_argument("email", type=str, required=True, help="Email cannot be blank")


class BookModel(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    isbn = db.Column(db.Integer, nullable=False, unique=True)
    publisher = db.Column(db.String(30), nullable=False)
    category = db.Column(db.String(30))
    borrowed = db.Column(db.Boolean, default=False)
    borrowed_date = db.Column(db.DateTime, nullable=True)
    available_by = db.Column(db.DateTime, nullable=True)
    borrowed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) 
    borrower = db.relationship('UserModel', backref='borrowed_books')

    def __repr__(self) -> str:
        return f"Book(name = {self.name}, isbn = {self.isbn}, publisher = {self.publisher}, category = {self.category}, borrowed = {self.borrowed}, borrowed_date = {self.borrowed_date}), borrowed_by = {self.borrowed_by}, available_by = {self.available_by}"

bookFields = {
    "id": fields.Integer,
    "name": fields.String,
    "author": fields.String,
    "isbn": fields.Integer,
    "publisher": fields.String,
    "category": fields.String,
    "borrowed": fields.Boolean,
    "borrowed_date": fields.String,
    "borrowed_by": fields.Integer,
    "available_by": fields.String
}

class Books(Resource):
    @marshal_with(bookFields)
    def get(self):
        books = BookModel.query.all()
        return books
    
    @marshal_with(bookFields)
    def post(self):
        args = library_args.parse_args()
        book = BookModel(name=args["name"], isbn=args["isbn"], publisher=args["publisher"], category=args["category"], borrowed=args["borrowed"], borrowed_date=args["borrowed_date"], borrowed_by=args["borrowed_by"], author=args["author"], available_by=args["available_by"])
        db.session.add(book)
        db.session.commit()
        books = BookModel.query.all()
        return books, 201

def get_book_by_id(id):
    book = BookModel.query.filter_by(id=id).first()
    return book

class Book(Resource):
    @marshal_with(bookFields)
    def get(self, id):
        book = get_book_by_id(id)
        if not book:
            abort(404, message="Book not found")
        return book
        
    
    def put(self, id):
        args = library_args.parse_args()
        book = BookModel.query.get_or_404(id)

        if args["name"]:
            book.name = args["name"]

        if args["isbn"]:
            book.isbn = args["isbn"]

        if args["publisher"]:
            book.publisher = args["publisher"]

        if args["category"]:
            book.category = args["category"]

        if args["borrowed"] is not None: 
            book.borrowed = args["borrowed"]

        if args["borrowed_date"]:
            book.borrowed_date = args["borrowed_date"]

        if args["borrowed_by"]:
            book.borrowed_by = args["borrowed_by"]

        db.session.commit()
        return book, 201
    
    def delete(self, id):
        book = BookModel.query.get_or_404(id)
        db.session.delete(book)
        db.session.commit()

        msg = json.dumps({"message": "Book deleted successfully"})
        return msg, 204


class BorrowedBooks(Resource):
    def get(self):
        borrowed_books = BookModel.query.filter_by(borrowed=True).all()
        return borrowed_books

class AvailableBooks(Resource):
    @marshal_with(bookFields)
    def get(self):
        available_books = BookModel.query.filter_by(borrowed=False).all()
        return available_books

api.add_resource(Books, "/api/books/")
api.add_resource(Book, "/api/books/<int:id>")
api.add_resource(BorrowedBooks, "/api/borrowed/")

library_args = reqparse.RequestParser()
library_args.add_argument("name", type=str, required=True, help="Book name shouldnt be empty")
library_args.add_argument("author", type=str, required=True, help="Author cant be empty")
library_args.add_argument("isbn", type=int, required=True, help="ISBN can't be empty")
library_args.add_argument("publisher", type=str, required=True, help="Publisher name can't be empty")
library_args.add_argument("category", type=str, required=False, help="Only string is allowed")
library_args.add_argument("borrowed", type=bool, required=False, help="Expects a boolean")
library_args.add_argument("borrowed_date", type=str)
library_args.add_argument("borrowed_by", type=int)
library_args.add_argument("available_by", type=str)


if __name__ == "__main__":
    app.run(debug=True, port=2324)
