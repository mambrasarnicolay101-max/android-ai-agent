// package.json
{
  "name": "social-media-carousel-generator",
  "version": "1.0.0",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.17.1",
    "jsonwebtoken": "^8.5.1",
    "mongodb": "^4.3.1",
    "vue": "^2.6.12"
  }
}

// server.js (Backend)
const express = require('express');
const app = express();
const mongoose = require('mongoose');
const jwt = require('jsonwebtoken');

// Koneksi ke MongoDB
mongoose.connect('mongodb://localhost/social-media-carousel', { useNewUrlParser: true, useUnifiedTopology: true });

// Model untuk carousel
const carouselModel = mongoose.model('Carousel', {
  title: String,
  images: [String]
});

// Middleware untuk autentikasi
const authenticate = (req, res, next) => {
  const token = req.header('Authorization');
  if (!token) return res.status(401).send('Anda belum login');
  jwt.verify(token, 'secretkey', (err, user) => {
    if (err) return res.status(401).send('Token tidak valid');
    req.user = user;
    next();
  });
};

// Routes untuk CRUD carousel
app.use(express.json());
app.post('/carousel', authenticate, (req, res) => {
  const carousel = new carouselModel(req.body);
  carousel.save((err, carousel) => {
    if (err) return res.status(400).send(err);
    res.send(carousel);
  });
});

app.get('/carousel', authenticate, (req, res) => {
  carouselModel.find().then((carousels) => res.send(carousels));
});

app.put('/carousel/:id', authenticate, (req, res) => {
  carouselModel.findByIdAndUpdate(req.params.id, req.body, { new: true }, (err, carousel) => {
    if (err) return res.status(400).send(err);
    res.send(carousel);
  });
});

app.delete('/carousel/:id', authenticate, (req, res) => {
  carouselModel.findByIdAndRemove(req.params.id, (err, carousel) => {
    if (err) return res.status(400).send(err);
    res.send(carousel);
  });
});

// Route untuk login
app.post('/login', (req, res) => {
  const { username, password } = req.body;
  if (username === 'admin' && password === 'admin') {
    const token = jwt.sign({ username }, 'secretkey', { expiresIn: '1h' });
    res.send(token);
  } else {
    res.status(401).send('Username atau password salah');
  }
});

app.listen(3000, () => console.log('Server berjalan pada port 3000'));

// frontend.vue (Frontend)
<template>
  <div>
    <h1>Social Media Carousel Generator</h1>
    <form @submit.prevent="submitForm">
      <input type="text" v-model="title" placeholder="Judul">
      <input type="file" multiple @change="handleFileChange">
      <button type="submit">Simpan</button>
    </form>
    <div v-for="carousel in carousels" :key="carousel._id">
      <h2>{{ carousel.title }}</h2>
      <img v-for="image in carousel.images" :key="image" :src="image">
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      title: '',
      images: [],
      carousels: []
    }
  },
  methods: {
    submitForm() {
      // Kirim request ke backend untuk menyimpan carousel
      fetch('/carousel', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + this.token
        },
        body: JSON.stringify({ title: this.title, images: this.images })
      })
      .then(response => response.json())
      .then(carousel => console.log(carousel))
      .catch(error => console.error(error));
    },
    handleFileChange(event) {
      // Ambil file yang diupload dan simpan di array images
      this.images = Array.from(event.target.files);
    }
  },
  mounted() {
    // Ambil token dari local storage
    this.token = localStorage.getItem('token');
    // Kirim request ke backend untuk mengambil carousel
    fetch('/carousel', {
      method: 'GET',
      headers: {
        'Authorization': 'Bearer ' + this.token
      }
    })
    .then(response => response.json())
    .then(carousels => this.carousels = carousels)
    .catch(error => console.error(error));
  }
}
</script>
