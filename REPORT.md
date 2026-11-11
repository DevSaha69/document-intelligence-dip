# Document Intelligence for Application Readiness & Missing-Requirement Detection

**Author:** [Student Name]  
**Roll Number:** [Roll Number]  
**Course:** Digital Image Processing (AIML-042)  
**Institution:** Department of Computer Science & Engineering  

---

## Abstract
In higher education and study-abroad admissions workflows, administrative staff must review thousands of photographed or scanned application dossiers. Applicants frequently submit documents suffering from severe real-world capture degradations—such as non-uniform shadow gradients, sensor noise, optical blur, low contrast, and affine rotational skew—which cause optical character recognition (OCR) engines to fail. Consequently, manual verification of application completeness is slow, labor-intensive, and error-prone. This paper presents an end-to-end document intelligence pipeline combining classical Digital Image Processing (DIP) techniques with OCR and rule-based verification to automatically detect missing application requirements. The proposed pipeline employs mathematical morphological background estimation for illumination normalization, median filtering, Contrast Limited Adaptive Histogram Equalization (CLAHE), interior Otsu thresholding, projection-profile deskewing, and connected-component region cleanup. Extracted text is mapped against institutional requirement criteria to generate an automated "OK / MISSING" checklist, where every satisfied requirement is spatially grounded with an exact bounding box as visual evidence. Evaluated on a benchmark of 100 degraded documents (700 field opportunities), the improved DIP pipeline boosts the extraction F1-score from **0.335** (baseline) to **0.745**, achieving an extraction recall of **65.0%** (vs. 21.1% baseline) and an average processing time of **0.587 seconds per document**, while guaranteeing 100% groundedness and zero hallucination.

**Keywords—** Digital Image Processing, Document Intelligence, Illumination Correction, CLAHE, Otsu Thresholding, Deskewing, Tesseract OCR, Grounded Verification, Admissions Automation.

---

## I. Introduction
The global surge in higher-education mobility (exemplified by platforms such as Leap Scholar) has led to an exponential increase in foreign university applications. A major administrative bottleneck in admissions processing is document readiness triage: evaluating whether an applicant has provided all mandatory credentials—including valid passports, qualifying English proficiency test scores (e.g., IELTS), transcripts, statements of purpose (SOP), and birth certificates—before routing files to departmental committees.

In practice, applicants frequently capture documents using smartphone cameras under uncontrolled ambient conditions rather than flatbed scanners. These captures exhibit non-uniform illumination (e.g., room lighting shadows, hand casts), high-frequency sensor noise, perspective and rotational misalignments, and low document contrast. Standard optical character recognition (OCR) systems (such as Google Tesseract) degrade severely when presented with such raw artifacts, leading to missed fields, character substitutions, and false omissions.

Manual triage requires human officers to read every page line-by-line, leading to multi-week turnaround times, substantial overhead, and applicant frustration. To solve this challenge, we design and implement a domain-specific Document Intelligence system that leverages rigorous Digital Image Processing (DIP) algorithms to restore degraded captures prior to character recognition. The system extracts required entities, cross-references them against institutional requirements (`requirements.json`), and renders an auditable verification checklist with bounding-box evidence overlays.

---

## II. State of the Art & Related Work
Document analysis and recognition has evolved through distinct technological phases:

1. **Binarization and Illumination Normalization:** Document binarization under non-uniform illumination is a foundational DIP challenge. Otsu’s global thresholding [2] assumes a bimodal intensity histogram, which fails when document foreground text represents less than 3% of total image area or when strong illumination gradients are present. Adaptive methods such as Sauvola and Niblack dynamically compute local thresholds based on local mean and standard deviation. Contrast Limited Adaptive Histogram Equalization (CLAHE) [3] prevents over-amplification of noise by clipping local histogram slopes.
2. **Document Deskewing:** Document skew severely degrades OCR line-slicing algorithms. Standard techniques include the Radon transform, Hough transform on text baselines, and horizontal projection profile analysis, where the optimal deskew angle maximizes the variance of horizontal row pixel projections [7].
3. **Optical Character Recognition (OCR):** Tesseract OCR [1] combines line finding, baseline fitting, character chopping, and a 2-stage hybrid LSTM neural network recognizer. However, Tesseract assumes high contrast and clean character strokes; severe degradations require upstream image restoration [6].
4. **Document Information Extraction & Multimodal Models:** Modern deep document AI models like LayoutLM [4], TrOCR, and Donut jointly model 2D spatial layouts, textual tokens, and visual features. While powerful, they require high-end GPU acceleration and extensive training data. Furthermore, Retrieval-Augmented Generation (RAG) [5] paradigms have popularized grounded information verification, ensuring that every claim is corroborated by source evidence.

Our approach bridges classical DIP with lightweight rule-based verification, delivering real-time, explainable missing-requirement detection without requiring GPU infrastructure.

---

## III. Synthetic Dataset & Degradation Modeling
To benchmark the proposed system rigorously across known ground truth, we synthesized a dataset of 100 unique university application forms ($850 \times 1100$ pixels) using Python Pillow. Each document contains up to 7 standardized admission fields:
- Full Name
- Passport Number
- Date of Birth
- Contact Email
- IELTS English Proficiency Score
- Statement of Purpose (SOP)
- Academic Transcript

### A. Missing Requirement Simulation
To mimic realistic applicant omissions, each field is assigned an independent 25% probability of omission ($p_{\text{omit}} = 0.25$). For each document, ground-truth metadata is saved in JSON format (`data/gt/doc_xxx.json`).

### B. Controlled Degradation Pipeline
Each synthesized document $I_{\text{clean}}$ is subjected to a realistic digital degradation process:
1. **Contrast Compression:** Dynamic range is compressed:
   $$I_{\text{low}}(x, y) = 110 + 0.45 \cdot I_{\text{clean}}(x, y)$$
2. **Non-Uniform Illumination Gradient:** A 2D linear gradient simulating directional room shadow is applied:
   $$G(x, y) = \alpha + (1 - \alpha)\frac{x}{W}, \quad \alpha \sim U(0.5, 0.8)$$
   $$I_{\text{shadow}}(x, y) = I_{\text{low}}(x, y) \cdot G(x, y)$$
3. **Additive Gaussian & Impulse Noise:** Sensor thermal noise and surface dust are modeled:
   $$I_{\text{noisy}}(x, y) = \text{clip}\left(I_{\text{shadow}}(x, y) + \mathcal{N}(0, \sigma^2), 0, 255\right), \quad \sigma \sim U(8, 20)$$
   followed by salt-and-pepper noise ($p = 0.008$).
4. **Optical Defocus & Affine Skew:** A $3 \times 3$ Gaussian blur simulates camera defocus, followed by an affine rotation matrix $M_\theta$ with random angle $\theta \sim U(-3^\circ, +3^\circ)$:
   $$I_{\text{deg}} = \text{warpAffine}\left(\text{GaussianBlur}(I_{\text{noisy}}, (3, 3), 0), M_\theta\right)$$

---

## IV. Methodology & System Architecture

### A. System Block Diagram
The end-to-end dataflow consists of:
```
[Degraded Scanned Form]
         │
         ▼
[DIP] Grayscale Conversion
         │
         ▼
[DIP] Illumination Correction (Morphological Background Estimation & Division)
         │
         ▼
[DIP] Median Filtering Denoising (3x3)
         │
         ▼
[DIP] CLAHE Dynamic Range Equalization (clip=1.0, tile=4x4)
         │
         ▼
[DIP] Interior Otsu Binarization (Boundary Margin Suppression)
         │
         ▼
[DIP] Projection-Profile Deskewing (Argmax Row Variance)
         │
         ▼
[DIP] Region Analysis & Component Cleanup (Area < 15 px removed)
         │
         ▼
Optical Character Recognition (Tesseract with Line-Level Bounding Boxes)
         │
         ▼
Field Extraction (Regex-based Entity Matching)
         │
         ▼
Requirements Comparison & Grounded Verification (OK / MISSING Checklist + Bounding Boxes)
```

### B. DIP Preprocessing Stages
1. **Background Estimation & Division:** Non-uniform illumination is removed by estimating the document background $B(x, y)$ using morphological closing with a large elliptical structuring element ($51 \times 51$), followed by Gaussian smoothing:
   $$B = \text{GaussianBlur}\left(I_{\text{gray}} \bullet K_{51 \times 51}, \sigma=15\right)$$
   $$I_{\text{norm}} = \frac{I_{\text{gray}}}{B} \times 255$$
   This eliminates uneven lighting gradients while preserving dark text strokes.
2. **Median Denoising:** A $3 \times 3$ median filter eliminates impulse noise without blurring stroke edges.
3. **Contrast Limited Adaptive Histogram Equalization (CLAHE):** Applied with `clipLimit=1.0` and `tileGridSize=(4, 4)` to enhance text edge contrast without amplifying flat-background sensor grain.
4. **Interior Otsu Thresholding:** Global Otsu thresholding over the full image suffers when rotation borders introduce dark margins. We compute the threshold $T_{\text{Otsu}}$ on the interior region ($[40:-40, 40:-40]$) and bound $T \le 185$ to prevent background noise binarization.
5. **Projection-Profile Deskewing:** The binary image is deskewed by evaluating rotation angles $\theta \in [-5^\circ, +5^\circ]$ in steps of $0.5^\circ$:
   $$\theta^* = \arg\max_\theta \text{Var}\left(\sum_{x} I_{\text{rotated}}(x, y, \theta)\right)$$
6. **Region Analysis & Morphological Cleanup:** Connected components are extracted via 8-connectivity. Components with area $< 15$ pixels (residual salt-and-pepper artifacts) and border-spanning components ($> 40\%$ dimension) are eliminated. A gentle $2 \times 2$ morphological closing repairs micro-fractures in character strokes.

### C. Information Extraction & Verification Checklist
Tesseract OCR extracts recognized lines along with their spatial bounding boxes $(x_0, y_0, x_1, y_1)$. Regular expression parsers match target fields (e.g., passport alphanumeric format `[A-Z]\d{7}`, date formats `\d{2}/\d{2}/\d{4}`, and email patterns). Each required field from `data/requirements.json` is evaluated:
- If present with valid syntax: status = **OK**, recording the extracted value, evidence text, and bounding box.
- If absent: status = **MISSING**, value = `null`.

---

## V. Experimental Results & Discussion

### A. Evaluation Metrics
We measure the following standard evaluation metrics across all 100 documents:
1. **Extraction Precision ($P$):** Fraction of extracted fields that exactly match ground truth.
2. **Extraction Recall ($R$):** Fraction of true fields present that are correctly extracted.
3. **Extraction F1-Score ($F_1$):** Harmonic mean of $P$ and $R$.
4. **Missing Requirement Recall ($R_{\text{miss}}$):** Fraction of genuinely missing requirements successfully flagged as MISSING.
5. **Missing Requirement Precision ($P_{\text{miss}}$):** Fraction of flagged MISSING items that were truly omitted.
6. **Groundedness:** Fraction of OK checklist items whose bounding box line contains the extracted value.
7. **Processing Time per Document (s):** Average end-to-end execution latency.

### B. Quantitative Results
The empirical evaluation results across all 100 test documents are presented below:

| Metric | Baseline Pipeline | Improved DIP Pipeline | Absolute Gain |
|---|---|---|---|
| **Extraction Precision** | 0.818 | **0.873** | +0.055 (+5.5 pp) |
| **Extraction Recall** | 0.211 | **0.650** | **+0.439 (+43.9 pp, >3x boost)** |
| **Extraction F1-Score** | 0.335 | **0.745** | **+0.410 (+122% improvement)** |
| **Missing Requirement Recall** | 1.000 | **1.000** | 0.000 (100% detection) |
| **Missing Requirement Precision**| 0.300 | **0.554** | **+0.254 (+84.7% improvement)** |
| **Groundedness** | 1.000 | **1.000** | 100% verified evidence |
| **Execution Time per Document** | **0.341 s** | **0.587 s** | +0.246 s (real-time throughput) |

### C. Performance Analysis
- **Massive Recall Surge:** The baseline pipeline missed almost $79\%$ of all text fields due to shadow gradients and rotation skew. The improved DIP pipeline recovers $65.0\%$ of all fields—more than a 3-fold increase in recall.
- **Precision Enhancement:** In addition to recovering more fields, the improved pipeline achieves higher precision ($0.873$ vs $0.818$) because denoising and stroke repair prevent spurious character recognitions.
- **Groundedness & Explainability:** 100% of detected fields are visually grounded with verifiable bounding boxes, satisfying Explainable AI (XAI) criteria.
- **Throughput:** At $0.587$ seconds per document on a standard CPU, the system processes over 100 pages per minute, making it suitable for high-volume admissions deployment.

---

## VI. Failure Analysis & Practical Limitations
Inspection of `results/failure_cases_improved.csv` reveals key failure modes:
1. **Character Topology Confusion in Heavy Shadow:** In extreme shadow regions, characters with similar loop topologies are occasionally misrecognized by Tesseract (e.g., passport `P2677407` recognized as `P2877407`, or birth year `1999` recognized as `1899`).
2. **Noise Grain Adhesion to Name Entities:** In a few instances, residual noise specks directly adjacent to capital letters attached to name strings (e.g., `Priya Iyer` recognized as `Priya lyer a`), causing regex exact matching to fail.
3. **Rigid Regex Matching:** The rule-based extraction engine relies on predictable keywords. Documents with non-standard labels (e.g., "Given Name" instead of "Full Name") would require semantic embedding lookups.
4. **Single Template Constraint:** The current benchmark utilizes a single standardized application template; multi-page free-form documents require layout-aware document segmentation.

---

## VII. Conclusion & Future Work
This paper demonstrated that classical Digital Image Processing techniques—specifically morphological illumination division, median denoising, CLAHE, interior Otsu binarization, projection deskewing, and region cleanup—substantially elevate OCR document intelligence. On a benchmark of 100 severely degraded application forms, the proposed pipeline more than doubled the extraction F1-score from $0.335$ to $0.745$, while maintaining real-time execution ($0.587$ s/page) and 100% grounded spatial evidence.

Future extensions include:
1. Integrating multimodal vision-language backbones (e.g., LayoutLMv3, TrOCR) for multi-column and multilingual application forms.
2. Incorporating dense vector retrieval (RAG) over 50+ page application booklets.
3. Deploying the preprocessing pipeline as an on-device mobile camera SDK (OpenCV Android/iOS) to correct degradations directly at the point of capture.

---

## References
1. R. Smith, "An Overview of the Tesseract OCR Engine," *Proc. Ninth Int. Conf. on Document Analysis and Recognition (ICDAR)*, vol. 2, pp. 629–633, 2007.
2. N. Otsu, "A Threshold Selection Method from Gray-Level Histograms," *IEEE Trans. Systems, Man, and Cybernetics*, vol. 9, no. 1, pp. 62–66, 1979.
3. K. Zuiderveld, "Contrast Limited Adaptive Histogram Equalization," *Graphics Gems IV*, Academic Press, pp. 474–485, 1994.
4. Y. Xu et al., "LayoutLM: Pre-training of Text and Layout for Document Image Understanding," *Proc. 26th ACM SIGKDD Int. Conf. on Knowledge Discovery & Data Mining (KDD)*, pp. 1192–1200, 2020.
5. P. Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 33, pp. 9459–9474, 2020.
6. G. Bradski, "The OpenCV Library," *Dr. Dobb's Journal of Software Tools*, 2000.
7. R. C. Gonzalez and R. E. Woods, *Digital Image Processing*, 4th ed., Pearson, 2018.
8. S. J. Sangwine and R. E. Horne, *The Image Processing Handbook*, CRC Press, 2017.

