// backend/server.js
const express = require('express');
const app = express();
const mongoose = require('mongoose');
const jwt = require('jsonwebtoken');

// Koneksi ke database
mongoose.connect('mongodb://localhost/socialcardgenerator', { useNewUrlParser: true, useUnifiedTopology: true });

// Schema untuk kartu sosial
const socialCardSchema = new mongoose.Schema({
  title: String,
  description: String,
  image: String
});

// Model untuk kartu sosial
const SocialCard = mongoose.model('SocialCard', socialCardSchema);

// Middleware untuk autentikasi
const authenticate = (req, res, next) => {
  const token = req.header('Authorization');
  if (!token) return res.status(401).send('Unauthorized');
  try {
    const decoded = jwt.verify(token, 'secretkey');
    req.user = decoded;
    next();
  } catch (err) {
    res.status(400).send('Invalid token');
  }
};

// API untuk membuat kartu sosial
app.post('/socialcards', authenticate, (req, res) => {
  const socialCard = new SocialCard(req.body);
  socialCard.save((err, socialCard) => {
    if (err) return res.status(400).send(err);
    res.send(socialCard);
  });
});

// API untuk mengambil kartu sosial
app.get('/socialcards', authenticate, (req, res) => {
  SocialCard.find().then((socialCards) => {
    res.send(socialCards);
  }).catch((err) => {
    res.status(400).send(err);
  });
});

// Jalankan server
app.listen(3000, () => {
  console.log('Server berjalan pada port 3000');
});
