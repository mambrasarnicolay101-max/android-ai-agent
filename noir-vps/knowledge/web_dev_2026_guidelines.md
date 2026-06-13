# Panduan Utama: Pengembangan Web & Produk Digital 2026 (NOIR AI CORE KNOWLEDGE)

Sebagai agen mandiri, setiap kali Anda diinstruksikan untuk membuat sistem web atau aplikasi, Anda WAJIB mengikuti arsitektur ini:

## 1. Arsitektur AI-Native
- **Agentic Logic:** Jangan hanya membuat aplikasi CRUD biasa. Sisipkan logika agen/LLM di sisi backend jika memungkinkan.
- **Serverless & Edge:** Asumsikan aplikasi akan di-deploy ke Edge (seperti Cloudflare Workers/Vercel).

## 2. Stack Teknologi Wajib
- **Frontend Kompleks:** Gunakan **Vite + React (TypeScript)** atau **Next.js 19**.
- **Frontend Sederhana (Vanilla):** Gunakan pola desain "Glassmorphism" murni, animasi mikro halus, dan dark mode yang elegan. Tidak boleh menggunakan desain kaku gaya 2010.
- **Styling:** Vanilla CSS (dengan variabel root) atau TailwindCSS. Jangan gunakan library Bootstrap.

## 3. Metodologi Penulisan Kode (TDD & DevSecOps)
- Jangan menulis kode bisnis sebelum memikirkan pengujiannya (TDD mindset).
- Pastikan keamanan API (CORS, validasi input, pencegahan SQLi) diimplementasikan sejak dari fondasi, bukan sebagai perbaikan (Zero-trust approach).
- Hindari manajemen state yang terlalu gemuk (seperti Redux lama); gunakan Zustand atau React Context sederhana.

*Catatan: Dokumen ini dimuat secara otomatis oleh OmniRouter saat mensintesis skill atau mengevaluasi kode pembangunan aplikasi.*
