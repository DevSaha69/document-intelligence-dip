# Document Intelligence for Application Readiness & Missing-Requirement Detection

**Digital Image Processing Final Project (AIML-042)**

---

## 1. Project Overview
This project solves the problem of automated university application triage and missing-requirement detection on low-quality, photographed or scanned student forms.

When applicants submit forms captured via mobile phones, images typically suffer from:
- **Non-uniform illumination** (room lighting shadows, hand casts)
- **High-frequency sensor noise** (thermal grain, salt-and-pepper artifacts)
- **Contrast degradation** (faint text, washed-out paper)
- **Optical defocus blur & geometric skew** (misaligned camera angles)

Our system applies an end-to-end Digital Image Processing (DIP) restoration pipeline upstream of Tesseract OCR to reliably extract form fields, compare them against a university requirements list (`data/requirements.json`), and output a verified **OK / MISSING** checklist where every satisfied requirement is **spatially grounded with bounding box evidence**.

---

## 2. Baseline vs. Improved Pipeline

### Baseline Pipeline:
- Converts input to grayscale → passes directly to Tesseract OCR.

### Improved DIP Pipeline:
1. **Grayscale Conversion**: Base intensity plane.
2. **Illumination Correction**: Background estimated via morphological closing with an elliptical structuring element ($51 \times 51$) followed by Gaussian smoothing; dividing the original by the background cancels shadow gradients:
   $$\text{norm} = \frac{\text{gray}}{\text{bg}} \times 255$$
3. **Median Denoising**: $3 \times 3$ median filter eliminates impulse noise while preserving sharp character stroke edges.
4. **Contrast Limited Adaptive Histogram Equalization (CLAHE)**: Enhances local stroke contrast without amplifying empty background noise (`clipLimit=1.0`, `tileGridSize=(4, 4)`).
5. **Interior Otsu Thresholding**: Calculates Otsu's optimal binarization threshold on the interior document area to prevent boundary shadow distortion, bounded by a safety noise threshold ($T \le 185$).
6. **Projection-Profile Deskewing**: Rotates the binarized image to the angle $\theta \in [-5^\circ, +5^\circ]$ that maximizes horizontal projection row variance:
   $$\theta^* = \arg\max_\theta \text{Var}\left(\sum_x I_{\text{rotated}}(x, y, \theta)\right)$$
7. **Region Analysis & Morphological Cleanup**: Connected component analysis filters out residual noise specks ($< 15\text{ px}$) and boundary artifacts. A gentle $2 \times 2$ closing repairs stroke discontinuities.

---

## 3. Results Summary (100 Documents Benchmark)

| Evaluation Metric | Baseline Pipeline | Improved DIP Pipeline | Absolute Gain |
|---|---|---|---|
| **Extraction Precision** | 81.8% | **87.3%** | +5.5 pp |
| **Extraction Recall** | 21.1% | **65.0%** | **+43.9 pp (>3x boost)** |
| **Extraction F1-Score** | 0.335 | **0.745** | **+0.410 (+122% gain)** |
| **Missing Requirement Recall** | 100.0% | **100.0%** | 100% detection |
| **Missing Requirement Precision**| 30.0% | **55.4%** | **+25.4 pp (+84.7% gain)** |
| **Groundedness** | 100.0% | **100.0%** | 100% verified spatial evidence |
| **Latency per Document** | **0.341 s** | **0.587 s** | Real-time (~102 pages/min) |

---

## 4. Environment & Installation

### Requirements
- Python 3.9+ (tested on Python 3.13)
- Tesseract OCR (v5.x recommended)

### Python Package Installation
```bash
pip install opencv-python pytesseract pillow numpy matplotlib pandas python-pptx fpdf2 python-docx
```

### Tesseract Installation
- **Windows**: The pipeline automatically looks for Tesseract in `.\tesseract\tesseract.exe`, `C:\Program Files\Tesseract-OCR\tesseract.exe`, and local paths. If installed elsewhere, verify `pytesseract.pytesseract.tesseract_cmd` in `pipeline.py`.
- **Ubuntu/Debian**: `sudo apt install tesseract-ocr`
- **macOS**: `brew install tesseract`

---

## 5. How to Run the Project (2 Commands)

### Step 1: Generate the Synthetic Dataset
```bash
python generate_data.py
```
*Generates 100 degraded application forms with simulated omissions in `data/images/` and ground truth in `data/gt/`.*

### Step 2: Run Pipeline & Evaluation
```bash
python evaluate.py
```
*Executes both Baseline and Improved pipelines, benchmarks all metrics, and saves outputs to `results/`.*

---

## 6. Output Artifacts in `results/`
- `results/results.csv`: Complete quantitative comparison table.
- `results/fig_stages.png`: High-resolution visual grid showing all 7 DIP restoration stages on a sample document.
- `results/fig_compare.png`: Comparative bar chart (Extraction F1, Recall, Groundedness).
- `results/fig_evidence.png`: Sample verified application form with green bounding boxes drawn over detected evidence lines.
- `results/example_checklist.json`: Structured verification checklist declaring status (OK vs. MISSING), values, and spatial evidence coordinates.
- `results/failure_cases_improved.csv`: Exhaustive log of misclassifications for error analysis.

---


