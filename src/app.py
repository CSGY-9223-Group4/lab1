from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
from werkzeug.exceptions import UnsupportedMediaType
import os

from .exceptions.auth_exception import AuthException
from .exceptions.user_exists_exception import UserAlreadyExistsException

from .api import note_service, user_service
from .config import settings


app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY
jwt = JWTManager(app)

INTERNAL_SERVER_ERROR = "Internal Server Error"


@app.route("/v1/register_user", methods=["POST"])
def register_user():
    try:
        # TODO: apply realistic validation for username/password
        username = request.json.get("username", None)
        password = request.json.get("password", None)
        if not username or not password:
            return jsonify({"error": "Missing username or password"}), 400

        access_token = user_service.register_user(username, password)
        return jsonify(message="User registered", access_token=access_token), 200
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
            return jsonify({"error": "Missing username or password"}), 400

        access_token = user_service.login(username, password)
        return jsonify(access_token=access_token), 200
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
        # TODO: add user_id to JWT and use it there
        author_id = request.args.get("author_id", None)
        if not author_id:
            return jsonify({"error": "Missing author id"}), 400

        db_notes = note_service.get_notes(author_id)
        notes_list = [note.to_dict() for note in db_notes]
        return jsonify(notes_list)
    except Exception as e:
        app.log_exception(e)
        return jsonify({"error": INTERNAL_SERVER_ERROR}), 500


@app.route("/v1/notes", methods=["POST"])
@jwt_required()
def post_note():
    try:
        # TODO: apply realistic validation
        note_title = request.json.get("title", None)
        note_text = request.json.get("text", None)
        is_public = request.json.get("public", False)
        # TODO: add user_id to JWT and use it there
        author_id = request.json.get("author_id", None)
        if not note_title or not note_text or not author_id:
            return jsonify({"error": "Missing note title or text or author id"}), 400

        db_note = note_service.post_note(note_title, note_text, author_id, is_public)
        return jsonify(db_note.to_dict()), 200
    except UnsupportedMediaType as e:
        return jsonify({"error": "Unsupported media type: " + e.get_description()}), 415
    except Exception as e:
        app.log_exception(e)
        return jsonify({"error": INTERNAL_SERVER_ERROR}), 500
