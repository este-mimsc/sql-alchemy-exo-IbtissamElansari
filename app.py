from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    from models import User, Post

    @app.route("/")
    def index():
        return jsonify({"message": "Welcome to the Flask + SQLAlchemy assignment"})

    # ---------------------------
    #   USERS ROUTES
    # ---------------------------
    @app.route("/users", methods=["GET", "POST"])
    def users():

        if request.method == "GET":
            users = User.query.all()
            return jsonify([u.to_dict() for u in users]), 200

        if request.method == "POST":
            data = request.get_json()

            if not data or "username" not in data:
                return jsonify({"error": "username is required"}), 400

            new_user = User(username=data["username"])
            db.session.add(new_user)

            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                return jsonify({"error": "username must be unique"}), 400

            return jsonify(new_user.to_dict()), 201

    # ---------------------------
    #   POSTS ROUTES
    # ---------------------------
    @app.route("/posts", methods=["GET", "POST"])
    def posts():

        if request.method == "GET":
            posts = Post.query.all()
            return jsonify([p.to_dict() for p in posts]), 200

        if request.method == "POST":
            data = request.get_json()

            required = ("title", "content", "user_id")
            if not all(key in data for key in required):
                return jsonify({"error": "title, content and user_id required"}), 400

            user = db.session.get(User, data["user_id"])
            if not user:
                return jsonify({"error": "user_id does not exist"}), 400

            new_post = Post(
                title=data["title"],
                content=data["content"],
                user_id=data["user_id"],
            )
            db.session.add(new_post)
            db.session.commit()

            return jsonify(new_post.to_dict()), 201

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
