import streamlit as st
import fitz  # PyMuPDF
import os
import hashlib
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PIL import Image
import io
import re

# ------------------- Folders -------------------
os.makedirs("input", exist_ok=True)
os.makedirs("output", exist_ok=True)

# ------------------- Helpers -------------------

def simple_sent_tokenize(text):
    """Split text into sentences without NLTK"""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def normalize_sentence(s):
    return " ".join(s.lower().split())

def extract_text_sentences(pdf_path):
    """Extract text from PDF using PyMuPDF and split into sentences"""
    doc = fitz.open(pdf_path)
    sentences = []
    for page in doc:
        text = page.get_text()
        sentences.extend(simple_sent_tokenize(text))
    return sentences

def extract_images(pdf_path):
    """Extract images from PDF as byte arrays"""
    doc = fitz.open(pdf_path)
    images = []
    for page in doc:
        for img in page.get_images(full=True):
            xref = img[0]
            base = doc.extract_image(xref)
            images.append(base["image"])
    return images

def image_hash(img_bytes):
    return hashlib.md5(img_bytes).hexdigest()

def create_clean_pdf(text_lines, images, output_path):
    """Create PDF with deduplicated text and images"""
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    y = height - 40

    c.setFont("Helvetica", 10)

    # Write text
    for line in text_lines:
        if y < 50:
            c.showPage()
            y = height - 40
            c.setFont("Helvetica", 10)
        c.drawString(40, y, line[:110])
        y -= 14

    # Write images
    for img_bytes in images:
        img = Image.open(io.BytesIO(img_bytes))
        img_path = "temp_img.png"
        img.save(img_path)
        c.showPage()
        c.drawImage(img_path, 50, 200, width=400, preserveAspectRatio=True)
        os.remove(img_path)

    c.save()

# ------------------- Streamlit App -------------------

st.title("PDF Deduplicator & Merger (Text + Images)")
st.write("Upload 2 or more PDFs. Duplicates (text & images) will be removed.")

uploaded_files = st.file_uploader(
    "Upload PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    all_sentences = []
    all_images = []

    for file in uploaded_files:
        path = f"input/{file.name}"
        with open(path, "wb") as f:
            f.write(file.getbuffer())

        all_sentences.extend(extract_text_sentences(path))
        all_images.extend(extract_images(path))

    # ---- Deduplicate text ----
    seen_text = set()
    final_text = []
    for s in all_sentences:
        key = normalize_sentence(s)
        if key not in seen_text:
            seen_text.add(key)
            final_text.append(s)

    # ---- Deduplicate images ----
    seen_images = set()
    final_images = []
    for img in all_images:
        h = image_hash(img)
        if h not in seen_images:
            seen_images.add(h)
            final_images.append(img)

    output_pdf = "output/final_deduplicated.pdf"
    create_clean_pdf(final_text, final_images, output_pdf)

    st.success("Merged PDF created successfully!")
    st.download_button("Download Final PDF", output_pdf)
