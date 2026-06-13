// backend/server.js
const express = require('express');
const mongoose = require('mongoose');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const app = express();
app.use(express.json());

// Koneksi MongoDB
mongoose.connect('mongodb://localhost/social-media-carousel', { useNewUrlParser: true, useUnifiedTopology: true });

// Schema pengguna
const userSchema = new mongoose.Schema({
  username: String,
  password: String,
  carousels: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Carousel' }]
});
const User = mongoose.model('User', userSchema);

// Schema carousel
const carouselSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
  title: String,
  images: [String]
});
const Carousel = mongoose.model('Carousel', carouselSchema);

// Autentikasi pengguna
app.post('/login', async (req, res) => {
  const { username, password } = req.body;
  const user = await User.findOne({ username });
  if (!user || !(await bcrypt.compare(password, user.password))) {
    return res.status(401).send('Username atau password salah');
  }
  const token = jwt.sign({ userId: user._id }, 'secretkey', { expiresIn: '1h' });
  res.send({ token });
});

// Buat carousel baru
app.post('/carousels', async (req, res) => {
  const { title, images } = req.body;
  const userId = req.user._id;
  const carousel = new Carousel({ userId, title, images });
  await carousel.save();
  res.send(carousel);
});

// Dapatkan semua carousel pengguna
app.get('/carousels', async (req, res) => {
  const userId = req.user._id;
  const carousels = await Carousel.find({ userId });
  res.send(carousels);
});

app.listen(3000, () => {
  console.log('Server berjalan di port 3000');
});

