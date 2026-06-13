from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from pymongo import MongoClient

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!
jwt = JWTManager(app)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['social-media']
collection = db['posts']

# Register API
@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    # Simpan ke database
    collection.insert_one({'username': username, 'password': password})
    return jsonify({'msg': 'User created successfully'}), 201

# Login API
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    # Cek di database
    user = collection.find_one({'username': username, 'password': password})
    if user:
        access_token = create_access_token(identity=username)
        return jsonify({'access_token': access_token}), 200
    return jsonify({'msg': 'Invalid credentials'}), 401

# Protected API dengan JWT
@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    return jsonify({'msg': 'Hello, {}'.format(get_jwt_identity())}), 200

# API untuk generate Xiaohongshu carousels & WeChat 21:9+1:1 card
@app.route('/generate-card', methods=['POST'])
@jwt_required
def generate_card():
    # Implementasi generate card menggunakan op7418/guizang-social-card-skill
    # ...
    return jsonify({'msg': 'Card generated successfully'}), 201

if __name__ == '__main__':
    app.run(debug=True)
