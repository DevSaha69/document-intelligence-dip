import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

def generate_docx(filename="Report.docx", student_name="[Student Name]", roll_no="[Roll Number]"):
    doc = docx.Document()
    
    # Page setup: Standard margins (0.75 in)
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
        
    NAVY = RGBColor(26, 54, 93)
    TEAL = RGBColor(49, 151, 149)
    DARK = RGBColor(30, 41, 59)
    
    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = p_title.add_run("Document Intelligence for Application Readiness & Missing-Requirement Detection\n")
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(18)
    run_title.font.bold = True
    run_title.font.color.rgb = NAVY
    
    # Author details
    p_auth = doc.add_paragraph()
    p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_auth = p_auth.add_run(f"Author: {student_name} | Roll Number: {roll_no}\nDepartment of Computer Science & Engineering | Digital Image Processing (AIML-042)\n")
    run_auth.font.name = "Calibri"
    run_auth.font.size = Pt(10.5)
    run_auth.font.italic = True
    
    # Abstract
    p_abs = doc.add_paragraph()
    r_abs_lbl = p_abs.add_run("Abstract— ")
    r_abs_lbl.bold = True
    r_abs_lbl.font.color.rgb = NAVY
    r_abs_body = p_abs.add_run(
        "In higher education and study-abroad admissions workflows, administrative staff must review thousands of "
        "photographed or scanned application dossiers. Applicants frequently submit documents suffering from severe real-world capture "
        "degradations—such as non-uniform shadow gradients, sensor noise, optical blur, low contrast, and affine rotational skew—which "
        "cause optical character recognition (OCR) engines to fail. This paper presents an end-to-end document intelligence pipeline "
        "combining classical Digital Image Processing (DIP) techniques with OCR and rule-based verification to automatically detect missing "
        "application requirements. The proposed pipeline employs mathematical morphological background estimation for illumination normalization, "
        "median filtering, Contrast Limited Adaptive Histogram Equalization (CLAHE), interior Otsu thresholding, projection-profile deskewing, "
        "and connected-component region cleanup. Extracted text is mapped against institutional requirement criteria to generate an automated "
        "'OK / MISSING' checklist with bounding box evidence. On a benchmark of 100 degraded documents, the proposed pipeline boosts the "
        "Extraction F1-score from 0.335 to 0.745 and Recall from 21.1% to 65.0% at 0.587 seconds per document with 100% grounded spatial evidence."
    )
    r_abs_body.font.size = Pt(9.5)
    
    p_kw = doc.add_paragraph()
    r_kw_lbl = p_kw.add_run("Keywords— ")
    r_kw_lbl.bold = True
    r_kw_body = p_kw.add_run("Digital Image Processing, Document Intelligence, Illumination Correction, CLAHE, Otsu Thresholding, Deskewing, Tesseract OCR, Grounded Verification, Admissions Automation.\n")
    r_kw_body.font.italic = True
    r_kw_body.font.size = Pt(9.5)
    
    def add_sec_h(text):
        h = doc.add_paragraph()
        r = h.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = NAVY
        return h

    def add_p(text):
        p = doc.add_paragraph()
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(10)
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(6)
        return p

    # I. INTRODUCTION
    add_sec_h("I. INTRODUCTION & PROBLEM STATEMENT")
    add_p(
        "Study-abroad application platforms (such as Leap Scholar) process thousands of student dossiers containing transcripts, "
        "passports, English scores (IELTS), and statements of purpose (SOP). Applicants frequently capture documents via smartphones under "
        "uncontrolled lighting, producing non-uniform shadow gradients, high-frequency noise, and geometric skew. "
        "Manual line-by-line verification causes weeks of turnaround time and administrative fatigue. "
        "Our goal is to build an automated, explainable document intelligence system where Digital Image Processing (DIP) restores "
        "severely degraded scans to enable reliable OCR, automated checklist generation (OK vs. MISSING), and spatial evidence localization."
    )

    # II. RELATED WORK
    add_sec_h("II. STATE OF THE ART & RELATED WORK")
    add_p(
        "Document image processing has advanced across classical DIP and modern deep learning. Classic global thresholding (Otsu 1979) "
        "fails on unimodal text documents with shadows; adaptive local methods (Sauvola) and CLAHE (Zuiderveld 1994) address local contrast. "
        "Projection profile analysis provides robust rotation estimation by maximizing horizontal variance (Gonzalez & Woods 2018). "
        "While deep vision-language transformers (LayoutLM Xu et al. 2020, Donut) achieve strong understanding, they demand heavy GPU compute. "
        "Classical DIP upstream of Tesseract OCR (Smith 2007) enables real-time CPU execution with auditable spatial evidence."
    )

    # III. DATASET
    add_sec_h("III. SYNTHETIC DATASET & DEGRADATION MODELING")
    add_p(
        "To evaluate against precise ground truth, 100 synthetic application documents (850x1100 px) were generated. Each document carries up to 7 standard fields "
        "(Full Name, Passport No, DOB, Email, IELTS, SOP, Academic Transcript) with a 25% random omission probability per field to simulate missing requirements. "
        "The degradation model applies: (1) contrast compression (I_low = 110 + 0.45*I), (2) non-uniform illumination gradient (0.5 to 1.0 attenuation), "
        "(3) additive Gaussian noise (sigma 8-20) plus salt-and-pepper noise (p=0.008), and (4) 3x3 Gaussian defocus blur followed by random affine rotation (-3 to +3 deg)."
    )

    # IV. METHODOLOGY
    add_sec_h("IV. METHODOLOGY & DIP ARCHITECTURE")
    add_p(
        "The proposed pipeline consists of: (1) Grayscale conversion, (2) Illumination correction via morphological background estimation (51x51 kernel) "
        "and division, (3) 3x3 Median denoising, (4) Contrast Limited Adaptive Histogram Equalization (clip=1.0, tile=4x4), (5) Interior Otsu binarization "
        "avoiding margin skew, (6) Projection-profile deskewing, (7) Connected-component region analysis and speck removal (< 15 px), and (8) Tesseract OCR "
        "line extraction with regex requirement verification."
    )
    
    if os.path.exists("results/fig_stages.png"):
        doc.add_paragraph().add_run().add_picture("results/fig_stages.png", width=Inches(6.8))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_c = p_cap.add_run("Fig. 1. Intermediate restoration stages across the 7 DIP processing steps on doc_000.png.\n")
        r_c.font.size = Pt(8.5); r_c.font.italic = True

    # V. EXPERIMENTAL RESULTS
    add_sec_h("V. EXPERIMENTAL RESULTS & COMPARATIVE BENCHMARK")
    add_p(
        "Evaluation was conducted on all 100 test documents (700 field opportunities) comparing the baseline (direct OCR) "
        "against the improved DIP pipeline. Table I summarizes the quantitative benchmark results."
    )
    
    # Table
    table = doc.add_table(rows=1, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table.rows[0].cells
    hdrs = ["Evaluation Metric", "Baseline Pipeline", "Improved DIP Pipeline", "Absolute Gain"]
    for i, h in enumerate(hdrs):
        hdr_cells[i].text = h
        hdr_cells[i].paragraphs[0].runs[0].font.bold = True
        hdr_cells[i].paragraphs[0].runs[0].font.size = Pt(9)
        
    t_data = [
        ("Extraction Precision", "0.818", "0.873", "+0.055 (+5.5 pp)"),
        ("Extraction Recall", "0.211", "0.650", "+0.439 (>3x boost)"),
        ("Extraction F1-Score", "0.335", "0.745", "+0.410 (+122% gain)"),
        ("Missing Requirement Recall", "1.000", "1.000", "0.000 (100% detection)"),
        ("Missing Requirement Precision", "0.300", "0.554", "+0.254 (+84.7% gain)"),
        ("Groundedness", "1.000", "1.000", "100% verified evidence"),
        ("Time per Document", "0.341 s", "0.587 s", "+0.246 s (~102 docs/min)")
    ]
    for row in t_data:
        r_cells = table.add_row().cells
        for i, val in enumerate(row):
            r_cells[i].text = val
            r_cells[i].paragraphs[0].runs[0].font.size = Pt(8.5)
            
    doc.add_paragraph()
    if os.path.exists("results/fig_compare.png"):
        doc.add_paragraph().add_run().add_picture("results/fig_compare.png", width=Inches(5.0))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_c = p_cap.add_run("Fig. 2. Performance comparison bar chart: Baseline vs. Improved DIP Pipeline.\n")
        r_c.font.size = Pt(8.5); r_c.font.italic = True

    if os.path.exists("results/fig_evidence.png"):
        doc.add_paragraph().add_run().add_picture("results/fig_evidence.png", height=Inches(3.8))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_c = p_cap.add_run("Fig. 3. Final verified checklist output with spatial bounding box evidence overlays.\n")
        r_c.font.size = Pt(8.5); r_c.font.italic = True

    # VI. FAILURE ANALYSIS
    add_sec_h("VI. FAILURE ANALYSIS & LIMITATIONS")
    add_p(
        "Analysis of failure cases (results/failure_cases_improved.csv) demonstrates that in extreme shadow regions, "
        "similar numeral topologies are occasionally misclassified by Tesseract (e.g., passport P2677407 misread as P2877407, "
        "year 1999 misread as 1899). Fine noise specks touching name boundaries occasionally appended extraneous characters. "
        "Rigid regular expressions require standard phrasing, and multi-template inputs necessitate layout-aware token classifiers."
    )

    # VII. CONCLUSION
    add_sec_h("VII. CONCLUSION & FUTURE WORK")
    add_p(
        "This project demonstrated that classical DIP techniques elevate OCR performance from 0.335 to 0.745 Extraction F1 "
        "and from 21.1% to 65.0% Recall on degraded phone captures, while preserving 100% grounded spatial evidence. "
        "Future work will integrate multimodal transformers (LayoutLMv3) and dense retrieval (RAG) over multi-page documents."
    )

    # REFERENCES
    add_sec_h("REFERENCES")
    refs = [
        "1. R. Smith, 'An Overview of the Tesseract OCR Engine,' Proc. ICDAR, vol. 2, pp. 629-633, 2007.",
        "2. N. Otsu, 'A Threshold Selection Method from Gray-Level Histograms,' IEEE Trans. SMC, vol. 9, no. 1, pp. 62-66, 1979.",
        "3. K. Zuiderveld, 'Contrast Limited Adaptive Histogram Equalization,' Graphics Gems IV, Academic Press, pp. 474-485, 1994.",
        "4. Y. Xu et al., 'LayoutLM: Pre-training of Text and Layout for Document Image Understanding,' Proc. KDD, pp. 1192-1200, 2020.",
        "5. P. Lewis et al., 'Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,' Advances in NeurIPS, vol. 33, 2020.",
        "6. G. Bradski, 'The OpenCV Library,' Dr. Dobb's Journal of Software Tools, 2000.",
        "7. R. C. Gonzalez and R. E. Woods, Digital Image Processing, 4th ed., Pearson, 2018.",
        "8. S. J. Sangwine and R. E. Horne, The Image Processing Handbook, CRC Press, 2017."
    ]
    for r in refs:
        p_ref = doc.add_paragraph()
        r_ref = p_ref.add_run(r)
        r_ref.font.name = "Calibri"
        r_ref.font.size = Pt(8.5)
        p_ref.paragraph_format.space_after = Pt(2)

    doc.save(filename)
    print(f"IEEE Conference Paper (Word format) saved successfully to {filename}")

if __name__ == "__main__":
    generate_docx("Report.docx")

