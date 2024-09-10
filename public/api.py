from datetime import datetime, timedelta
from admin.api import db, userFields, UserModel, BookModel, user_args, create_app, AvailableBooks, get_book_by_id, bookFields
from flask_restful import Api, Resource, marshal_with, abort, reqparse

app = create_app()
api = Api(app)

class User(Resource):
    @marshal_with(userFields)
    def post(self):
        args = user_args.parse_args()
        user = UserModel(first_name=args["first_name"], last_name=args["last_name"], email=args["email"])
        db.session.add(user)
        db.session.commit()
        return user, 201

class Book(Resource):
    @marshal_with(bookFields)
    def get(self, id):
        book = get_book_by_id(id)
        if not book:
            abort(404, message="Book not found")
        return book

filter_parser = reqparse.RequestParser()
filter_parser.add_argument("publisher", type=str, help="Filter by publisher")
filter_parser.add_argument("category", type=str, help="Filter by category")

class FilterBooks(Resource):
    def get(self):
        args = filter_parser.parse_args()
        query = BookModel.query
        
        if args['publisher']:
            query = query.filter_by(publisher=args['publisher'])
        
        if args['category']:
            query = query.filter_by(category=args['category'])
        
        books = query.all()
        
        books_list = [{
            "id": book.id,
            "name": book.name,
            "isbn": book.isbn,
            "publisher": book.publisher,
            "category": book.category,
            "borrowed": book.borrowed,
            "borrowed_date": book.borrowed_date
        } for book in books]

        return {"books": books_list}, 200

borrow_args = reqparse.RequestParser()
borrow_args.add_argument("book_id", type=int, help="ID of the book to borrow", required=True)
borrow_args.add_argument("email", type=str, help="email of the user borrowing the book", required=True)
borrow_args.add_argument("no_of_days", type=int, help="Number of days to borrow the book", required=True)

class BorrowBook(Resource):
    @marshal_with(bookFields)
    def put(self):
        args = borrow_args.parse_args()
        book = BookModel.query.get(args["book_id"])
        if not book:
            abort(404, message="Book not found")
        
        if book.borrowed:
            abort(400, message="This book is already borrowed")
        
        user = UserModel.query.filter_by(email=args["email"]).first()
        if not user:
            abort(404, message="User not found")
        
        available_by_date = datetime.now() + timedelta(days=args["no_of_days"])
        
        book.borrowed = True
        book.borrowed_by = user.id
        book.borrowed_date = datetime.now()
        book.available_by = available_by_date
        
        user.book_borrowed = book.name
        user.days_to_use = args["no_of_days"]
        
        db.session.commit()
    
        return book, 200

api.add_resource(User, "/api/public/user/")
api.add_resource(AvailableBooks, "/api/public/books/")
api.add_resource(Book, "/api/public/books/<int:id>")
api.add_resource(FilterBooks, "/api/public/filter/")
api.add_resource(BorrowBook, "/api/public/borrow/")

if __name__ == "__main__":
    app.run(debug=True, port=2323)

