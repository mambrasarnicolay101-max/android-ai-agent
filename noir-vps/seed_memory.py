from vector_memory import vector_memory as neural_memory

# Seeding Noir with essential local knowledge
essential_knowledge = [
    "Sistem Noir Sovereign V21.1 menggunakan port 8765 untuk dashboard utama.",
    "IP VPS Alibaba Cloud Noir adalah 8.215.23.17.",
    "Bypass SSL diaktifkan dengan NOIR_SSL_BYPASS=1 di file .env untuk mengatasi SSLEOFError.",

    "Penyimpanan sertifikat sistem Windows digunakan melalui modul pip-system-certs.",
    "Noir Sovereign memiliki 3 pilar kecerdasan lokal: Neural Memory, Local SLM, dan Pattern Recognition.",
    "Setiap aksi perangkat Android (screenshot, GPS, dll) dipicu melalui jalur Gateway terenkripsi AES-256-GCM."
]

for info in essential_knowledge:
    neural_memory.add_experience(info, category="system_core", source="seeding")

print(f"Neural Memory seeded with {len(essential_knowledge)} essential entries.")
