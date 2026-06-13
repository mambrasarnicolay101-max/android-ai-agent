const express = require('express');
const app = express();
const mongoose = require('mongoose');
const jwt = require('jsonwebtoken');

// Koneksi ke MongoDB
mongoose.connect('mongodb://localhost/social-media-carousel', { useNewUrlParser: true, useUnifiedTopology: true });

// Model untuk Carousel
const carouselSchema = new mongoose.Schema({
  title: String,
  images: [String],
  description: String
});
const Carousel = mongoose.model('Carousel', carouselSchema);

// Autentikasi dengan JWT
app.post('/login', (req, res) => {
  const { username, password } = req.body;
  // Proses autentikasi sederhana, dalam aplikasi nyata gunakan bcrypt atau similar
  if (username === 'admin' && password === 'password') {
    const token = jwt.sign({ username }, 'secretkey');
    res.json({ token });
  } else {
    res.status(401).json({ message: 'Invalid credentials' });
  }
});

// API untuk membuat carousel
app.post('/carousel', authenticate, (req, res) => {
  const { title, images, description } = req.body;
  const carousel = new Carousel({ title, images, description });
  carousel.save((err, carousel) => {
    if (err) {
      res.status(500).json({ message: 'Gagal membuat carousel' });
    } else {
      res.json(carousel);
    }
  });
});

// Middleware untuk autentikasi
function authenticate(req, res, next) {
  const token = req.header('Authorization');
  if (!token) return res.status(401).json({ message: 'Unauthorized' });
  try {
    const decoded = jwt.verify(token, 'secretkey');
    req.user = decoded;
    next();
  } catch (ex) {
    res.status(400).json({ message: 'Invalid token' });
  }
}

app.listen(3000, () => console.log('Server berjalan di port 3000'));
