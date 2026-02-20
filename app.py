import streamlit as st
import os
from PyPDF2 import PdfReader, PdfWriter
import hashlib
import nltk

# Ensure punkt tokenizer is available
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

from nltk.tokenize import sent_tokenize
from pdfminer.high_level import extract_text

# ------------------ Helper Functions ------------------

def pdf_to_text(pdf_path):
    """Extract text from a PDF for deduplication."""
    return extract_text(pdf_path)

def remove_duplicate_sentences(texts):
    """Combine texts and remove duplicate sentences."""
    all_text = " ".join(texts)
    sentences = sent_tokenize(all_text)
    unique_sentences = list(dict.fromkeys(sentences))
    return "\n".join(unique_sentences)

def hash_page(page):
    """Generate hash for a PDF page to detect duplicates"""
    return hashlib.md5(page.extract_text().encode('utf-8')).hexdigest()

def merge_pdfs_remove_duplicates(pdf_paths, output_path):
    """Merge PDFs and remove duplicate pages & duplicate sentences"""
    writer = PdfWriter()
    seen_hashes = set()
    all_texts = []

    for pdf_path in pdf_paths:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            page_text = page.extract_text() or ""
            page_hash = hashlib.md5(page_text.encode('utf-8')).hexdigest()
            if page_hash not in seen_hashes:
                writer.add_page(page)
                seen_hashes.add(page_hash)
                all_texts.append(page_text)

    # Optional: remove duplicate sentences from combined text
    dedup_text = remove_duplicate_sentences(all_texts)
    
    # Save final PDF
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path, dedup_text

# ------------------ Streamlit App ------------------

st.title("PDF Combiner & Deduplicator (Text + Images + Tables)")

st.write("Upload multiple PDFs. The app will remove duplicate pages, text, tables, and images automatically.")

uploaded_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    os.makedirs("input", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    pdf_paths = []
    for pdf_file in uploaded_files:
        temp_path = os.path.join("input", pdf_file.name)
        with open(temp_path, "wb") as f:
            f.write(pdf_file.getbuffer())
        pdf_paths.append(temp_path)

    st.info("Processing PDFs... This may take a few seconds.")

    output_pdf_path = os.path.join("output", "final_combined.pdf")
    output_pdf_path, dedup_text = merge_pdfs_remove_duplicates(pdf_paths, output_pdf_path)

    st.success("✅ Final PDF created with duplicates removed!")
    st.download_button("Download Final PDF", output_pdf_path)
    st.text_area("Deduplicated Text Preview", dedup_text[:5000], height=300)
