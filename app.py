import streamlit as st
import os
from PyPDF2 import PdfReader, PdfWriter
import hashlib

# ---------------- Helper Functions ----------------

def hash_page_binary(page):
    """
    Hash the full content of a page to detect duplicates.
    This works for text, tables, and images as it hashes the raw PDF page content.
    """
    return hashlib.md5(page.get_object().get_data()).hexdigest()

def merge_pdfs_remove_duplicate_pages(pdf_paths, output_pdf_path):
    writer = PdfWriter()
    seen_hashes = set()
    total_pages = 0
    kept_pages = 0

    for pdf_path in pdf_paths:
        reader = PdfReader(pdf_path)

        for page in reader.pages:
            total_pages += 1
            # Use raw PDF object bytes to detect duplicates
            try:
                page_hash = hashlib.md5(page.get_object().get_data()).hexdigest()
            except:
                # fallback if get_data fails
                page_hash = hashlib.md5(str(page).encode('utf-8')).hexdigest()

            if page_hash not in seen_hashes:
                writer.add_page(page)
                seen_hashes.add(page_hash)
                kept_pages += 1

    with open(output_pdf_path, "wb") as f:
        writer.write(f)

    return total_pages, kept_pages

# ---------------- Streamlit UI ----------------

st.set_page_config(page_title="PDF Deduplicator", layout="centered")

st.title("📄 PDF Deduplicator & Combiner")
st.write("Combine PDFs and remove duplicate pages (text, tables, images). Fully offline & confidential.")

uploaded_files = st.file_uploader(
    "Upload 2 or more PDFs",
    type="pdf",
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

    if st.button("🚀 Merge & Remove Duplicates"):
        with st.spinner("Processing PDFs..."):
            output_path = os.path.join("output", "final_dedup.pdf")
            total, kept = merge_pdfs_remove_duplicate_pages(pdf_paths, output_path)

        st.success("✅ PDFs processed successfully!")
        st.write(f"📄 Total pages uploaded: {total}")
        st.write(f"📄 Pages after deduplication: {kept}")

        with open(output_path, "rb") as f:
            st.download_button(
                "⬇ Download Final PDF",
                f,
                file_name="final_dedup.pdf",
                mime="application/pdf"
            )
else:
    st.info("Please upload at least 2 PDFs to combine.")e.extract_text() or ""
    return hash(text.strip())

def get_image_hash(page_image):
    return imagehash.phash(page_image)

def dedup_merge(pdf_paths, output_pdf_path):
    writer = PdfWriter()
    seen_hashes = set()

    for pdf_path in pdf_paths:
        reader = PdfReader(pdf_path)

        # convert pages to images
        images = convert_from_path(pdf_path, dpi=150)

        for idx, page in enumerate(reader.pages):
            text_hash = get_text_hash(page)
            img_hash = get_image_hash(images[idx])

            combined = (text_hash, str(img_hash))

            if combined not in seen_hashes:
                seen_hashes.add(combined)
                writer.add_page(page)

    with open(output_pdf_path, "wb") as f:
        writer.write(f)

    return len(seen_hashes)

# ---------------- Streamlit App ----------------

st.title("PDF Deduplicator & Combiner")
st.write("Upload PDFs and remove duplicate text, tables, and images.")

uploaded_files = st.file_uploader(
    "Upload PDFs (≥ 2)", type="pdf", accept_multiple_files=True
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

    if st.button("🔁 Merge & Remove Duplicates"):
        with st.spinner("Processing..."):
            output_path = os.path.join("output", "final_dedup.pdf")
            count = dedup_merge(pdf_paths, output_path)

        st.success("✅ Done!")
        st.write(f"📄 Pages after deduplication: {count}")

        with open(output_path, "rb") as f:
            st.download_button(
                "⬇ Download Result PDF",
                f,
                file_name="final_dedup.pdf",
                mime="application/pdf"
            )
else:
    st.info("Please upload *at least 2 PDFs*!")
