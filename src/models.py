from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class Books(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    isbn = db.Column(db.Integer, nullable=False)
    comments = db.relationship("Comments", back_populates="books")

    def __repr__(self):
        return '<Books %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "isbn": self.isbn,
            "comments": list(map(lambda x: x.serialize(), self.comments))
        }

class Comments(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(400))
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"))
    books = relationship("Books", primaryjoin=book_id == Books.id)

    def __repr__(self):
        return '<Comments %r>' % self.comment

    def serialize(self):
        return {
            "id": self.id,
            "comment": self.comment,
        }