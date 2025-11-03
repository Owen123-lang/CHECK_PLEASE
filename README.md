# Check Please - Asisten Riset AI

**Check Please** adalah aplikasi web yang dirancang sebagai asisten riset cerdas, menggunakan arsitektur **Agentic RAG (Retrieval-Augmented Generation)** untuk melakukan verifikasi dan kompilasi profil akademis secara otonom.

Aplikasi ini memungkinkan pengguna untuk mengajukan pertanyaan dalam bahasa alami, memberikan sumber URL tambahan, dan menerima jawaban komprehensif yang didukung oleh data dari basis pengetahuan vektor dan sumber web real-time.

**🆕 NEW FEATURE: AI-Powered CV Generation** - Sistem sekarang dapat menghasilkan CV (Curriculum Vitae) profesional dalam format PDF untuk dosen/profesor berdasarkan percakapan dengan chatbot!

---

## 📋 Daftar Isi

1.  [Arsitektur & Alur Kerja](#-arsitektur--alur-kerja)
2.  [Teknologi yang Digunakan](#-teknologi-yang-digunakan)
3.  [Struktur Proyek](#-struktur-proyek)
4.  [Panduan Instalasi](#-panduan-instalasi)
5.  [Cara Menjalankan](#-cara-menjalankan)
6.  [Fitur CV Generation](#-fitur-cv-generation)
7.  [Kendala & Solusi](#-kendala--solusi)
8.  [Changelog](#-changelog)

---

## 🏗️ Arsitektur & Alur Kerja

Aplikasi ini menggunakan arsitektur 3-lapis yang terdiri dari Frontend, Backend, dan AI Layer.

**Alur Kerja Proses RAG:**

1.  **Permintaan Pengguna**: Pengguna memasukkan kueri dan secara opsional menambahkan URL sumber melalui **Frontend (Next.js)**.
2.  **Penerimaan API**: **Backend (FastAPI)** menerima permintaan pada endpoint `/api/chat`.
3.  **Inisialisasi Crew**: `agent_core.py` menginisialisasi `AgenticCrew` yang menggunakan **Google Gemini 1.5 Flash** sebagai LLM.
4.  **Eksekusi Tugas (Task Execution)**:
    - **Agen RAG** diberi tugas untuk menjawab kueri pengguna.
    - **Tool 1: `DynamicWebScraperTool`**: Jika pengguna memberikan URL, agen menggunakan tool ini untuk mengekstrak konten.
    - **Tool 2: `PrimaryVectorSearchTool`**: Agen mencari informasi relevan di **Astra DB** (vector database).
5.  **Sintesis & Generasi**: Agen menganalisis konteks dari kedua tool, lalu menggunakan **Gemini LLM** untuk merumuskan jawaban.
6.  **Pengiriman Respons**: Jawaban dikirim ke frontend untuk ditampilkan.

---

## 🛠️ Teknologi yang Digunakan

| Kategori      | Teknologi                                                              | Deskripsi                                           |
| :------------ | :--------------------------------------------------------------------- | :-------------------------------------------------- |
| **Frontend**  | [Next.js](https://nextjs.org/), [React](https://reactjs.org/), [TypeScript](https://www.typescriptlang.org/) | Framework untuk antarmuka pengguna yang modern.     |
|               | [Tailwind CSS](https://tailwindcss.com/)                               | Styling UI dengan tema "Saul Goodman".              |
| **Backend**   | [FastAPI](https://fastapi.tiangolo.com/), [Python](https://www.python.org/) | Framework API berperforma tinggi.                   |
| **AI Layer**  | [CrewAI](https://www.crewai.com/)                                      | Framework untuk membangun agen AI kolaboratif.      |
|               | [Google Gemini 1.5 Flash](https://ai.google.dev/)                      | LLM untuk reasoning dan function calling.           |
|               | [LangChain](https://www.langchain.com/)                                | Orkestrasi untuk tool dan komponen AI.              |
| **Database**  | [Astra DB](https://www.datastax.com/products/astra-db)                 | Database vektor cloud untuk pencarian RAG.          |
| **PDF**       | [WeasyPrint](https://weasyprint.org/)                                  | Library untuk membuat laporan PDF dari HTML.        |
|               | [Jinja2](https://palletsprojects.com/p/jinja/)                         | Template engine untuk rendering HTML.               |

---

## 📁 Struktur Proyek

```
CheckPlease_terbaru/
├── backend/
│   ├── .env                  # Environment variables (TIDAK di-commit ke git)
│   ├── .env.example          # Template environment variables
│   ├── requirements.txt      # Dependensi Python
│   ├── main.py               # Server FastAPI utama
│   ├── agent_core.py         # Logika inti CrewAI & inisialisasi LLM
│   ├── tools.py              # Tools untuk RAG (Astra DB & Web Scraper)
│   ├── pdf_generator.py      # Generator PDF
│   └── templates/
│       └── pdf_template.html # Template HTML untuk PDF
└── frontend/
    ├── package.json          # Dependensi Node.js
    ├── next.config.js        # Konfigurasi Next.js
    ├── tailwind.config.ts    # Konfigurasi tema Tailwind CSS
    └── app/
        ├── page.tsx          # Halaman landing
        ├── dashboard/        # Dashboard notebooks
        └── chat/             # Halaman chat utama
```

---

## 🔧 Panduan Instalasi

### Prasyarat

- **Python 3.9+**
- **Node.js 18+**
- **Akun Astra DB**: Database gratis dengan token dan API endpoint
- **Google Gemini API Key**: Dari [Google AI Studio](https://makersuite.google.com/app/apikey)

### ⚙️ Setup Backend

1.  **Masuk ke folder backend**
    ```bash
    cd backend
    ```

2.  **Buat dan aktifkan virtual environment**
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # macOS / Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependensi Python**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Setup environment variables**
    - File `.env` sudah ada dengan kredensial yang benar ✅
    - Pastikan isinya seperti ini:
    ```env
    ASTRA_DB_NAMESPACE=default_keyspace
    ASTRA_DB_COLLECTION=f1gpt
    ASTRA_DB_API_ENDPOINT=https://your-database-id.apps.astra.datastax.com
    ASTRA_DB_APPLICATION_TOKEN=AstraCS:xxxxx...
    GEMINI_API_KEY=AIzaSy...
    TAVILY_API_KEY=tvly-...
    ```

### 🎨 Setup Frontend

1.  **Masuk ke folder frontend**
    ```bash
    cd frontend
    ```

2.  **Install dependensi Node.js**
    ```bash
    npm install
    ```

---

## ▶️ Cara Menjalankan

### 1. Jalankan Backend Server

Dari folder `backend/`:
```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Output yang diharapkan:**
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 2. Jalankan Frontend Server

Buka **terminal baru**, dari folder `frontend/`:
```bash
npm run dev
```

**Output yang diharapkan:**
```
✓ Ready in 5s
○ Local:        http://localhost:3001
```

*(Port 3001 karena port 3000 sudah digunakan)*

### 3. Buka Aplikasi

- **Landing Page**: `http://localhost:3001`
- **Dashboard**: `http://localhost:3001/dashboard`
- **Chat Interface**: `http://localhost:3001/chat`

---

## 📄 Fitur CV Generation

### Cara Menggunakan CV Generator

1. **Melalui Chat:**
   ```
   User: "Generate CV for Prof. Dr. Riri Fitri Sari"
   AI: [Mengumpulkan data dari database, SINTA, Google Scholar]
   AI: "✅ CV data collected successfully..."
   ```

2. **Melalui API Endpoint:**
   ```bash
   POST /api/generate-cv
   {
     "professor_name": "Prof. Dr. Riri Fitri Sari",
     "session_id": "optional-session-id"
   }
   ```

3. **Sumber Data CV:**
   - **Database Internal**: Profil akademik dari Astra DB
   - **SINTA**: Score, publikasi nasional, afiliasi
   - **Google Scholar**: Sitasi, publikasi internasional
   - **Web Search**: Informasi tambahan dari web
   - **Conversation Context**: Data dari percakapan sebelumnya (jika ada session_id)

4. **Format CV yang Dihasilkan:**
   - Header profesional dengan nama, gelar, afiliasi
   - Metrics (SINTA Score, Google Scholar, Scopus)
   - Research Areas (bidang penelitian)
   - Education (pendidikan)
   - Academic Positions (jabatan akademik)
   - Selected Publications (maksimal 10 publikasi utama)
   - Awards & Honors
   - Teaching (mata kuliah yang diajar)
   - External Profiles (link ke Google Scholar, Scopus, dll)

### Contoh Penggunaan

**Dalam Bahasa Indonesia:**
```
"Buatkan CV untuk Prof. Muhammad Suryanegara"
"Generate CV Prof. Dadang Gunawan"
"Create curriculum vitae untuk Dr. Anak Agung"
```

**Dalam Bahasa Inggris:**
```
"Generate CV for Prof. Dr. Riri Fitri Sari"
"Create CV for Prof. Suryadibrata"
"Make curriculum vitae for Dr. Muhamad Asvial"
```

### Teknologi CV Generation

- **PDF Generation**: WeasyPrint (HTML to PDF)
- **Template Engine**: Jinja2
- **Data Parsing**: Regex + NLP untuk ekstraksi informasi
- **Multi-Source Aggregation**: Menggabungkan data dari 4+ sumber
- **Context-Aware**: Menggunakan riwayat percakapan untuk memperkaya data

### API Response

Ketika CV berhasil dibuat, API akan mengembalikan:
- **Content-Type**: `application/pdf`
- **Filename**: `CV_[Nama]_[Tanggal].pdf`
- **Size**: Biasanya 100-500 KB tergantung jumlah publikasi

---

## 🚨 Kendala & Solusi

### 1. ❌ Error: "OPENAI_API_KEY is required"

**Masalah**: CrewAI mencoba menggunakan OpenAI ketika seharusnya menggunakan Gemini.

**Penyebab**: Format inisialisasi LLM tidak spesifik untuk Gemini.

**Solusi**: ✅ **SUDAH DIPERBAIKI** di `agent_core.py`:
```python
self.llm = LLM(
    model="gemini/gemini-1.5-flash",  # Format: provider/model
    api_key=api_key,
    temperature=0.7
)
```

---

### 2. ❌ Error: "Tool Usage Failed - Input should be a valid string"

**Masalah**: Ollama llama3 mengirim format argument yang salah ke tools.

**Penyebab**: Ollama llama3 **tidak mendukung function calling** yang dibutuhkan CrewAI.

**Solusi**: ✅ **Kembali menggunakan Gemini** yang mendukung function calling dengan sempurna.

**Catatan**: Jika ingin menggunakan Ollama di masa depan, gunakan model yang support function calling seperti:
- `llama3.1` (lebih baru dari llama3)
- `mistral-nemo`
- `qwen2.5`

---

### 3. ❌ Error: `ollama pull llama3` - "max retries exceeded"

**Masalah**: Error saat download model Ollama.

**Penyebab**: Masalah koneksi internet, DNS, atau firewall.

**Solusi**:
1. Restart Ollama service
2. Coba lagi: `ollama pull llama3`
3. Jika masih gagal, coba model lebih kecil: `ollama pull llama3:8b`
4. Ganti DNS ke `1.1.1.1` atau `8.8.8.8`

**Catatan**: Karena Ollama tidak support function calling dengan baik, **tidak perlu lagi pull model Ollama** untuk aplikasi ini.

---

### 4. ❌ Frontend Error: "ERR_CONNECTION_REFUSED"

**Masalah**: Frontend tidak bisa connect ke backend.

**Penyebab**:
- Backend belum berjalan
- CORS configuration salah

**Solusi**: ✅ **SUDAH DIPERBAIKI**:
1. Backend sudah menambahkan `localhost:3001` ke CORS origins
2. Pastikan backend berjalan di port 8000
3. Pastikan frontend berjalan di port 3001

---

### 5. ⚠️ Response AI Lambat

**Normal!** Response memakan waktu **30-60 detik** karena:
1. Agent harus memanggil **Astra DB** untuk vector search
2. Agent harus memanggil **Gemini API** (internet required)
3. CrewAI melakukan **multi-step reasoning**

**Tip**: Jangan refresh halaman sampai response muncul!

---

## 📝 Changelog

### Version 0.4.0 (Latest)
- ✅ **NEW**: AI-powered CV generation from chat conversations
- ✅ **NEW**: Multi-source data aggregation (DB + SINTA + Scholar + Web)
- ✅ **NEW**: Professional academic CV template
- ✅ **NEW**: Session-based conversation tracking
- ✅ **NEW**: Context-aware CV generation using chat history
- ✅ **NEW**: `/api/generate-cv` endpoint for CV download
- ✅ **IMPROVED**: CV Generator Tool integrated with CrewAI agent
- ✅ **IMPROVED**: Automatic data parsing and structuring

### Version 0.3.0
- ✅ Hybrid RAG system with intelligent routing
- ✅ SINTA scraper integration
- ✅ Google Scholar search integration
- ✅ Improved web scraping with retry mechanism

---

## 🎯 Fitur Utama

### Backend API
- **GET /** - Health check endpoint
- **POST /api/chat** - RAG chat endpoint dengan support untuk multiple URLs
- **POST /api/generate-pdf** - PDF generator untuk export hasil
- **POST /api/generate-cv** - CV generator untuk dosen/profesor

### Frontend UI
- **Landing Page**: Hero section dengan branding "Check Please"
- **Dashboard**: Notebook management dengan placeholder projects
- **Chat Interface**: 3-kolom layout (Sources, Chat, Studio)
- **URL Input**: Support untuk menambahkan multiple URL sebagai context

---

## 🔐 Security Notes

**PENTING**: File `.env` mengandung kredensial sensitif dan **TIDAK boleh** di-commit ke Git.

Pastikan `.gitignore` sudah mengandung:
```
.env
```

---

## 📧 Support

Jika ada pertanyaan atau masalah, silakan:
1. Cek bagian [Kendala & Solusi](#-kendala--solusi) terlebih dahulu
2. Jalankan test script: `python backend/test_connections.py`
3. Cek log di terminal backend untuk error details

---

## 📄 License

MIT License

---

**Built with ❤️ using Next.js, FastAPI, CrewAI, and Google Gemini**
