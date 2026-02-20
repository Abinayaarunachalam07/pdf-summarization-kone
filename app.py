import streamlit as st
import os
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
from PIL import Image
import imagehash
import tempfile

# ---------------- Helper Functions ----------------

def get_text_hash(page):
    text = page.extract_text() or ""
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
