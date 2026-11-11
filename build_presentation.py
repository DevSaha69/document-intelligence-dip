import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck(output_path="Presentation.pptx", student_name="[Student Name]", roll_no="[Roll Number]"):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]
    
    # Color palette
    NAVY = RGBColor(26, 54, 93)      # #1A365D Primary dark
    SLATE = RGBColor(74, 85, 104)    # #4A5568 Secondary text
    TEAL = RGBColor(49, 151, 149)    # #319795 Accent
    LIGHT_BG = RGBColor(247, 250, 252) # #F7FAFC Background card
    WHITE = RGBColor(255, 255, 255)
    DARK = RGBColor(30, 41, 59)
    GREEN = RGBColor(40, 167, 69)

    def add_header(slide, title, subtitle=None):
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(1.0))
        tf = header_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = "Calibri"
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = NAVY
        
        if subtitle:
            p2 = tf.add_paragraph()
            p2.text = subtitle
            p2.font.name = "Calibri"
            p2.font.size = Pt(14)
            p2.font.color.rgb = SLATE

    # SLIDE 1: Title Slide
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = NAVY
    bg1.line.color.rgb = NAVY
    
    tb1 = s1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.333), Inches(4.0))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "Document Intelligence for Application Readiness & Missing-Requirement Detection"
    p.font.name = "Calibri"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = WHITE
    
    p2 = tf1.add_paragraph()
    p2.text = "\nDigital Image Processing Final Project"
    p2.font.name = "Calibri"
    p2.font.size = Pt(22)
    p2.font.color.rgb = TEAL
    
    p3 = tf1.add_paragraph()
    p3.text = f"\nPrepared by: {student_name} (Roll No: {roll_no})\nDomain: Computer Vision, OCR & DIP Preprocessing"
    p3.font.name = "Calibri"
    p3.font.size = Pt(16)
    p3.font.color.rgb = RGBColor(226, 232, 240)

    # SLIDE 2: Problem Statement & Motivation
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Problem Statement & Practical Motivation", "Automating university admissions triage and missing-document detection")
    
    # Left Card
    c1 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    c1.fill.solid(); c1.fill.fore_color.rgb = LIGHT_BG; c1.line.color.rgb = RGBColor(226, 232, 240)
    tf_c1 = c1.text_frame; tf_c1.word_wrap = True
    p = tf_c1.paragraphs[0]; p.text = "The Admissions Bottleneck"; p.font.bold = True; p.font.size = Pt(20); p.font.color.rgb = NAVY
    points_1 = [
        "Study-abroad portals receive thousands of photographed/scanned forms weekly.",
        "Students frequently submit incomplete packages (missing IELTS, SOP, Passport, etc.).",
        "Manual verification causes long turnaround times (days to weeks) and costly human error.",
        "Raw scans suffer from severe phone-capture defects: uneven shadows, tilt/skew, low contrast, and sensor noise."
    ]
    for pt in points_1:
        p = tf_c1.add_paragraph()
        p.text = f"- {pt}"
        p.font.size = Pt(14); p.font.color.rgb = DARK
        
    # Right Card
    c2 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.8))
    c2.fill.solid(); c2.fill.fore_color.rgb = LIGHT_BG; c2.line.color.rgb = RGBColor(226, 232, 240)
    tf_c2 = c2.text_frame; tf_c2.word_wrap = True
    p = tf_c2.paragraphs[0]; p.text = "Proposed DIP Solution"; p.font.bold = True; p.font.size = Pt(20); p.font.color.rgb = TEAL
    points_2 = [
        "An automated end-to-end DIP pipeline to restore degraded document images.",
        "Combines morphological background division, median filtering, CLAHE, and projection deskewing.",
        "Robust OCR line bounding-box segmentation via Tesseract engine.",
        "Regex-based Named Entity Recognition against institution requirements.",
        "Generates a grounded OK / MISSING verification checklist with spatial evidence boxes."
    ]
    for pt in points_2:
        p = tf_c2.add_paragraph()
        p.text = f"- {pt}"
        p.font.size = Pt(14); p.font.color.rgb = DARK

    # SLIDE 3: System Architecture & Block Diagram
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "System Architecture & DIP Pipeline Workflow", "Complete dataflow from degraded acquisition to verified readiness checklist")
    
    tb3 = s3.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf3 = tb3.text_frame; tf3.word_wrap = True
    
    stages_info = [
        ("1. Input Document", "Photographed / scanned form with shadow gradients, blur, and skew."),
        ("2. Illumination Correction", "Morphological closing (elliptical kernel 51x51) estimates background; gray / bg * 255 cancels gradients."),
        ("3. Median Denoising", "3x3 median filter eliminates impulse noise and salt-and-pepper grain."),
        ("4. Contrast Enhancement (CLAHE)", "Contrast Limited Adaptive Histogram Equalization redistributes text-to-background dynamic range."),
        ("5. Interior Otsu Thresholding", "Binarization calculated on inner text area avoiding boundary shadow skews."),
        ("6. Projection-Profile Deskew", "Variance of horizontal row projections var(sum_x) finds tilt angle (-5 to +5 deg)."),
        ("7. Region Analysis & Speck Removal", "Connected components filter out noise clusters (< 15 px) and outer boundary artifacts."),
        ("8. OCR & Grounded Evidence", "Tesseract extracts word/line bounding boxes; regex NER matches requirements to generate checklist.")
    ]
    for stg, desc in stages_info:
        p = tf3.add_paragraph()
        p.text = f"{stg}: {desc}"
        p.font.size = Pt(13)
        p.font.name = "Calibri"
        p.font.color.rgb = DARK

    # SLIDE 4: Dataset & Degradation Model
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Synthetic Dataset & Degradation Modeling", "Controlled generation of 100 application documents with known ground truth")
    
    tb4 = s4.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf4 = tb4.text_frame; tf4.word_wrap = True
    
    d_points = [
        ("Controlled Synthetic Ground Truth", "100 application forms generated via PIL (850x1100 resolution) featuring up to 7 standard university admissions fields: Full Name, Passport Number, Date of Birth, Email, IELTS Score, Statement of Purpose, Academic Transcript."),
        ("Simulated Missing Requirements", "Each field has a ~25% independent probability of omission, mimicking real-world applicant omissions."),
        ("Uneven Illumination & Shadows", "Linear gradient multiplication (0.5 to 1.0 attenuation across width) simulating room lighting and hand shadows."),
        ("Contrast Compression", "Linear rescaling: I_low = 110 + 0.45 * I, compressing text-to-paper dynamic range."),
        ("Additive & Impulse Noise", "Additive Gaussian noise (sigma ~ 8 to 20) + salt-and-pepper noise (p = 0.008 total)."),
        ("Optical Blur & Geometric Affine Skew", "Gaussian blur (3x3 kernel) simulating camera defocus + random affine rotation (-3 to +3 degrees).")
    ]
    for heading, desc in d_points:
        p = tf4.add_paragraph()
        p.text = f"{heading}: {desc}"
        p.font.size = Pt(14)
        p.font.color.rgb = DARK

    # SLIDE 5: Visual Stages
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "DIP Intermediate Restoration Stages", "Visual progression across the 7 restoration operations on doc_000.png")
    if os.path.exists("results/fig_stages.png"):
        s5.shapes.add_picture("results/fig_stages.png", Inches(0.8), Inches(1.8), width=Inches(11.7))

    # SLIDE 6: Comparative Results
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Experimental Evaluation: Baseline vs. Improved", "Rigorous benchmarking across 100 documents (700 evaluation field opportunities)")
    
    if os.path.exists("results/fig_compare.png"):
        s6.shapes.add_picture("results/fig_compare.png", Inches(0.8), Inches(2.0), width=Inches(5.5))
        
    tb6 = s6.shapes.add_textbox(Inches(6.6), Inches(2.0), Inches(5.9), Inches(4.8))
    tf6 = tb6.text_frame; tf6.word_wrap = True
    p = tf6.paragraphs[0]; p.text = "Key Quantitative Findings:"; p.font.bold = True; p.font.size = Pt(18); p.font.color.rgb = NAVY
    res_points = [
        "Extraction Precision: 81.8% -> 87.3% (+5.5 pp)",
        "Extraction Recall: 21.1% -> 65.0% (+43.9 pp, >3x boost!)",
        "Extraction F1-Score: 0.335 -> 0.745 (+0.410 jump)",
        "Missing Requirement Precision: 30.0% -> 55.4% (near 2x boost)",
        "Missing Requirement Recall: 100% on both pipelines",
        "Groundedness: 100.0% (all OK items carry verified bounding box evidence)",
        "Runtime per Document: 0.587s (real-time throughput, ~102 pages/min)"
    ]
    for r in res_points:
        p = tf6.add_paragraph()
        p.text = f"- {r}"
        p.font.size = Pt(14); p.font.color.rgb = DARK

    # SLIDE 7: Grounded Evidence Output
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Readiness Checklist & Spatial Grounding", "Visual bounding box evidence and structured verification JSON")
    if os.path.exists("results/fig_evidence.png"):
        s7.shapes.add_picture("results/fig_evidence.png", Inches(0.8), Inches(1.8), height=Inches(5.0))
        
    tb7 = s7.shapes.add_textbox(Inches(5.5), Inches(1.8), Inches(7.0), Inches(5.0))
    tf7 = tb7.text_frame; tf7.word_wrap = True
    p = tf7.paragraphs[0]; p.text = "Checklist Verification Output:"; p.font.bold = True; p.font.size = Pt(18); p.font.color.rgb = NAVY
    c_pts = [
        "Each detected requirement is validated against university rules.",
        "Extracted field carries exact bounding box coordinates (x0, y0, x1, y1) in image space.",
        "Green bounding boxes superimposed directly over applicant document.",
        "Guarantees Explainable AI (XAI): human reviewers can instantly verify flagged items without re-reading the entire page.",
        "Missing requirements are flagged for automated reminder emails to applicants."
    ]
    for cp in c_pts:
        p = tf7.add_paragraph()
        p.text = f"- {cp}"
        p.font.size = Pt(14); p.font.color.rgb = DARK

    # SLIDE 8: Failure Analysis & Limitations
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Failure Analysis & Engineering Limitations", "Honest characterization of challenging failure modes")
    
    tb8 = s8.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf8 = tb8.text_frame; tf8.word_wrap = True
    
    fails = [
        ("Character Confusion in Noisy Digits", "In severe shadow regions, digits with similar stroke topology are occasionally misread (e.g. 'P2677407' read as 'P2877407', '1999' read as '1899')."),
        ("Speck Merging on Name Boundaries", "Residual noise touching trailing characters can cause regex NER mismatch (e.g. 'Priya Iyer' read as 'Priya lyer a')."),
        ("Single-Template Layout Assumption", "Current evaluation uses a single standardized application template; variable layouts require layout-aware NER."),
        ("Regex Rule Rigidity", "Exact regex patterns require specific keywords; non-standard headings require semantic NLP or LayoutLM embeddings.")
    ]
    for heading, desc in fails:
        p = tf8.add_paragraph()
        p.text = f"{heading}: {desc}"
        p.font.size = Pt(14); p.font.color.rgb = DARK

    # SLIDE 9: Conclusion & Future Scope
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "Conclusion & Future Horizons", "Summary of impact and next-generation document intelligence")
    
    tb9 = s9.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf9 = tb9.text_frame; tf9.word_wrap = True
    
    concs = [
        ("DIP Restoration is Essential", "Demonstrated that classical Digital Image Processing techniques (illumination division, CLAHE, Otsu, deskew) more than double OCR Extraction F1 (0.335 -> 0.745) on realistic mobile captures."),
        ("Grounded Explainability", "Every verification decision provides visual evidence bounding boxes, ensuring 100% groundedness and zero hallucination."),
        ("Future Direction 1: Deep Vision-Language Models", "Integrating multimodal document understanding backbones (LayoutLMv3, Donut, TrOCR) for multi-column, free-form documents."),
        ("Future Direction 2: Retrieval-Augmented Generation (RAG)", "Coupling OCR line vectors with vector databases to perform semantic requirement checks across 50+ page application booklets."),
        ("Future Direction 3: On-Device Mobile SDK", "Compensating camera distortions at point-of-capture via lightweight OpenCV Android/iOS sidecars.")
    ]
    for heading, desc in concs:
        p = tf9.add_paragraph()
        p.text = f"{heading}: {desc}"
        p.font.size = Pt(14); p.font.color.rgb = DARK

    prs.save(output_path)
    print(f"Presentation saved successfully to {output_path}")

if __name__ == "__main__":
    create_deck("Presentation.pptx")

