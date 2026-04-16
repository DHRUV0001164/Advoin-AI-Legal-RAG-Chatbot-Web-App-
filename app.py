import os
import tempfile
import threading
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from fpdf import FPDF
from groq import Groq
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in the environment variables.")

client = Groq(api_key=GROQ_API_KEY)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

vectorstore = None
is_knowledge_loading = False
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

DATA_DIR = "knowledge_pdfs"
os.makedirs(DATA_DIR, exist_ok=True)

def init_knowledge_base_task():
    global vectorstore, is_knowledge_loading
    is_knowledge_loading = True
    docs = []
    print(f"Loading PDFs in background from {DATA_DIR}...")
    for filename in os.listdir(DATA_DIR):
        if filename.lower().endswith(".pdf"):
            try:
                print(f"Processing {filename}...")
                file_path = os.path.join(DATA_DIR, filename)
                loader = PyPDFLoader(file_path)
                pages = loader.load()
                docs.extend(text_splitter.split_documents(pages))
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    if docs:
        vectorstore = Chroma.from_documents(documents=docs, embedding=embeddings)
        print(f"Knowledge base initialized successfully with {len(docs)} document chunks!")
    else:
        print(f"No PDFs found in {DATA_DIR}. Running with baseline AI knowledge only.")
    is_knowledge_loading = False

@app.on_event("startup")
def startup_event():
    # Start PDF ingestion in background thread so the server opens instantly
    thread = threading.Thread(target=init_knowledge_base_task)
    thread.daemon = True
    thread.start()

SYSTEM_PROMPT = """
You are a legal awareness and guidance assistant exclusively for Indian Law.
Your job is to help people understand legal rights, legal obligations, and law-related situations within the jurisdiction of India only, in a calm, supportive, and human way.

You are not a lawyer and do not replace a licensed advocate.
You speak like a helpful, trustworthy human being, not like a robot, policy document, or legal textbook.
Your tone must be respectful, empathetic, clear, and practical.

LANGUAGE RULE:
Always reply in the same language used by the user.

STRICT DOMAIN RULE (VERY IMPORTANT):
1. You ONLY handle legal matters related to India (Indian Constitution, Bhartiya Nyaya Sanhita, IPC, CrPC, IT Act, etc).
2. If a user asks about laws from other countries or jurisdictions, you must politely refuse and state that you ONLY provide guidance for the jurisdiction of India.
3. If the user asks about anything outside law (like finance, general life, coding, medicine), you must politely refuse to answer and gently redirect them back to Indian legal topics.

WHAT YOU DO:
Explain legal rights and protections in simple, everyday language based heavily on the Context provided.
If the answer isn't in the provided context, use your knowledge of Indian Law but add a disclaimer that the specific detail was not in the local documents.
"""

FIR_SYSTEM_PROMPT = """
You are a licensed Indian police officer and legal expert.
Your strictly specific job is to draft a formal First Information Report (FIR) based on the user's incident description.
Draft a complete, official-looking FIR document, referencing the correct sections of the Bhartiya Nyaya Sanhita (BNS) or Indian Penal Code (IPC), IT Act, etc as applicable.
DO NOT use markdown formatting like asterisks or hashtags. Use purely plain text. Write everything sequentially without markdown lists if possible.
DO NOT chat or provide advice. Simply return ONLY the FIR text. Limit it to a single formal letter layout. English or Hindi depending on user language.
"""

class ChatRequest(BaseModel):
    message: str

class FIRRequest(BaseModel):
    incident_description: str

@app.post("/api/chat")
async def chat_with_bot(request: ChatRequest):
    global is_knowledge_loading
    if is_knowledge_loading:
        return {"response": "⏳ ***Status Update:*** I am currently analyzing and memorizing the thousands of pages from the Indian Legal PDFs you provided. It takes a few minutes for my systems to boot up. Please try asking your question again in a minute!"}

    query = request.message
    context = ""
    
    if vectorstore is not None:
        try:
            search_results = vectorstore.similarity_search(query, k=3)
            context = "\n".join([doc.page_content for doc in search_results])
        except Exception as e:
            print(f"Vector search error: {e}")
            context = "Error retrieving context from database."
    else:
        context = "No custom documents loaded. Use general knowledge."
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Context provided from documents:\n{context}\n\nQuestion: {query}"}
    ]
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.1
        )
        return {"response": response.choices[0].message.content.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Error: {str(e)}")

@app.post("/api/draft_fir")
async def draft_fir(request: FIRRequest):
    description = request.incident_description
    
    messages = [
        {"role": "system", "content": FIR_SYSTEM_PROMPT},
        {"role": "user", "content": f"Draft an FIR for the following incident:\n\n{description}"}
    ]
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.1
        )
        fir_text = response.choices[0].message.content.strip()
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        # Set auto page break
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Helvetica", size=12)
        
        # Write text handling line breaks
        for line in fir_text.split('\n'):
            clean_line = line.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 7, txt=clean_line)
            
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(temp_pdf.name)
        
        return FileResponse(
            temp_pdf.name, 
            media_type='application/pdf', 
            filename='FIR_Draft.pdf'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FIR Drafting Error: {str(e)}")

# Mount static frontend
os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
