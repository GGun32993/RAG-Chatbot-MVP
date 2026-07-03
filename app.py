import os
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Load environment variables
load_dotenv()

# Project Paths
CHROMA_DB_DIR = "chroma_db"
DOCUMENTS_DIR = "documents"

# Streamlit Page Config
st.set_page_config(
    page_title="HR Intelligent RAG Chatbot",
    page_icon="🏢",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom Premium CSS Styling
st.markdown("""
<style>
    /* Main Layout */
    .stApp {
        background-color: var(--background-color);
    }
    
    /* Custom Header card */
    .header-card {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 2.2rem 1.8rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.3);
    }
    .header-card h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.025em;
        color: #FFFFFF !important;
    }
    .header-card p {
        margin-top: 0.75rem;
        margin-bottom: 0;
        font-size: 1.1rem;
        color: rgba(255, 255, 255, 0.9) !important;
        font-weight: 300;
    }

    /* Citation badge style */
    .citation-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 10px;
        margin-bottom: 15px;
    }
    .citation-badge {
        background: var(--secondary-background-color);
        border: 1px solid rgba(59, 130, 246, 0.3);
        color: var(--text-color) !important;
        border-radius: 8px;
        padding: 6px 14px;
        font-size: 0.85rem;
        font-weight: 500;
        display: inline-flex;
        align-items: center;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
    }
    .citation-badge:hover {
        background: rgba(59, 130, 246, 0.1);
        border-color: #3B82F6;
        transform: translateY(-1px);
    }

    /* Status cards */
    .status-card {
        background-color: var(--secondary-background-color);
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(226, 232, 240, 0.2);
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }

    /* Input box alignment */
    .stChatInput {
        border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

# Custom Header
st.markdown("""
<div class="header-card">
    <h1>🏢 HR Intelligent Chatbot</h1>
    <p>ค้นหาและถาม-ตอบข้อมูลกฎการลา เบอร์ภายใน และสวัสดิการของพนักงาน</p>
</div>
""", unsafe_allow_html=True)

# Check API Key
if not os.getenv("GEMINI_API_KEY"):
    st.error("🔑 ไม่พบ `GEMINI_API_KEY` ในไฟล์ `.env` กรุณาตั้งค่า API Key เพื่อเปิดใช้งานระบบแชทบอท")
    st.info("💡 วิธีแก้ไข: สร้างไฟล์ `.env` ในโฟลเดอร์โครงการ จากนั้นเพิ่มคีย์ `GEMINI_API_KEY=your_actual_key`")
    st.stop()

# Cache Vector Database Connection
@st.cache_resource
def load_vector_db():
    if not os.path.exists(CHROMA_DB_DIR) or not os.listdir(CHROMA_DB_DIR):
        return None
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        db = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embeddings)
        return db
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดฐานข้อมูลเวกเตอร์: {e}")
        return None

# Load DB
db = load_vector_db()

# Check if Database exists
if db is None:
    st.markdown(f"""
    <div class="status-card" style="border-left: 5px solid #F59E0B;">
        <h4 style="color: #D97706; margin-top: 0;">⚠️ ไม่พบข้อมูลเอกสารในระบบ (Vector Database is empty)</h4>
        <p style="margin-bottom: 10px; color: #4B5563;">กรุณาดำเนินการตามขั้นตอนดังต่อไปนี้เพื่อนำเข้าเอกสารตั้งต้น:</p>
        <ol style="margin-bottom: 0; color: #4B5563; padding-left: 20px;">
            <li>สร้างไฟล์เอกสารตัวอย่างโดยรันคำสั่ง: <br><code>python generate_docs.py</code></li>
            <li>นำข้อมูลเข้าสู่ระบบเวกเตอร์โดยรันคำสั่ง: <br><code>python ingest.py</code></li>
            <li>กดรีเฟรชหน้าเว็บนี้อีกครั้ง</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Initialize Chat History in Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Conversation History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # If there are sources in the message, render them nicely
        if "sources" in message and message["sources"]:
            st.markdown('<p style="margin-top: 10px; font-size: 0.9rem; font-weight: 600; color: #475569;">📄 อ้างอิงจากเอกสาร:</p>', unsafe_allow_html=True)
            citation_html = '<div class="citation-container">'
            for source, page in message["sources"]:
                citation_html += f'<span class="citation-badge">📌 {source} (หน้า {page})</span>'
            citation_html += '</div>'
            st.markdown(citation_html, unsafe_allow_html=True)

# Chat Input
if question := st.chat_input("พิมพ์คำถามของท่านที่นี่... (เช่น ลาพักร้อนได้กี่วันต่อปี, เบอร์โทร IT)"):
    
    # 1. Show user question in the UI
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})
    
    # 2. Retrieve relevant chunks from ChromaDB
    # Retrieve top 4 most relevant chunks
    retriever = db.as_retriever(search_kwargs={"k": 4})
    relevant_docs = retriever.invoke(question)
    
    # Extract page content and metadata
    context_parts = []
    sources = []
    
    for idx, doc in enumerate(relevant_docs):
        context_parts.append(doc.page_content)
        src = doc.metadata.get("source", "เอกสารทั่วไป")
        pg = doc.metadata.get("page", 1)
        sources.append((src, pg))
        
    context_text = "\n\n---\n\n".join(context_parts)
    
    # Remove duplicate sources to display clean citations
    unique_sources = sorted(list(set(sources)))
    
    # 3. Create Gemini LLM Chain
    # We use gemini-1.5-flash for fast and accurate chat response
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0)
    
    system_prompt = (
        "คุณคือผู้ช่วย AI ฝ่ายทรัพยากรบุคคล (HR Assistant) ที่มีความสุภาพและเป็นมิตร "
        "หน้าที่ของคุณคือการตอบคำถามของพนักงานเกี่ยวกับกฎการลาพักร้อน เบอร์ติดต่อภายใน และนโยบายบริษัท "
        "โดยอิงตาม 'บริบท (Context)' ที่แนบมาให้เท่านั้น ห้ามเดาคำตอบ หรือใช้ข้อมูลความรู้ทั่วไปภายนอกนอกจากในบริบทนี้เด็ดขาด\n\n"
        "กฎที่ต้องปฏิบัติอย่างเคร่งครัด:\n"
        "1. ตอบคำถามด้วยความซื่อสัตย์ตามข้อมูลที่ปรากฏใน Context เท่านั้น\n"
        "2. หากข้อมูลใน Context ไม่ระบุเรื่องที่ถาม หรือไม่สามารถหาคำตอบได้ ให้ตอบตรงๆ ว่า "
        "'ไม่พบข้อมูลดังกล่าวในเอกสารนโยบายบริษัทค่ะ/ครับ แนะนำให้ติดต่อฝ่าย HR โดยตรงได้ที่เบอร์ภายใน 1201 หรืออีเมล hr@company.com เพื่อสอบถามข้อมูลเพิ่มเติมค่ะ/ครับ'\n"
        "3. การอ้างอิงเอกสาร ไม่ต้องใส่ชื่อไฟล์หรือเลขหน้าลงในข้อความตอบคำถาม (เพราะระบบจะแสดงป้ายอ้างอิงให้อัตโนมัติอยู่แล้ว)\n"
        "4. ตอบเป็นภาษาไทยด้วยน้ำเสียงที่สุภาพ เป็นมิตร ลงท้ายด้วย ค่ะ/ครับ เสมอ\n\n"
        "บริบท (Context):\n"
        "{context}"
    )
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}")
    ])
    
    # Format Chat History for LangChain
    chat_history = []
    for msg in st.session_state.messages[:-1]:
        if msg["role"] == "user":
            chat_history.append(HumanMessage(content=msg["content"]))
        else:
            chat_history.append(AIMessage(content=msg["content"]))
            
    chain = prompt_template | llm
    
    # 4. Generate answer from Gemini
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        with st.spinner("กำลังค้นหาข้อมูลและสรุปคำตอบ..."):
            response = chain.invoke({
                "context": context_text,
                "chat_history": chat_history,
                "question": question
            })
            answer = response.content
            response_placeholder.markdown(answer)
            
            # If search returned results, show citation badges below the answer
            if relevant_docs:
                st.markdown('<p style="margin-top: 10px; font-size: 0.9rem; font-weight: 600; color: #475569;">📄 อ้างอิงจากเอกสาร:</p>', unsafe_allow_html=True)
                citation_html = '<div class="citation-container">'
                for source, page in unique_sources:
                    citation_html += f'<span class="citation-badge">📌 {source} (หน้า {page})</span>'
                citation_html += '</div>'
                st.markdown(citation_html, unsafe_allow_html=True)
                
    # Save assistant response to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": unique_sources
    })
