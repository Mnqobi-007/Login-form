#backend.py file
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
#import jwt
import datetime

app = Flask(__name__)
CORS(app)  # allow frontend to connect

# Secret key for JWT
app.config['SECRET_KEY'] = "supersecretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///speedsta.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# ================= MODELS =================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password = db.Column(db.String(200), nullable=False)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    rating = db.Column(db.Integer)
    category = db.Column(db.String(50))
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

@app.route("/")
def home():
    return render_template("form.html")

# ================= ROUTES =================

@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "User already exists"}), 400

    hashed_pw = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    user = User(fullname=data["fullname"], email=data["email"],
                phone=data.get("phone"), password=hashed_pw)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "✅ User registered successfully"})


@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(email=data["email"]).first()
    if not user or not bcrypt.check_password_hash(user.password, data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({"message": "✅ Login successful", "user": user.fullname})

@app.route("/api/feedback", methods=["POST"])
def feedback():
    data = request.json
    fb = Feedback(name=data.get("name"), email=data.get("email"),
                  rating=data.get("rating"), category=data.get("category"),
                  message=data.get("message"))
    db.session.add(fb)
    db.session.commit()
    return jsonify({"message": "✅ Feedback submitted"})

# ================= MAIN =================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
