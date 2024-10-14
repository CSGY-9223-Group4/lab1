from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
from werkzeug.exceptions import BadRequest, UnsupportedMediaType

from .exceptions.auth_exception import AuthException
from .exceptions.user_exists_exception import UserAlreadyExistsException

from .api.note_service import NoteService, note_service
from .api.user_service import UserService, user_service
from .config import settings

INTERNAL_SERVER_ERROR = "Internal Server Error"
MAX_PAGE_SIZE = 100


def create_app(user_serv: UserService, note_serv: NoteService):
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY

    app.user_service = user_serv
    app.note_service = note_serv
    return app


app = create_app(user_service, note_service)
jwt = JWTManager(app)


@app.route("/v1/register_user", methods=["POST"])
def register_user():
    try:
        # TODO: apply realistic validation for username/password
        username = request.json.get("username", None)
        password = request.json.get("password", None)
        if not username or not password:
            raise BadRequest("Missing username or password")

        access_token = app.user_service.register_user(username, password)
        return jsonify(message="User registered", access_token=access_token), 200
    except BadRequest as e:
        return jsonify({"error": "Bad request: " + e.get_description()}), 400
    except UnsupportedMediaType as e:
        return jsonify({"error": "Unsupported media type: " + e.get_description()}), 415
    except UserAlreadyExistsException:
        return jsonify({"error": "User already exists"}), 409
    except Exception as e:
        app.log_exception(e)
        return jsonify({"error": INTERNAL_SERVER_ERROR}), 500


@app.route("/v1/login", methods=["POST"])
def login():
    try:
        username = request.json.get("username", None)
        password = request.json.get("password", None)
        if not username or not password:
            raise BadRequest("Missing username or password")

        access_token = app.user_service.login(username, password)
        return jsonify(access_token=access_token), 200
    except BadRequest as e:
        return jsonify({"error": "Bad request: " + e.get_description()}), 400
    except UnsupportedMediaType as e:
        return jsonify({"error": "Unsupported media type: " + e.get_description()}), 415
    except AuthException:
        return jsonify({"error": "Invalid username or password"}), 401
    except Exception as e:
        app.log_exception(e)
        return jsonify({"error": INTERNAL_SERVER_ERROR}), 500


@app.route("/v1/protected", methods=["GET"])
@jwt_required()
def protected():
    try:
        return jsonify(logged_in_as=get_jwt_identity()), 200
    except Exception as e:
        app.log_exception(e)
        return jsonify({"error": INTERNAL_SERVER_ERROR}), 500


@app.route("/v1/notes", methods=["GET"])
@jwt_required()
def get_notes():
    try:
        user_identity = get_jwt_identity()
        author_id = app.user_service.get_user_id_from_token(user_identity)
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 10))
        if page_size > MAX_PAGE_SIZE or page_size < 1 or page < 1:
            raise ValueError("Invalid page or page_size")

        db_notes = app.note_service.get_notes(author_id, page, page_size)
        notes_list = [note.to_dict() for note in db_notes]
        return jsonify(notes_list)
    except ValueError as e:
        return jsonify({"error": "Invalid page or page_size"}), 400
    except BadRequest as e:
        return jsonify({"error": "Bad request: " + e.get_description()}), 400
    except AuthException:
        return jsonify({"error": "Unauthorized"}), 401
    except Exception as e:
        app.log_exception(e)
        return jsonify({"error": INTERNAL_SERVER_ERROR}), 500


@app.route("/v1/notes/<int:note_id>", methods=["GET"])
@jwt_required()
def get_note(note_id: int):
    try:
        user_identity = get_jwt_identity()
        author_id = app.user_service.get_user_id_from_token(user_identity)
        if note_id < 0:
            return jsonify({"error": f"Invalid note id {note_id}"})

        db_note = app.note_service.get_note_by_id(author_id, note_id)
        if not db_note:
            return jsonify({"error": f"Note with id {note_id} does not exist"}), 404

        return jsonify(db_note.to_dict()), 200
    except BadRequest as e:
        return jsonify({"error": "Bad request: " + e.get_description()}), 400
    except AuthException:
        return jsonify({"error": "Unauthorized"}), 401
    except Exception as e:
        app.log_exception(e)
        return jsonify({"error": INTERNAL_SERVER_ERROR}), 500


@app.route("/v1/notes", methods=["POST"])
@jwt_required()
def create_note():
    try:
        user_identity = get_jwt_identity()
        author_id = app.user_service.get_user_id_from_token(user_identity)

        # TODO: apply realistic validation
        note_title = request.json.get("title", None)
        note_text = request.json.get("text", None)
        is_public = request.json.get("public", False)

        if not note_title or not note_text:
            raise BadRequest("Missing note title or text")

        db_note = app.note_service.create_note(
            note_title, note_text, author_id, is_public
        )
        return jsonify(db_note.to_dict()), 201
    except BadRequest as e:
        return jsonify({"error": "Bad request: " + e.get_description()}), 400
    except AuthException:
        return jsonify({"error": "Unauthorized"}), 401
    except UnsupportedMediaType as e:
        return jsonify({"error": "Unsupported media type: " + e.get_description()}), 415
    except Exception as e:
        app.log_exception(e)
        return jsonify({"error": INTERNAL_SERVER_ERROR}), 500


@app.route("/v1/notes/<int:note_id>", methods=["PUT"])
@jwt_required()
def update_note(note_id: int):
    try:
        user_identity = get_jwt_identity()
        author_id = app.user_service.get_user_id_from_token(user_identity)

        # TODO: apply realistic validation
        note_title = request.json.get("title", None)
        note_text = request.json.get("text", None)
        is_public = request.json.get("public", False)
        if note_id < 0:
            return jsonify({"error": f"Invalid note id {note_id}"})
        if not note_title or not note_text:
            raise BadRequest("Missing note title or text")

        db_note = app.note_service.update_note(
            note_id, note_title, note_text, author_id, is_public
        )
        if not db_note:
            return jsonify({"error": f"Note with id {note_id} does not exist"}), 404
        return jsonify(db_note.to_dict()), 200
    except BadRequest as e:
        return jsonify({"error": "Bad request: " + e.get_description()}), 400
    except AuthException:
        return jsonify({"error": "Unauthorized"}), 401
    except UnsupportedMediaType as e:
        return jsonify({"error": "Unsupported media type: " + e.get_description()}), 415
    except Exception as e:
        app.log_exception(e)
        return jsonify({"error": INTERNAL_SERVER_ERROR}), 500


@app.route("/v1/notes/<int:note_id>", methods=["DELETE"])
@jwt_required()
def delete_note(note_id: int):
    try:
        user_identity = get_jwt_identity()
        author_id = app.user_service.get_user_id_from_token(user_identity)

        if note_id < 0:
            return jsonify({"error": f"Invalid note id {note_id}"})

        db_note = app.note_service.delete_note(author_id, note_id)
        if not db_note:
            return jsonify({"error": f"Note with id {note_id} does not exist"}), 404
        return jsonify(message=f"Successfully deleted note {note_id}"), 200
    except BadRequest as e:
        return jsonify({"error": "Bad request: " + e.get_description()}), 400
    except AuthException:
        return jsonify({"error": "Unauthorized"}), 401
    except Exception as e:
        app.log_exception(e)
        return jsonify({"error": INTERNAL_SERVER_ERROR}), 500
