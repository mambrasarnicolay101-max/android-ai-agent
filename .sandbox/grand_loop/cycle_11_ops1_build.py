# Backend (Flask)
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from pymongo import MongoClient
from guizang_social_card_skill import generate_carousel

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret'
jwt = JWTManager(app)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['social_media']

# Register user
@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    user = db.users.find_one({'username': username})
    if user:
        return jsonify({'error': 'Username already exists'}), 400
    db.users.insert_one({'username': username, 'password': password})
    return jsonify({'message': 'User created successfully'}), 201

# Login user
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    user = db.users.find_one({'username': username, 'password': password})
    if not user:
        return jsonify({'error': 'Invalid username or password'}), 401
    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token}), 200

# Generate carousel
@app.route('/generate', methods=['POST'])
@jwt_required()
def generate_carousel_route():
    text = request.json.get('text')
    carousel = generate_carousel(text)
    return jsonify({'carousel': carousel}), 200

if __name__ == '__main__':
    app.run(debug=True)

# Frontend (Vue.js)
import Vue from 'vue'
import axios from 'axios'

new Vue({
  el: '#app',
  data: {
    text: '',
    carousel: ''
  },
  methods: {
    generateCarousel() {
      axios.post('/generate', { text: this.text })
        .then(response => {
          this.carousel = response.data.carousel
        })
        .catch(error => {
          console.error(error)
        })
    }
  }
})
