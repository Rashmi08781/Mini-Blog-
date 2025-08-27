from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from datetime import datetime

app = Flask(__name__)

# --- DATABASE CONFIG ---
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# --- MODEL ---
class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(120), default="anonymous")
    tags = db.Column(db.String(400), default="")
    published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "author": self.author,
            "tags": [t for t in self.tags.split(",") if t.strip()] if self.tags else [],
            "published": self.published,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def set_tags(self, tags_list):
        if isinstance(tags_list, list):
            self.tags = ",".join([t.strip() for t in tags_list if t and isinstance(t, str)])
        elif isinstance(tags_list, str):
            self.tags = tags_list
        else:
            self.tags = ""

# --- INIT DB ---
with app.app_context():
    db.create_all()

# --- HEALTH CHECK ---
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify(status="ok", time=datetime.utcnow().isoformat())

# --- CRUD API ENDPOINTS ---
@app.route("/api/posts", methods=["GET"])
def list_posts():
    q = request.args.get("q", type=str)
    tag = request.args.get("tag", type=str)
    posts = Post.query
    if q:
        like = f"%{q}%"
        posts = posts.filter(or_(Post.title.ilike(like), Post.content.ilike(like), Post.author.ilike(like)))
    if tag:
        posts = posts.filter(Post.tags.ilike(f"%{tag}%"))
    posts = posts.order_by(Post.created_at.desc())
    return jsonify([p.to_dict() for p in posts.all()])

@app.route("/api/posts/<int:post_id>", methods=["GET"])
def get_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify(error="Post not found"), 404
    return jsonify(post.to_dict())

@app.route("/api/posts", methods=["POST"])
def create_post():
    payload = request.get_json()
    post = Post(
        title=payload.get("title"),
        content=payload.get("content"),
        author=payload.get("author", "anonymous"),
        published=payload.get("published", False)
    )
    post.set_tags(payload.get("tags", []))
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_dict()), 201

@app.route("/api/posts/<int:post_id>", methods=["PUT", "PATCH"])
def update_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify(error="Post not found"), 404
    payload = request.get_json()
    if "title" in payload:
        post.title = payload["title"]
    if "content" in payload:
        post.content = payload["content"]
    if "author" in payload:
        post.author = payload["author"]
    if "tags" in payload:
        post.set_tags(payload["tags"])
    if "published" in payload:
        post.published = payload["published"]
    post.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(post.to_dict())

@app.route("/api/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify(error="Post not found"), 404
    db.session.delete(post)
    db.session.commit()
    return jsonify(ok=True, id=post_id)

# --- FRONTEND ---
@app.route("/")
def index():
    return render_template("index.html")

# --- RUN ---
if __name__ == "__main__":
    app.run(debug=True)
