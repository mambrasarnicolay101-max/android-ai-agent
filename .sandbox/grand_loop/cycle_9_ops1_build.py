// backend/server.js
const express = require('express');
const app = express();
const mongoose = require('mongoose');
const jwt = require('jsonwebtoken');

// Koneksi database
mongoose.connect('mongodb://localhost/socialcardgenerator', { useNewUrlParser: true, useUnifiedTopology: true });

// Model untuk kartu sosial
const socialCardModel = mongoose.model('SocialCard', {
  title: String,
  description: String,
  imageUrl: String
});

// Autentikasi dengan JWT
app.post('/login', (req, res) => {
  const { username, password } = req.body;
  if (username === 'admin' && password === 'password') {
    const token = jwt.sign({ username: 'admin' }, 'secretkey', { expiresIn: '1h' });
    res.json({ token });
  } else {
    res.status(401).json({ message: 'Invalid username or password' });
  }
});

// API untuk menghasilkan kartu sosial
app.post('/generate', authenticate, (req, res) => {
  const { title, description, imageUrl } = req.body;
  const socialCard = new socialCardModel({ title, description, imageUrl });
  socialCard.save((err, data) => {
    if (err) {
      res.status(500).json({ message: 'Gagal menghasilkan kartu sosial' });
    } else {
      res.json({ message: 'Kartu sosial berhasil dihasilkan' });
    }
  });
});

// Middleware untuk autentikasi
function authenticate(req, res, next) {
  const token = req.header('Authorization');
  if (!token) return res.status(401).json({ message: 'Unauthorized' });
  jwt.verify(token, 'secretkey', (err, decoded) => {
    if (err) return res.status(401).json({ message: 'Invalid token' });
    req.user = decoded;
    next();
  });
}

app.listen(3000, () => {
  console.log('Server listening on port 3000');
});
