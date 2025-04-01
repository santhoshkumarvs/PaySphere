from flask import Flask, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt  # For password hashing
from database import db
from models import User

# Initialize Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Replace with a strong secret key

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Route for the root path
@app.route('/', methods=['GET'])
def home():
    return {"message": "Welcome to PaySphere!"}

# Route to handle the favicon request
@app.route('/favicon.ico', methods=['GET'])
def favicon():
    return '', 204

# Route to add a new user (registration)
@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(email=data['email'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return {"message": "User registered successfully!"}, 201

# Route for user login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=str(user.id))  # Pass user ID as a string
        return {"access_token": access_token}, 200
    return {"message": "Invalid credentials"}, 401

# Protected route (requires JWT token)
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = int(get_jwt_identity())  # Retrieve identity from the token
    user = User.query.get(current_user_id)
    return {"message": f"Hello, {user.email}!"}

# Route to fetch all users
@app.route('/get_users', methods=['GET'])
def get_users():
    users = User.query.all()
    return {"users": [{"id": user.id, "email": user.email} for user in users]}

# Main entry point
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)  # Run the Flask application
