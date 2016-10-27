"""Models and database functions for Goodreads reviews project."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

app = Flask(__name__)
db = SQLAlchemy()

db = SQLAlchemy()


##############################################################################
# Model definitions

class Group(db.Model):
    """track groups so we can skip those already processed"""

    __tablename__ = "groups"

    # goodreads group id
    group_id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(256))
    process_success = db.Column(db.Boolean)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Group group_id=%s success=%s>" % (self.user_id, self.process_success)


class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    # this is the goodreads user id
    user_id = db.Column(db.Integer, primary_key=True)
    private = db.Column(db.Boolean)
    process_success = db.Column(db.Boolean)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s success=%s>" % (self.user_id, self.process_success)


class Book(db.Model):
    """Books on ratings website."""

    __tablename__ = "books"

    # book_id is the isbn
    book_id = db.Column(db.String(32), primary_key=True)
    title = db.Column(db.String(256))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Book book_id=%s title=%s>" % (self.book_id, self.title)


class Rating(db.Model):
    """Rating of a book by a user."""

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    book_id = db.Column(db.String, db.ForeignKey('books.book_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    score = db.Column(db.Integer)

    # Define relationship to user
    user = db.relationship("User",
                           backref=db.backref("ratings", order_by=rating_id))

    # Define relationship to movie
    book = db.relationship("Book",
                            backref=db.backref("ratings", order_by=rating_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Rating rating_id=%s book_id=%s user_id=%s score=%s>" % (
            self.rating_id, self.book_id, self.user_id, self.score)


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///goodreads'
#    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    connect_to_db(app)
    db.create_all()

    print "Connected to DB."
