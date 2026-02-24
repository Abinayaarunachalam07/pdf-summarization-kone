import streamlit as st
import fitz  # PyMuPDF
import os
import hashlib
import nltk
from nltk.tokenize import sent_tokenize
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PIL import Image
import io

nltk.download("punkt")

# ---------------- SETUP ----------------
os.makedirs("input", exist_ok=True)
os.makedirs("output", exist_ok=True)

# ---------------- HELPERS ----------------

def normalize_sentence(s):
    return " ".join(s.lower().split())

def extract_text_sentences(pdf_path):
    doc = fitz.open(pdf_path)
    sentences = []
    for page in doc:
        text = page.get_text()
        sentences.extend(sent_tokenize(text))
    return sentences

def extract_images(pdf_path):
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
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    y = height - 40

    c.setFont("Helvetica", 10)

    for line in text_lines:
        if y < 50:
            c.showPage()
            y = height - 40
            c.setFont("Helvetica", 10)
        c.drawString(40, y, line[:110])
        y -= 14

    for img_bytes in images:
        img = Image.open(io.BytesIO(img_bytes))
        img_path = "temp_img.png"
        img.save(img_path)
        c.showPage()
        c.drawImage(img_path, 50, 200, width=400, preserveAspectRatio=True)
        os.remove(img_path)

    c.save()

# ---------------- STREAMLIT UI ----------------

st.title("PDF Deduplicator (Text + Image)")
st.write("Fully offline | Confidential | Manager-ready")

uploaded_files = st.file_uploader(
    "Upload 2 or more PDFs",
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

    # ---- TEXT DEDUP ----
    seen_text = set()
    final_text = []
    for s in all_sentences:
        key = normalize_sentence(s)
        if key not in seen_text:
            seen_text.add(key)
            final_text.append(s)

    # ---- IMAGE DEDUP ----
    seen_images = set()
    final_images = []
    for img in all_images:
        h = image_hash(img)
        if h not in seen_images:
            seen_images.add(h)
            final_images.append(img)

    output_pdf = "output/final_deduplicated.pdf"
    create_clean_pdf(final_text, final_images, output_pdf)

    st.success("Duplicate text & images removed successfully!")
    st.download_button("Download Final PDF", output_pdf)
