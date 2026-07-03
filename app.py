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
    
    /* Custom Header card with Glassmorphism & Gradient Border */
    .header-card {
        background: 
            linear-gradient(135deg, rgba(15, 23, 42, 0.75) 0%, rgba(30, 41, 59, 0.75) 100%) padding-box,
            linear-gradient(135deg, rgba(99, 102, 241, 0.35), rgba(168, 85, 247, 0.35)) border-box;
        border: 1px solid transparent;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 2.2rem 2rem 1.8rem 2rem;
        border-radius: 24px;
        margin-bottom: 1.5rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 45px -10px rgba(99, 102, 241, 0.18), 0 0 25px -5px rgba(168, 85, 247, 0.12);
    }
    
    /* Decorative glowing orb behind the header */
    .header-card::before {
        content: "";
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, transparent 60%);
        pointer-events: none;
        z-index: 1;
    }
    
    /* Badge styling with pulse animation */
    @keyframes pulse-glow {
        0%, 100% {
            transform: scale(1);
            opacity: 0.9;
            filter: drop-shadow(0 0 2px rgba(168, 85, 247, 0.4));
        }
        50% {
            transform: scale(1.1);
            opacity: 1;
            filter: drop-shadow(0 0 8px rgba(168, 85, 247, 0.8));
        }
    }
    
    .header-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: linear-gradient(90deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%);
        border: 1px solid rgba(168, 85, 247, 0.35);
        color: #c7d2fe !important;
        padding: 6px 14px;
        border-radius: 30px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 1.2rem;
        position: relative;
        z-index: 2;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);
    }
    
    .header-badge .animated-spark {
        display: inline-block;
        animation: pulse-glow 2s infinite ease-in-out;
    }
    
    /* Title layout & typography */
    .header-title-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 12px;
        margin-bottom: 0.6rem;
        position: relative;
        z-index: 2;
    }
    
    .header-icon {
        width: 36px;
        height: 36px;
        display: inline-block;
        filter: drop-shadow(0 0 8px rgba(99, 102, 241, 0.5));
    }
    
    .header-card h1 {
        margin: 0;
        font-size: 2.3rem;
        font-weight: 850;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #ffffff 40%, #c7d2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .header-card p {
        margin-top: 0.4rem;
        margin-bottom: 1.2rem;
        font-size: 1rem;
        color: #94a3b8 !important;
        font-weight: 400;
        line-height: 1.5;
        position: relative;
        z-index: 2;
        max-width: 520px;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Trust Indicators */
    .trust-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 12px;
        margin-top: 1.2rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        flex-wrap: wrap;
        position: relative;
        z-index: 2;
    }
    .trust-item {
        font-size: 0.78rem;
        color: #64748b !important;
        font-weight: 500;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }
    .trust-icon {
        font-size: 0.85rem;
    }
    .trust-divider {
        color: rgba(255, 255, 255, 0.15);
        font-size: 0.8rem;
    }

    /* Style secondary buttons to look like suggestion chips */
    button[data-testid*="baseButton-secondary"] {
        background-color: rgba(99, 102, 241, 0.08) !important;
        border: 1px solid rgba(99, 102, 241, 0.25) !important;
        color: #c7d2fe !important;
        border-radius: 50px !important;
        padding: 0.4rem 1.2rem !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        width: 100% !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }

    button[data-testid*="baseButton-secondary"]:hover {
        background-color: rgba(99, 102, 241, 0.22) !important;
        border-color: rgba(168, 85, 247, 0.6) !important;
        color: #ffffff !important;
        box-shadow: 0 0 15px rgba(139, 92, 246, 0.4) !important;
        transform: translateY(-2px) !important;
    }

    button[data-testid*="baseButton-secondary"]:active {
        transform: translateY(0px) !important;
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

    /* Input box alignment & premium styling */
    div[data-testid="stChatInput"] {
        border-radius: 16px !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
        background-color: rgba(15, 23, 42, 0.4) !important;
        box-shadow: 0 4px 20px -5px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    /* Glow when focused */
    div[data-testid="stChatInput"]:focus-within {
        border-color: rgba(139, 92, 246, 0.5) !important;
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.25), 0 4px 20px -5px rgba(0, 0, 0, 0.5) !important;
        background-color: rgba(15, 23, 42, 0.65) !important;
    }

    /* Submit button inside chat input */
    div[data-testid="stChatInput"] button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
        border: none !important;
        border-radius: 10px !important;
        color: white !important;
        transition: all 0.2s ease !important;
    }
    
    div[data-testid="stChatInput"] button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 0 10px rgba(139, 92, 246, 0.6) !important;
    }
</style>
""", unsafe_allow_html=True)


# Custom Header
st.markdown("""
<div class="header-card">
    <div class="header-badge">
        <span class="animated-spark">✨</span> AI-Powered Workspace
    </div>
    <div class="header-title-container">
        <svg class="header-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="icon-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#6366f1" />
                    <stop offset="100%" stop-color="#a855f7" />
                </linearGradient>
            </defs>
            <path d="M12 2C6.477 2 2 6.477 2 12c0 1.886.525 3.647 1.44 5.16L2.05 21.95a1 1 0 001.21 1.21l4.79-1.39A9.96 9.96 0 0012 22c5.523 0 10-4.477 10-10S17.523 2 12 2z" fill="url(#icon-grad)" />
            <circle cx="8" cy="12" r="1.2" fill="#ffffff" />
            <circle cx="12" cy="12" r="1.2" fill="#ffffff" />
            <circle cx="16" cy="12" r="1.2" fill="#ffffff" />
            <path d="M19 3l.7 1.8 1.8.7-1.8.7-.7 1.8-.7-1.8-1.8-.7 1.8-.7L19 3z" fill="#ffffff" />
        </svg>
        <h1>HR Intelligent Chatbot</h1>
    </div>
    <p>ค้นหาและถาม-ตอบข้อมูลกฎการลา เบอร์ภายใน และสวัสดิการของพนักงานด้วย AI อัจฉริยะ</p>
    
    <div class="trust-container">
        <span class="trust-item"><span class="trust-icon">📄</span> ครอบคลุม 3 เอกสารนโยบายหลัก</span>
        <span class="trust-divider">•</span>
        <span class="trust-item"><span class="trust-icon">⚡</span> ตอบใน &lt; 3 วินาที</span>
        <span class="trust-divider">•</span>
        <span class="trust-item"><span class="trust-icon">🔒</span> ข้อมูลบริษัทปลอดภัย 100%</span>
    </div>
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

# Detect queries at the top of the chat area
query_to_process = None
if "clicked_suggestion" in st.session_state:
    query_to_process = st.session_state.clicked_suggestion
    del st.session_state.clicked_suggestion

chat_input_val = st.chat_input("พิมพ์คำถามของท่านที่นี่... (เช่น ลาพักร้อนได้กี่วันต่อปี, เบอร์โทร IT)")
if chat_input_val:
    query_to_process = chat_input_val

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

# Show suggestions only on the welcome screen
if len(st.session_state.messages) == 0 and not query_to_process:
    st.markdown('<p style="text-align: center; font-size: 0.85rem; color: #64748b; font-weight: 600; margin-top: 0.8rem; margin-bottom: 0.8rem; letter-spacing: 0.05em; text-transform: uppercase;">💡 แนะนำหัวข้อเริ่มต้นถาม:</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📅 ลาพักร้อนได้กี่วันต่อปี", use_container_width=True):
            st.session_state.clicked_suggestion = "ลาพักร้อนได้กี่วันต่อปี"
            st.rerun()
    with col2:
        if st.button("💻 เบอร์ติดต่อ IT", use_container_width=True):
            st.session_state.clicked_suggestion = "เบอร์ติดต่อ IT"
            st.rerun()
    with col3:
        if st.button("🏥 นโยบายการลาป่วย", use_container_width=True):
            st.session_state.clicked_suggestion = "ลาป่วยต้องแจ้งล่วงหน้ากี่วัน/แจ้งอย่างไร"
            st.rerun()

# Run query processing
if query_to_process:
    # 1. Show user question in the UI
    with st.chat_message("user"):
        st.markdown(query_to_process)
    st.session_state.messages.append({"role": "user", "content": query_to_process})
    
    # 2. Retrieve relevant chunks from ChromaDB
    retriever = db.as_retriever(search_kwargs={"k": 4})
    relevant_docs = retriever.invoke(query_to_process)
    
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
                "question": query_to_process
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
    st.rerun()
