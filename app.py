import streamlit as st
from PyPDF2 import PdfReader
from pdfminer.high_level import extract_text
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize
# ------------------- Helper Functions -------------------
def pdf_to_text(pdf_path):
    """Extract text from PDF"""
    return extract_text(pdf_path)
def extract_sections(text):
    """
    Simple section extraction based on patterns like '1.', '1.1', '2.', etc.
    Returns a dict {section_title: section_text}
    """
    lines = text.splitlines()
    sections = {}
    current_section = "Introduction"
    sections[current_section] = ""
    for line in lines:
        line_strip = line.strip()
        if line_strip:
            # detect section number e.g., 1., 1.1, 2.3 etc.
            if line_strip[:2].replace(".", "").isdigit() or (line_strip[:3].replace(".", "").isdigit()):
                current_section = line_strip
                if current_section not in sections:
                    sections[current_section] = ""
            else:
                sections[current_section] += line_strip + " "
    return sections

def deduplicate_sections(all_sections):
    """
    all_sections: list of dicts [{section_title: text}]
    Returns combined sections with duplicate sentences removed across PDFs
    """
    combined_sections = {}
    seen_sentences = set()

    for section_dict in all_sections:
        for sec_title, text in section_dict.items():
            sentences = sent_tokenize(text)
            filtered_sentences = []
            for s in sentences:
                s_clean = s.strip().lower()
                if s_clean not in seen_sentences:
                    seen_sentences.add(s_clean)
                    filtered_sentences.append(s)
            if sec_title in combined_sections:
                combined_sections[sec_title] += " ".join(filtered_sentences) + " "
            else:
                combined_sections[sec_title] = " ".join(filtered_sentences) + " "
    return combined_sections

def create_pdf_from_sections(sections_dict, output_path):
    """Generate PDF with sections"""
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    y = height - 40
    c.setFont("Helvetica-Bold", 12)
    
    for sec_title, text in sections_dict.items():
        # Section title
        c.drawString(40, y, sec_title)
        y -= 20
        c.setFont("Helvetica", 10)

        # Split text into lines
        lines = text.split(". ")
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if y < 40:
                c.showPage()
                y = height - 40
                c.setFont("Helvetica", 10)
            c.drawString(50, y, line[:120])
            y -= 15
        y -= 10  # space between sections
        c.setFont("Helvetica-Bold", 12)
    
    c.save()

# ------------------- Streamlit App -------------------

st.title("PDF Section-wise Deduplicator & Combiner")
st.write("Upload 2 or more PDFs. Duplicates will be removed section-wise.")

# Create folders if they don't exist
os.makedirs("input", exist_ok=True)
os.makedirs("output", exist_ok=True)

uploaded_files = st.file_uploader(
    "Upload PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    st.write("Processing PDFs...")
    all_sections_list = []

    for pdf_file in uploaded_files:
        temp_path = os.path.join("input", pdf_file.name)
        with open(temp_path, "wb") as f:
            f.write(pdf_file.getbuffer())

        text = pdf_to_text(temp_path)
        sections = extract_sections(text)
        all_sections_list.append(sections)

    combined_sections = deduplicate_sections(all_sections_list)
   output_file = os.path.join("output", "final_combined.pdf")
    create_pdf_from_sections(combined_sections, output_file)
    st.success("Final PDF created successfully!")
    st.download_button("Download Final PDF", output_file)
