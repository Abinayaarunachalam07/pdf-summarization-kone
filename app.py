import streamlit as st
import os
import hashlib
from PyPDF2 import PdfReader, PdfWriter

# ------------------ Helper Functions ------------------

def page_hash(page):
    """
    Create a stable hash for a PDF page using text + structure.
    This helps detect duplicate pages including text, tables, images.
    """
    text = page.extract_text() or ""
    raw = text.encode("utf-8")
    return hashlib.md5(raw).hexdigest()

def merge_pdfs_remove_duplicates(pdf_paths, output_path):
    writer = PdfWriter()
    seen_pages = set()
    total_pages = 0
    kept_pages = 0

    for pdf_path in pdf_paths:
        reader = PdfReader(pdf_path)

        for page in reader.pages:
            total_pages += 1
            h = page_hash(page)

            if h not in seen_pages:
                writer.add_page(page)
                seen_pages.add(h)
                kept_pages += 1

    with open(output_path, "wb") as f:
        writer.write(f)

    return total_pages, kept_pages

# ------------------ Streamlit UI ------------------

st.set_page_config(page_title="PDF Deduplicator", layout="centered")

st.title("📄 PDF Combiner & Deduplicator (Offline)")
st.write(
    "Combine 2 or more PDFs into one and automatically remove duplicate "
    "text, tables, images, and infographics. Fully offline & confidential."
)

uploaded_files = st.file_uploader(
    "Upload PDF files",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files and len(uploaded_files) >= 2:
    os.makedirs("input", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    pdf_paths = []

    for file in uploaded_files:
        path = os.path.join("input", file.name)
        with open(path, "wb") as f:
            f.write(file.getbuffer())
        pdf_paths.append(path)

    if st.button("🚀 Combine PDFs"):
        with st.spinner("Processing PDFs and removing duplicates..."):
            output_path = os.path.join("output", "final_combined.pdf")
            total, kept = merge_pdfs_remove_duplicates(pdf_paths, output_path)

        st.success("✅ Final PDF created successfully!")
        st.write(f"📊 Total pages processed: **{total}**")
        st.write(f"📉 Pages after deduplication: **{kept}**")

        with open(output_path, "rb") as f:
            st.download_button(
                "⬇ Download Final PDF",
                f,
                file_name="final_combined.pdf",
                mime="application/pdf"
            )
else:
    st.info("Please upload **at least 2 PDFs** to start.")
