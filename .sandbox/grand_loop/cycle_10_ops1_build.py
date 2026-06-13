// Backend (server.js)
const express = require('express');
const mongoose = require('mongoose');
const jwt = require('jsonwebtoken');
const app = express();
app.use(express.json());

// Koneksi ke MongoDB
mongoose.connect('mongodb://localhost:27017/carousel', { useNewUrlParser: true, useUnifiedTopology: true });

// Schema untuk carousel
const carouselSchema = new mongoose.Schema({
  title: String,
  description: String,
  images: [String]
});
const Carousel = mongoose.model('Carousel', carouselSchema);

// Autentikasi menggunakan JWT
app.post('/login', (req, res) => {
  const { username, password } = req.body;
  if (username === 'admin' && password === 'password') {
    const token = jwt.sign({ username }, 'secretkey', { expiresIn: '1h' });
    res.json({ token });
  } else {
    res.status(401).json({ message: 'Invalid credentials' });
  }
});

// Protected route untuk membuat carousel
app.post('/carousel', authenticateToken, (req, res) => {
  const { title, description, images } = req.body;
  const carousel = new Carousel({ title, description, images });
  carousel.save((err, carousel) => {
    if (err) {
      res.status(500).json({ message: 'Gagal membuat carousel' });
    } else {
      res.json(carousel);
    }
  });
});

// Middleware untuk autentikasi
function authenticateToken(req, res, next) {
  const token = req.header('Authorization');
  if (!token) return res.status(401).json({ message: 'Unauthorized' });
  jwt.verify(token, 'secretkey', (err, user) => {
    if (err) return res.status(403).json({ message: 'Forbidden' });
    req.user = user;
    next();
  });
}

app.listen(3000, () => {
  console.log('Server berjalan pada port 3000');
});

// Frontend (main.js)
import Vue from 'vue'
import App from './App.vue'
import axios from 'axios'

Vue.prototype.$axios = axios

new Vue({
  render: h => h(App),
}).$mount('#app')

// File App.vue
<template>
  <div>
    <h1>Social Media Carousel Generator</h1>
    <form @submit.prevent="buatCarousel">
      <input v-model="title" type="text" placeholder="Judul">
      <textarea v-model="description" placeholder="Deskripsi"></textarea>
      <input v-model="images" type="text" placeholder="URL Gambar (pisahkan dengan koma)">
      <button type="submit">Buat Carousel</button>
    </form>
    <ul>
      <li v-for="carousel in carousels" :key="carousel._id">
        {{ carousel.title }}
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  data() {
    return {
      title: '',
      description: '',
      images: '',
      carousels: []
    }
  },
  mounted() {
    this.$axios.get('http://localhost:3000/carousel')
      .then(response => {
        this.carousels = response.data
      })
      .catch(error => {
        console.log(error)
      })
  },
  methods: {
    buatCarousel() {
      this.$axios.post('http://localhost:3000/carousel', {
        title: this.title,
        description: this.description,
        images: this.images.split(',')
      })
      .then(response => {
        this.carousels.push(response.data)
        this.title = ''
        this.description = ''
        this.images = ''
      })
      .catch(error => {
        console.log(error)
      })
    }
  }
}
</script>
