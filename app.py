import streamlit as st
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from docx import Document
from PIL import Image as PILImage
import tempfile, base64

st.set_page_config(page_title="Resume Builder", layout="wide")

st.title("📄 Resume Builder with Templates")

with st.sidebar:
    st.header("Profile")
    name = st.text_input("Full Name", "Jane Doe")
    title = st.text_input("Job Title", "Software Engineer")
    email = st.text_input("Email", "jane@example.com")
    phone = st.text_input("Phone", "+1-234-567-890")
    linkedin = st.text_input("LinkedIn", "https://linkedin.com/in/janedoe")
    github = st.text_input("GitHub", "https://github.com/janedoe")
    photo = st.file_uploader("Upload Profile Photo", type=["png","jpg","jpeg"])

    st.header("Resume Content")
    summary = st.text_area("Professional Summary", "Results-driven engineer with proven experience...")
    education = st.text_area("Education", "B.Sc. Computer Science — XYZ University (2018-2022)")
    experience = st.text_area("Experience", "Software Engineer — ACME Inc. (2022-Present)")
    projects = st.text_area("Projects & Outside Experience", "- Project A\n- Project B")
    activities = st.text_area("Activities & Leadership", "- Member of ABC Club")
    skills = st.text_area("Skills & Interests", "Python, SQL, React, Leadership")
    certifications = st.text_area("Certifications", "AWS Certified Developer")
    languages = st.text_area("Languages", "English, Spanish")

    layout = st.radio("Choose Layout", ["Single Column", "Two Column"], index=0)
    generate = st.button("Generate Resume")

# --- PDF Generation ---
def create_pdf(data, photo_file, layout):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=50, rightMargin=50, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    normal = ParagraphStyle('normal', parent=styles['Normal'], fontSize=10, leading=12)
    heading = ParagraphStyle('heading', parent=styles['Heading2'], fontSize=12, leading=14, spaceAfter=6, textColor=colors.black)

    story = []

    # Header with photo
    if photo_file:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        PILImage.open(photo_file).save(tmp.name)
        im = Image(tmp.name, width=1.0*inch, height=1.0*inch)
        header_table = Table([[im, Paragraph(f"<b>{data['name']}</b><br/>{data['title']}<br/>{data['email']} | {data['phone']}<br/>{data['linkedin']} | {data['github']}", normal)]], colWidths=[1.2*inch, 5*inch])
        header_table.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP")]))
        story.append(header_table)
    else:
        story.append(Paragraph(f"<b>{data['name']}</b><br/>{data['title']}<br/>{data['email']} | {data['phone']}<br/>{data['linkedin']} | {data['github']}", normal))
    story.append(Spacer(1,12))

    def section(title, content):
        story.append(Paragraph(title, heading))
        story.append(Paragraph(content.replace("\n","<br/>"), normal))
        story.append(Spacer(1,8))

    if layout == "Single Column":
        section("Education", data['education'])
        section("Professional Experience", data['experience'])
        section("Projects & Outside Experience", data['projects'])
        section("Activities & Leadership", data['activities'])
        section("Skills & Interests", data['skills'])
        section("Certifications", data['certifications'])
        section("Languages", data['languages'])
    else:
        # Two column look with table
        left = []
        right = []
        left.append(Paragraph("Summary", heading))
        left.append(Paragraph(data['summary'], normal))
        left.append(Spacer(1,6))
        left.append(Paragraph("Skills & Interests", heading))
        left.append(Paragraph(data['skills'], normal))
        left.append(Spacer(1,6))
        left.append(Paragraph("Certifications", heading))
        left.append(Paragraph(data['certifications'], normal))
        left.append(Spacer(1,6))
        left.append(Paragraph("Languages", heading))
        left.append(Paragraph(data['languages'], normal))

        right.append(Paragraph("Education", heading))
        right.append(Paragraph(data['education'], normal))
        right.append(Spacer(1,6))
        right.append(Paragraph("Experience", heading))
        right.append(Paragraph(data['experience'], normal))
        right.append(Spacer(1,6))
        right.append(Paragraph("Projects", heading))
        right.append(Paragraph(data['projects'], normal))
        right.append(Spacer(1,6))
        right.append(Paragraph("Activities & Leadership", heading))
        right.append(Paragraph(data['activities'], normal))

        table = Table([[left, right]], colWidths=[2.5*inch, 3.5*inch])
        table.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP")]))
        story.append(table)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# --- DOCX Generation ---
def create_docx(data, photo_file):
    doc = Document()
    if photo_file:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        PILImage.open(photo_file).save(tmp.name)
        doc.add_picture(tmp.name, width=1.0*inch)
    doc.add_heading(data['name'], 0)
    doc.add_paragraph(data['title'])
    doc.add_paragraph(f"{data['email']} | {data['phone']}\n{data['linkedin']} | {data['github']}")

    def section(title, content):
        doc.add_heading(title, level=1)
        doc.add_paragraph(content)

    section("Summary", data['summary'])
    section("Education", data['education'])
    section("Experience", data['experience'])
    section("Projects & Outside Experience", data['projects'])
    section("Activities & Leadership", data['activities'])
    section("Skills & Interests", data['skills'])
    section("Certifications", data['certifications'])
    section("Languages", data['languages'])

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()

if generate:
    data = {
        "name": name,
        "title": title,
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "summary": summary,
        "education": education,
        "experience": experience,
        "projects": projects,
        "activities": activities,
        "skills": skills,
        "certifications": certifications,
        "languages": languages
    }
    pdf_bytes = create_pdf(data, photo, layout)
    docx_bytes = create_docx(data, photo)

    st.download_button("📥 Download PDF", data=pdf_bytes, file_name="resume.pdf", mime="application/pdf")
    st.download_button("📥 Download DOCX", data=docx_bytes, file_name="resume.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    st.success("Resume generated successfully!")