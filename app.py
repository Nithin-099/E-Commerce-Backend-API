from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)

# Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['JWT_SECRET_KEY'] = 'supersecretkey'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    product_id = db.Column(db.Integer)

# Create DB
with app.app_context():
    db.create_all()

# Register
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(username=data['username'], password=hashed_pw)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"})

# Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        token = create_access_token(identity=user.id)
        return jsonify({"access_token": token})
    return jsonify({"message": "Invalid credentials"}), 401

# Add Product
@app.route('/product', methods=['POST'])
@jwt_required()
def add_product():
    data = request.json
    product = Product(name=data['name'], price=data['price'])
    db.session.add(product)
    db.session.commit()
    return jsonify({"message": "Product added successfully"})

# Get Products
@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    result = [{"id": p.id, "name": p.name, "price": p.price} for p in products]
    return jsonify(result)

# Place Order
@app.route('/order', methods=['POST'])
@jwt_required()
def place_order():
    user_id = get_jwt_identity()
    data = request.json
    order = Order(user_id=user_id, product_id=data['product_id'])
    db.session.add(order)
    db.session.commit()
    return jsonify({"message": "Order placed successfully"})

if __name__ == '__main__':
    app.run(debug=True)
