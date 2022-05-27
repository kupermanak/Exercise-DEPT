import os
import requests
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Books, Comments

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

#Traer info desde la API
@app.route('/booksAPI', methods=['GET'])
def get_books_from_API():
    resp = requests.get('https://openlibrary.org/search.json?author=tolkien')
    data = resp.json()
    for request_body in data["docs"]:
        item = Books(name=request_body["title"], isbn=request_body["last_modified_i"])
        db.session.add(item)
        db.session.commit()
        # print(request_body["last_modified_i"])
    # print(data["docs"][0]["isbn"][0])


    response_body = {
        "msg": "Hello, this is your GET /books response "
    }

    return jsonify(response_body), 200

#Obtener lista de libros
@app.route('/books', methods=['GET'])
def get_books():
    books = Books.query.all()
    books = list(map(lambda book : book.serialize(), books))
    return jsonify(books), 200

#Traer info por libro
@app.route("/books/<int:id>", methods=['GET'])
def get_book(id):
    books = Books.query.get(id)
    book = books.serialize()
    return jsonify(book), 200

#Guardar info de un libro
@app.route('/create/books', methods=['POST'])
def Post_book():
    body = request.get_json()
    if body is None:
        raise APIException("You need to specify the request body as a json object", status_code=400)
    if 'name' not in body:
        raise APIException('You need to specify the name', status_code=400)
    if 'isbn' not in body:
        raise APIException('You need to specify the isbn', status_code=400)

    #Insertamos al bd
    books1 = Books(name=body['name'], isbn=body['isbn'])
    db.session.add(books1)
    db.session.commit()
    return "the book has been uploaded successfully", 200

#Crear un comentario
@app.route('/create/comments', methods=['POST'])
def Post_comments():
    body = request.get_json()
    if body is None:
        raise APIException("You need to specify the request body as a json object", status_code=400)
    if 'comment' not in body:
        raise APIException('You need to write a comment', status_code=400)
    if 'book' not in body:
        raise APIException('You need to specify the book', status_code=400)
    
    is_book = Books.query.get(body["book"])
    print(is_book)
    if is_book == None:
        raise APIException("you need to specify book ID", status_code=400)

    #Insertamos al bd
    comment1 = Comments(comment=body['comment'])
    db.session.add(comment1)
    db.session.commit()
    return "the comment has been uploaded successfully", 200

#Traer comentarios
@app.route("/comments/<int:id>", methods=['GET'])
def get_comment(id):
    comments = Comments.query.get(id)
    comment = comments.serialize()
    return jsonify(comment), 200

#Actualizar un comentario
@app.route('/updateComment/<int:id>', methods=['PUT'])
def update_comment (id):
    body= request.get_json()
    if  body is None :
        raise APIException("tienes que enviar informacion para actualizar",status_code=400)   
    comment1=Comments.query.get(id)
    if comment1 is None:
        raise APIException("El comentario no existe",status_code=400)
    if 'comment' in body :
        comment1.comment=body['comment']

    db.session.commit()
    return jsonify(comment1.serialize()),200

#Borrar un comentario
@app.route("/deleteComment/<int:id>", methods=["DELETE"])
def delete_comment(id):
    del_comment = Comments.query.get(id)
    if del_comment is None:
        raise APIException('Comentario no encontrado', status_code=404)
    db.session.delete(del_comment)
    db.session.commit()
    return jsonify("Comentario eliminado"), 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
