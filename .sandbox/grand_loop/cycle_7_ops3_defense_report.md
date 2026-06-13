## PATCH CODE:
```python
# Backend (server.js)
const express = require('express');
const app = express();
const mongoose = require('mongoose');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');

// Koneksi ke MongoDB
mongoose.connect('mongodb://localhost/socialcardgenerator', { useNewUrlParser: true, useUnifiedTopology: true });

// Model untuk kartu sosial
const socialCardModel = mongoose.model('SocialCard', {
  title: String,
  description: String,
  imageUrl: String,
  userId: String
});

// Autentikasi dengan JWT dan password hashing
app.post('/login', (req, res) => {
  const { username, password } = req.body;
  // Logika autentikasi dengan password hashing
  const user = { username: 'admin', password: bcrypt.hashSync('password', 10) };
  if (username === user.username && bcrypt.compareSync(password, user.password)) {
    const token = jwt.sign({ userId: '1' }, process.env.SECRET_KEY, { expiresIn: '1h' });
    res.json({ token });
  } else {
    res.status(401).json({ message: 'Invalid credentials' });
  }
});

//Endpoint untuk membuat kartu sosial dengan autentikasi dan validasi input
app.post('/create-social-card', authenticate, (req, res) => {
  const { title, description, imageUrl } = req.body;
  if (!title || !description || !imageUrl) {
    res.status(400).json({ message: 'Invalid input' });
  } else {
    const socialCard = new socialCardModel({ title, description, imageUrl, userId: req.user.userId });
    socialCard.save((err, socialCard) => {
      if (err) {
        res.status(500).json({ message: 'Internal Server Error' });
      } else {
        res.json({ message: 'Social card created successfully' });
      }
    });
  }
});

// Autentikasi middleware
function authenticate(req, res, next) {
  const token = req.header('Authorization').replace('Bearer ', '');
  jwt.verify(token, process.env.SECRET_KEY, (err, decoded) => {
    if (err) {
      res.status(401).json({ message: 'Invalid token' });
    } else {
      req.user = decoded;
      next();
    }
  });
}
```

## YARA RULES:
```
rule detect_insecure_login {
  meta:
    description = "Insecure login attempt"
    author = "Blue Team"
  strings:
    $a = "username=admin&password=password"
  condition:
    $a
}

rule detect_jwt_token_manipulation {
  meta:
    description = "JWT token manipulation attempt"
    author = "Blue Team"
  strings:
    $a = "jwt.sign"
    $b = "jwt.verify"
  condition:
    $a or $b
}

rule detect_xss_attempt {
  meta:
    description = "XSS attempt"
    author = "Blue Team"
  strings:
    $a = "<script>"
  condition:
    $a
}
```

## FIREWALL RULES:
```
iptables -A INPUT -p tcp --dport 3000 -j ACCEPT
iptables -A INPUT -p tcp --dport 3000 -m string --algo kmp --string "username=admin&password=password" -j DROP
iptables -A INPUT -p tcp --dport 3000 -m string --algo kmp --string "<script>" -j DROP
```

## INCIDENT RESPONSE:
1. Identifikasi serangan dan dampaknya.
2. Isolasi sistem yang terkena serangan.
3. Analisis log untuk mengetahui sumber serangan.
4. Lakukan patching dan perbaikan kerentanan.
5. Monitor sistem untuk mencegah serangan serupa.

## KERENTANAN YANG TERLEWAT RED TEAM:
* Kerentanan SQL Injection pada query database.
* Kerentanan Cross-Site Request Forgery (CSRF) pada form submit.
* Kerentanan Insufficient Logging & Monitoring.

## REKOMENDASI ARSITEKTUR AMAN:
1. Gunakan arsitektur Microservices untuk memisahkan komponen-komponen sistem.
2. Implementasikan autentikasi dan autorisasi yang kuat.
3. Gunakan teknologi enkripsi untuk melindungi data sensitif.
4. Implementasikan monitoring dan logging yang efektif.
5. Lakukan testing keamanan secara teratur.

## MONITORING ALERT:
1. Buat rule untuk mendeteksi login gagal berulang-ulang.
2. Buat rule untuk mendeteksi trafik aneh pada port 3000.
3. Buat rule untuk mendeteksi query database yang mencurigakan.
4. Buat rule untuk mendeteksi aktivitas sistem yang tidak biasa.