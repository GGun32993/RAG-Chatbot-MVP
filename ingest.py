import os
import glob
import pdfplumber
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

# Load environment variables from .env file
load_dotenv()

# Verify API key
if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in your .env file.")

# Define paths
DOCUMENTS_DIR = "documents"
CHROMA_DB_DIR = "chroma_db"

def load_and_split_pdf(pdf_path):
    """
    Read PDF page by page using pdfplumber, extract text, 
    and split text into chunks of 300-500 words (approx. 1000-1500 characters in Thai).
    Retains page number (1-based) and filename metadata.
    """
    filename = os.path.basename(pdf_path)
    documents = []
    
    # 300-500 words is approximately 1000-1500 characters in Thai.
    # We use RecursiveCharacterTextSplitter for clean chunking within the page bounds.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200, 
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    
    print(f"Reading: {filename}...")
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_number = i + 1
            text = page.extract_text()
            if not text or not text.strip():
                continue
            
            # Split the page text
            chunks = text_splitter.split_text(text)
            
            for chunk in chunks:
                doc = Document(
                    page_content=chunk.strip(),
                    metadata={
                        "source": filename,
                        "page": page_number
                    }
                )
                documents.append(doc)
                
    print(f"-> Extracted {len(documents)} chunks from {filename}")
    return documents

def main():
    # 1. Scan for PDFs
    pdf_files = glob.glob(os.path.join(DOCUMENTS_DIR, "*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in '{DOCUMENTS_DIR}' directory. Please run generate_docs.py first.")
        return
        
    all_chunks = []
    for pdf_file in pdf_files:
        chunks = load_and_split_pdf(pdf_file)
        all_chunks.extend(chunks)
        
    if not all_chunks:
        print("No content could be extracted from PDFs.")
        return
        
    print(f"\nTotal chunks to ingest: {len(all_chunks)}")
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    # 3. Save to ChromaDB (local persistent)
    print("Saving to local ChromaDB...")
    db = Chroma.from_documents(
        documents=all_chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_DIR
    )
    
    print(f"Success! Vector database successfully created at '{CHROMA_DB_DIR}'")

if __name__ == "__main__":
    main()
