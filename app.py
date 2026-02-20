import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from pdfminer.high_level import extract_text
import os
import nltk

nltk.download('punkt')
from nltk.tokenize import sent_tokenize

# ----------------- Helper Functions -----------------

def pdf_to_text(pdf_path):
    """Extract text from PDF"""
    text = extract_text(pdf_path)
    return text

def remove_duplicate_sentences(texts):
    """Combine multiple texts and remove duplicate sentences"""
    all_text = " ".join(texts)
    sentences = sent_tokenize(all_text)
    unique_sentences = list(dict.fromkeys(sentences))  # preserves order
    return "\n".join(unique_sentences)

def create_summary_pdf(text, output_path):
    """Create a PDF from text"""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    lines = text.split("\n")
    y = height - 40
    for line in lines:
        if y < 40:
            c.showPage()
            y = height - 40
        c.drawString(40, y, line[:150])  # Truncate line to fit width
        y -= 15
    c.save()

# ----------------- Streamlit App -----------------

st.title("PDF Deduplicator & Combiner")

st.write("Upload 2 or more PDFs to combine and remove duplicate sentences.")

uploaded_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    # Extract text from all PDFs
    st.write("Processing PDFs...")
    texts = []
    for pdf_file in uploaded_files:
        # Save temporary
        temp_path = os.path.join("input", pdf_file.name)
        with open(temp_path, "wb") as f:
            f.write(pdf_file.getbuffer())
        text = pdf_to_text(temp_path)
        texts.append(text)

    # Remove duplicate sentences
    final_text = remove_duplicate_sentences(texts)

    # Save final PDF
    output_path = os.path.join("output", "final_summary.pdf")
    os.makedirs("output", exist_ok=True)
    create_summary_pdf(final_text, output_path)

    st.success("Final PDF created!")
    st.download_button("Download Final PDF", output_path)
