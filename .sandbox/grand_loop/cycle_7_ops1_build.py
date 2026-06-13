// Backend (server.js)
const express = require('express');
const app = express();
const mongoose = require('mongoose');
const jwt = require('jsonwebtoken');

// Koneksi ke MongoDB
mongoose.connect('mongodb://localhost/socialcardgenerator', { useNewUrlParser: true, useUnifiedTopology: true });

// Model untuk kartu sosial
const socialCardModel = mongoose.model('SocialCard', {
  title: String,
  description: String,
  imageUrl: String,
  userId: String
});

// Autentikasi dengan JWT
app.post('/login', (req, res) => {
  const { username, password } = req.body;
  // Logika autentikasi sederhana
  if (username === 'admin' && password === 'password') {
    const token = jwt.sign({ userId: '1' }, 'secretkey');
    res.json({ token });
  } else {
    res.status(401).json({ message: 'Invalid credentials' });
  }
});

//Endpoint untuk membuat kartu sosial
app.post('/create-social-card', authenticate, (req, res) => {
  const { title, description, imageUrl } = req.body;
  const socialCard = new socialCardModel({ title, description, imageUrl, userId: req.user.userId });
  socialCard.save((err, data) => {
    if (err) {
      res.status(500).json({ message: 'Gagal membuat kartu sosial' });
    } else {
      res.json({ message: 'Kartu sosial berhasil dibuat' });
    }
  });
});

// Middleware untuk autentikasi
function authenticate(req, res, next) {
  const token = req.header('Authorization');
  if (!token) return res.status(401).json({ message: 'Akses ditolak' });
  try {
    const decoded = jwt.verify(token, 'secretkey');
    req.user = decoded;
    next();
  } catch (ex) {
    res.status(400).json({ message: 'Token tidak valid' });
  }
}

app.listen(3000, () => {
  console.log('Server berjalan pada port 3000');
});

// Frontend (main.js)
import Vue from 'vue';
import App from './App.vue';
import axios from 'axios';

Vue.prototype.$axios = axios;

new Vue({
  render: h => h(App)
}).$mount('#app');
