# ⚖️ Advoin – AI Legal Assistant

## 🚀 RAG-Based Legal Chatbot with FIR Generation

<p align="center">
  <b>Upload Documents • Ask Questions • Generate FIRs</b><br/>
  <i>Making Legal Knowledge Accessible, Actionable, and Instant</i>
</p>

---

## 🧠 Overview

**Advoin** is a full-stack AI-powered legal assistant that allows users to:

- 📄 Upload legal documents (Constitution, Acts, Case Laws)
- 💬 Ask questions and get context-aware answers
- 📝 Generate structured FIRs as downloadable PDFs

Built using **Retrieval-Augmented Generation (RAG)**, the system ensures responses are **accurate, contextual, and grounded in real data**.



---

## ✨ Features

### 📄 Document Intelligence
- Upload and process legal PDFs
- Smart chunking and embedding

### 💬 AI Legal Chat
- Ask questions from uploaded documents
- Get precise, context-aware answers

### 🧠 RAG System
- Semantic search using embeddings
- ChromaDB for vector storage

### ⚡ Fast AI
- Powered by Groq for low-latency responses

### 📝 FIR Generator (🚀 Key Feature)
- Convert incident → structured FIR
- Suggest relevant IPC/BNS sections
- Download FIR as a clean PDF

### 🌙 Modern UI
- Clean, responsive dark interface

---

## 🛠️ Tech Stack

**Backend**
- FastAPI  
- LangChain  
- ChromaDB  
- PyPDF  
- Groq API  
- FPDF  

**Frontend**
- HTML5  
- CSS3  
- JavaScript  

---

## 🧑‍💻 Development Journey

This project was built after learning:

- HTML5 for structure  
- CSS3 for UI design  
- JavaScript for interactivity  

These fundamentals were used to build a complete full-stack AI application, integrating:

- Frontend interface  
- Backend APIs  
- RAG-based AI system  
- Legal document generation  

---

## 📂 Project Structure

```
advoin/
├── backend/
│   ├── app.py
│   ├── rag_pipeline.py
│   ├── fir_generator.py
│   ├── requirements.txt
│   └── .env
├── static/
│   ├── index.html
│   ├── style.css
│   └── main.js
└── README.md
```

---

## ⚙️ Setup

### 1. Clone Repository

```
git clone https://github.com/yourusername/advoin.git
cd advoin
```

### 2. Install Dependencies

```
cd backend
pip install -r requirements.txt
```

### 3. Add API Key

Create a `.env` file:

```
GROQ_API_KEY=your_api_key_here
```

### 4. Run Backend

```
uvicorn app:app --reload
```

### 5. Run Frontend

```
cd static
python -m http.server
```

Open in browser:  
http://localhost:8000

---

## 🔌 API Endpoints

| Endpoint         | Method | Description       |
|-----------------|--------|------------------|
| /api/upload     | POST   | Upload PDF       |
| /api/chat       | POST   | Ask questions    |
| /api/draft_fir  | POST   | Generate FIR PDF |

---

## 🧠 Workflow

```
PDF → Text → Embeddings → Vector DB
        ↓
User Query → Retrieval → AI Response
        ↓
FIR Request → AI Draft → PDF Generation
```

---

## 🎯 Use Cases

- ⚖️ Legal assistance  
- 📚 Law students  
- 🧑‍💼 Quick legal reference  
- 📝 FIR drafting  

---

## 🚀 Future Scope

- Multi-language FIR (Hindi/English)  
- Legal document generator (Notices, Agreements)  
- Authentication system  
- Chat history  
- Voice assistant  
- Mobile optimization  

---

## 🧪 Testing

- ✔ PDF Upload  
- ✔ Chat System  
- ✔ RAG Retrieval  
- ✔ FIR Generation  

---

## 💡 Vision

To build an AI legal ecosystem that simplifies legal knowledge and makes legal assistance accessible to everyone.

---

