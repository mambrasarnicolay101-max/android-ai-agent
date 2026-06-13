const express = require('express');
const app = express();
const mongoose = require('mongoose');
const jwt = require('jsonwebtoken');

mongoose.connect('mongodb://localhost/socialcardgenerator', { useNewUrlParser: true, useUnifiedTopology: true });

const Template = mongoose.model('Template', {
  name: String,
  description: String,
  image: String
});

app.use(express.json());

app.post('/template', async (req, res) => {
  const template = new Template(req.body);
  try {
    await template.save();
    res.send('Template berhasil dibuat');
  } catch (err) {
    res.status(500).send('Gagal membuat template');
  }
});

app.get('/template', async (req, res) => {
  try {
    const templates = await Template.find().exec();
    res.send(templates);
  } catch (err) {
    res.status(500).send('Gagal mengambil template');
  }
});

app.post('/auth', (req, res) => {
  const token = jwt.sign(req.body, 'secretkey', { expiresIn: '1h' });
  res.send(token);
});

app.use((req, res, next) => {
  const token = req.header('Authorization');
  if (!token) return res.status(401).send('Anda belum login');
  jwt.verify(token, 'secretkey', (err, user) => {
    if (err) return res.status(401).send('Token tidak valid');
    req.user = user;
    next();
  });
});

app.listen(3000, () => {
  console.log('Server berjalan pada port 3000');
});
