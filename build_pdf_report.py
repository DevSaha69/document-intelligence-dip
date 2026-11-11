import os
from fpdf import FPDF

class IEEE_Report(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(100, 100, 100)
            self.cell(0, 5, "Digital Image Processing Project - Document Intelligence for Application Readiness", 0, 0, "L")
            self.cell(0, 5, f"Page {self.page_no()}", 0, 1, "R")
            self.line(10, 15, 200, 15)
            self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"IEEE Conference Paper Outline | Digital Image Processing Final Project", 0, 0, "C")

    def section_title(self, title):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(26, 54, 93) # Navy
        self.ln(3)
        self.cell(0, 6, title, 0, 1, "L")
        self.set_text_color(30, 41, 59)

    def subsection_title(self, title):
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(49, 151, 149) # Teal
        self.cell(0, 5, title, 0, 1, "L")
        self.set_text_color(30, 41, 59)

    def body_p(self, text):
        self.set_font("Helvetica", "", 8.5)
        self.set_text_color(30, 41, 59)
        self.multi_cell(0, 4.2, text)
        self.ln(1.5)

def generate_pdf(filename="Report.pdf", student_name="[Student Name]", roll_no="[Roll Number]"):
    pdf = IEEE_Report(format="A4")
    pdf.set_margins(12, 12, 12)
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # PAGE 1
    pdf.add_page()
    
    # Title
    pdf.set_font("Helvetica", "B", 15)
    pdf.set_text_color(26, 54, 93)
    pdf.multi_cell(0, 6.5, "Document Intelligence for Application Readiness &\nMissing-Requirement Detection", 0, "C")
    pdf.ln(2)
    
    # Authors
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.set_text_color(74, 85, 104)
    pdf.cell(0, 4.5, f"Author: {student_name} (Roll No: {roll_no})", 0, 1, "C")
    pdf.set_font("Helvetica", "I", 8.5)
    pdf.cell(0, 4, "Department of Computer Science & Engineering | Digital Image Processing Project (AIML-042)", 0, 1, "C")
    pdf.ln(3)
    
    # Abstract box
    pdf.set_fill_color(245, 247, 250)
    pdf.set_draw_color(210, 215, 225)
    pdf.rect(12, pdf.get_y(), 186, 32, "FD")
    y_start = pdf.get_y() + 2
    pdf.set_xy(14, y_start)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(26, 54, 93)
    pdf.write(4, "Abstract- ")
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(40, 40, 40)
    abstract_text = (
        "In study-abroad and higher education admissions, administrative triage of photographed/scanned application forms "
        "is a critical operational bottleneck. Real-world captures suffer from severe degradations including uneven illumination shadows, "
        "sensor noise, optical blur, low contrast, and affine rotational skew, causing standard OCR systems to fail. "
        "This paper presents an end-to-end document intelligence pipeline combining classical Digital Image Processing (DIP) techniques "
        "with OCR and rule verification. The proposed pipeline employs morphological closing background division, median filtering, CLAHE, "
        "interior Otsu binarization, projection deskewing, and region cleanup. Evaluated on a benchmark of 100 degraded documents (700 field opportunities), "
        "the improved pipeline more than doubles the Extraction F1-score from 0.335 to 0.745 (Recall 21.1% to 65.0%) with 100% grounded spatial evidence "
        "in 0.587 seconds per document."
    )
    pdf.write(3.8, abstract_text)
    pdf.ln(4)
    pdf.set_x(14)
    pdf.set_font("Helvetica", "B", 8)
    pdf.write(4, "Keywords- ")
    pdf.set_font("Helvetica", "I", 7.5)
    pdf.write(4, "Digital Image Processing, Document Intelligence, Illumination Correction, CLAHE, Otsu Thresholding, Deskewing, Tesseract OCR, Grounded Verification.")
    pdf.set_y(y_start + 32)
    pdf.ln(3)
    
    # Section I
    pdf.section_title("I. INTRODUCTION & PROBLEM STATEMENT")
    pdf.body_p(
        "Study-abroad application platforms (such as Leap Scholar) process thousands of student dossiers containing transcripts, "
        "passports, English scores (IELTS), and statements of purpose (SOP). Applicants frequently capture documents via smartphones under "
        "uncontrolled lighting, producing non-uniform shadow gradients, high-frequency noise, and geometric skew. "
        "Manual line-by-line verification causes weeks of turnaround time and administrative fatigue. "
        "Our goal is to build an automated, explainable document intelligence system where Digital Image Processing (DIP) restores "
        "severely degraded scans to enable reliable OCR, automated checklist generation (OK vs. MISSING), and spatial evidence localization."
    )
    
    # Section II
    pdf.section_title("II. STATE OF THE ART & RELATED WORK")
    pdf.body_p(
        "Document image processing has advanced across classical DIP and modern deep learning. Classic global thresholding (Otsu 1979) "
        "fails on unimodal text documents with shadows; adaptive local methods (Sauvola) and CLAHE (Zuiderveld 1994) address local contrast. "
        "Projection profile analysis provides robust rotation estimation by maximizing horizontal variance (Gonzalez & Woods 2018). "
        "While deep vision-language transformers (LayoutLM Xu et al. 2020, Donut) achieve strong understanding, they demand heavy GPU compute. "
        "Classical DIP upstream of Tesseract OCR (Smith 2007) enables real-time CPU execution with auditable spatial evidence."
    )

    # Section III
    pdf.section_title("III. SYNTHETIC DATASET & DEGRADATION MODELING")
    pdf.body_p(
        "To evaluate against precise ground truth, 100 synthetic application documents (850x1100 px) were generated. Each document carries up to 7 standard fields "
        "(Full Name, Passport No, DOB, Email, IELTS, SOP, Academic Transcript) with a 25% random omission probability per field to simulate missing requirements. "
        "The degradation model applies: (1) contrast compression (I_low = 110 + 0.45*I), (2) non-uniform illumination gradient (0.5 to 1.0 attenuation), "
        "(3) additive Gaussian noise (sigma 8-20) plus salt-and-pepper noise (p=0.008), and (4) 3x3 Gaussian defocus blur followed by random affine rotation (-3 to +3 deg)."
    )

    # PAGE 2
    pdf.add_page()
    pdf.section_title("IV. METHODOLOGY & DIP ARCHITECTURE")
    pdf.body_p(
        "The architecture operates in three modular phases: (1) DIP restoration pipeline, (2) OCR line-evidence extraction, "
        "and (3) requirement verification against requirements.json."
    )
    
    # Pseudocode box
    pdf.set_fill_color(240, 244, 248)
    pdf.set_draw_color(200, 210, 225)
    pdf.rect(12, pdf.get_y(), 186, 42, "FD")
    y_code = pdf.get_y() + 2
    pdf.set_xy(14, y_code)
    pdf.set_font("Courier", "B", 7.5)
    pdf.set_text_color(20, 30, 60)
    code_lines = [
        "Algorithm 1: End-to-End DIP Document Intelligence Pipeline",
        "Input : Degraded document image I; Institutional requirements R (requirements.json)",
        "Output: Binarized document, Extracted entities, Grounded OK/MISSING checklist with bounding boxes",
        "1: G = to_grayscale(I);  K = getStructuringElement(MORPH_ELLIPSE, (51, 51))",
        "2: B = GaussianBlur(morphologyEx(G, MORPH_CLOSE, K), (0, 0), sigma=15)    // Background estimation",
        "3: I_norm = divide(G, B, scale=255);  D = medianBlur(I_norm, 3)             // Gradient cancellation & denoise",
        "4: C = createCLAHE(clipLimit=1.0, tileGridSize=(4, 4)).apply(D)            // Local contrast enhancement",
        "5: T_otsu = threshold_otsu(C[40:-40, 40:-40]);  BW = threshold(C, min(T_otsu, 185), 255) // Interior Otsu",
        "6: BW = rotate(BW, theta_opt = argmax_theta Var(sum_x(BW_rotated(theta)))) // Projection deskew",
        "7: Inv = 255 - BW;  filter_connected_components(Inv, area < 15 px);  Out = 255 - Inv",
        "8: Lines, Boxes = Tesseract_OCR(Out, config='--psm 6')",
        "9: Checklist = verify_requirements(Lines, Boxes, R)  // OK with evidence box or MISSING"
    ]
    for cl in code_lines:
        pdf.cell(0, 3.8, cl, 0, 1, "L")
        pdf.set_x(14)
    pdf.set_y(y_code + 43)
    pdf.ln(3)

    pdf.subsection_title("Visual Progression Across 7 DIP Stages:")
    if os.path.exists("results/fig_stages.png"):
        pdf.image("results/fig_stages.png", x=12, y=pdf.get_y(), w=186)
        pdf.set_y(pdf.get_y() + 105)
    pdf.ln(2)

    # PAGE 3
    pdf.add_page()
    pdf.section_title("V. EXPERIMENTAL RESULTS & COMPARATIVE BENCHMARK")
    pdf.body_p(
        "We evaluated both the Baseline (grayscale directly to OCR) and the Improved DIP pipeline across all 100 documents "
        "(700 total evaluation field opportunities). Ground truth metadata was compared via whitespace-normalized exact string matching."
    )
    
    # Results Table
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(26, 54, 93)
    pdf.set_text_color(255, 255, 255)
    
    col_w = [55, 42, 42, 47]
    headers = ["Evaluation Metric", "Baseline Pipeline", "Improved DIP Pipeline", "Absolute Improvement"]
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 6, h, 1, 0, "C", True)
    pdf.ln()
    
    table_data = [
        ("Extraction Precision", "0.818", "0.873", "+0.055 (+5.5 pp)"),
        ("Extraction Recall", "0.211", "0.650", "+0.439 (>3x improvement)"),
        ("Extraction F1-Score", "0.335", "0.745", "+0.410 (+122% gain)"),
        ("Missing Requirement Recall", "1.000", "1.000", "0.000 (100% detection)"),
        ("Missing Requirement Precision", "0.300", "0.554", "+0.254 (+84.7% gain)"),
        ("Groundedness", "1.000", "1.000", "100% verified spatial evidence"),
        ("Execution Time per Document", "0.341 s", "0.587 s", "+0.246 s (~102 docs/min)")
    ]
    
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(30, 41, 59)
    for row_idx, row in enumerate(table_data):
        fill = (row_idx % 2 == 1)
        pdf.set_fill_color(245, 247, 250) if fill else pdf.set_fill_color(255, 255, 255)
        for i, val in enumerate(row):
            align = "L" if i == 0 else "C"
            pdf.cell(col_w[i], 5.2, val, 1, 0, align, True)
        pdf.ln()
    pdf.ln(3)

    pdf.subsection_title("Performance Comparison Chart & Grounded Verification Visuals:")
    y_charts = pdf.get_y()
    if os.path.exists("results/fig_compare.png") and os.path.exists("results/fig_evidence.png"):
        pdf.image("results/fig_compare.png", x=12, y=y_charts, w=95)
        pdf.image("results/fig_evidence.png", x=112, y=y_charts, h=65)
        pdf.set_y(y_charts + 68)
    pdf.ln(2)

    # PAGE 4
    pdf.add_page()
    pdf.section_title("VI. FAILURE ANALYSIS & PRACTICAL LIMITATIONS")
    pdf.body_p(
        "Analysis of failure cases (results/failure_cases_improved.csv) illuminates key operational boundaries:\n"
        "- Character Confusion in Dark Shadow: Severe illumination attenuation occasionally leads to numeral misclassifications "
        "(e.g., passport digit '6' read as '8' in P2677407 -> P2877407; birth year 1999 -> 1899).\n"
        "- Noise Specks on Entity Margins: Fine salt-and-pepper artifacts touching character strokes occasionally altered name tokens "
        "(e.g., Priya Iyer read as 'Priya lyer a').\n"
        "- Regex Rigidity: Keyword patterns require predefined phrasing; novel synonyms require semantic embedding matching.\n"
        "- Template Uniformity: The synthetic evaluation assumes a standard 1-column form; multi-page layouts require layout segmentation."
    )

    pdf.section_title("VII. NOVELTY, ETHICS & EXPLAINABILITY")
    pdf.body_p(
        "Unlike black-box generative models prone to hallucinations, our DIP framework guarantees 100% groundedness: "
        "every verified requirement carries an exact bounding box in image coordinates. Human admissions reviewers can inspect "
        "the visual overlay directly, fulfilling strict Explainable AI (XAI) mandates for high-stakes educational decision-making."
    )

    pdf.section_title("VIII. CONCLUSION & FUTURE WORK")
    pdf.body_p(
        "This project establishes that classical Digital Image Processing remains indispensable for document AI. "
        "On 100 degraded application forms, morphological background division, median filtering, CLAHE, interior Otsu binarization, "
        "deskewing, and region cleanup boosted OCR Extraction F1 from 0.335 to 0.745 and Recall from 21.1% to 65.0% at 0.587 s/doc. "
        "Future work includes integrating transformer vision backbones (LayoutLMv3), dense vector retrieval (RAG) for multi-page dossiers, "
        "and deploying the pipeline on mobile devices via OpenCV sidecars."
    )

    pdf.section_title("REFERENCES")
    pdf.set_font("Helvetica", "", 7.5)
    refs = [
        "[1] R. Smith, 'An Overview of the Tesseract OCR Engine,' Proc. ICDAR, vol. 2, pp. 629-633, 2007.",
        "[2] N. Otsu, 'A Threshold Selection Method from Gray-Level Histograms,' IEEE Trans. SMC, vol. 9, no. 1, pp. 62-66, 1979.",
        "[3] K. Zuiderveld, 'Contrast Limited Adaptive Histogram Equalization,' Graphics Gems IV, Academic Press, pp. 474-485, 1994.",
        "[4] Y. Xu et al., 'LayoutLM: Pre-training of Text and Layout for Document Image Understanding,' Proc. KDD, pp. 1192-1200, 2020.",
        "[5] P. Lewis et al., 'Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,' Advances in NeurIPS, vol. 33, 2020.",
        "[6] G. Bradski, 'The OpenCV Library,' Dr. Dobb's Journal of Software Tools, 2000.",
        "[7] R. C. Gonzalez and R. E. Woods, Digital Image Processing, 4th ed., Pearson, 2018.",
        "[8] S. J. Sangwine and R. E. Horne, The Image Processing Handbook, CRC Press, 2017."
    ]
    for r in refs:
        pdf.cell(0, 3.8, r, 0, 1, "L")

    pdf.output(filename)
    print(f"IEEE 4-page Paper saved successfully to {filename}")

if __name__ == "__main__":
    generate_pdf("Report.pdf")

