# HSR-AIML-042 — Document Intelligence for Application Readiness & Missing-Requirement Detection
### Simple, working plan (no fancy stuff)

**Idea in one line:** Take scanned/photographed application forms (noisy, skewed, badly lit) → clean them with image processing → OCR → extract fields → compare with the university requirement list → output a checklist saying what is **OK** and what is **MISSING**, with the image line/box as evidence.

**Baseline vs Improved (this is what the rubric wants):**
- **Baseline** = grayscale → OCR directly
- **Improved** = illumination correction → denoise → CLAHE (contrast) → Otsu threshold → deskew → morphology/region cleanup → OCR

You will show the improved one gives higher Extraction F1 and Requirement Recall.

---

## 0. Time plan (about 2 days)
| Step | Time |
|---|---|
| Install + run code below | 1 hr |
| Generate dataset + run evaluation | 1 hr |
| Take screenshots/figures | 1 hr |
| 4-page IEEE paper | 3-4 hrs |
| README + file renaming + PPT | 2 hrs |

---

## 1. Setup
```bash
pip install opencv-python pytesseract pillow numpy matplotlib pandas
```
Also install the **Tesseract OCR program** (pytesseract needs it):
- Windows: install from "UB Mannheim Tesseract", then add at top of `pipeline.py`:
  `pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"`
- Ubuntu: `sudo apt install tesseract-ocr`
- Mac: `brew install tesseract`

## 2. Folder structure
```
Name_RollNumber_project/
  Name_RollNumber_generate_data.py
  Name_RollNumber_pipeline.py
  Name_RollNumber_evaluate.py
  Name_RollNumber_README.md
  Name_RollNumber_Report.pdf        (4-page IEEE)
  Name_RollNumber_Presentation.pptx
  data/ (auto-created)  results/ (auto-created)
```
> Every uploaded file must start with `Name_RollNumber_`. If you rename the .py files, change the import line in evaluate.py (`from Name_RollNumber_pipeline import *`) — **or** keep the code names as `generate_data.py`, `pipeline.py`, `evaluate.py` while testing and rename only at the end (fix the import then).

---

## 3. Dataset (synthetic, as the topic allows)
We generate 100 fake application forms with PIL. Each has up to 7 fields; each field is randomly **omitted ~25%** of the time (these are the "missing requirements"). Then we degrade the image (uneven lighting, low contrast, noise, blur, rotation) to simulate phone scans. Ground-truth JSON is saved for each image.

### `generate_data.py`
```python
import random, json, os, cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont
random.seed(42); np.random.seed(42)
os.makedirs("data/images", exist_ok=True); os.makedirs("data/gt", exist_ok=True)

FIRST = ["Aarav","Priya","Rohan","Sneha","Karthik","Ananya","Vikram","Meera","Arjun","Divya"]
LAST  = ["Sharma","Reddy","Iyer","Patel","Nair","Gupta","Rao","Menon","Singh","Das"]

def get_font(size):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "C:/Windows/Fonts/arial.ttf", "/Library/Fonts/Arial.ttf"]:
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def make_gt():
    gt = {
      "name": f"{random.choice(FIRST)} {random.choice(LAST)}",
      "passport": random.choice("ABCKLMNP") + str(random.randint(1000000, 9999999)),
      "dob": f"{random.randint(1,28):02d}/{random.randint(1,12):02d}/{random.randint(1995,2004)}",
      "email": f"user{random.randint(100,999)}@gmail.com",
      "ielts": f"{random.choice([5.5,6.0,6.5,7.0,7.5,8.0])}",
      "sop": "attached", "transcript": "attached"}
    return {k: v for k, v in gt.items() if random.random() > 0.25}   # drop ~25%

LABEL = {"name": "Full Name: {}", "passport": "Passport No: {}", "dob": "Date of Birth: {}",
         "email": "Email: {}", "ielts": "IELTS Score: {}",
         "sop": "Statement of Purpose: Attached", "transcript": "Academic Transcript: Attached"}

def draw_doc(gt):
    img = Image.new("L", (850, 1100), 255); d = ImageDraw.Draw(img)
    d.text((250, 60), "APPLICATION FORM", fill=0, font=get_font(40))
    y = 180
    for k in LABEL:
        if k in gt:
            d.text((80, y), LABEL[k].format(gt[k]), fill=0, font=get_font(30))
        y += 90
    return np.array(img)

def degrade(a):
    a = a.astype(np.float32)
    h, w = a.shape
    # low contrast
    a = 110 + a * 0.45
    # uneven illumination (gradient shadow)
    grad = np.tile(np.linspace(random.uniform(0.5, 0.8), 1.0, w), (h, 1))
    if random.random() < 0.5: grad = grad[:, ::-1]
    a = a * grad
    # noise
    a += np.random.normal(0, random.uniform(8, 20), a.shape)
    a = np.clip(a, 0, 255).astype(np.uint8)
    # salt & pepper
    m = np.random.rand(h, w)
    a[m < 0.004] = 0; a[m > 0.996] = 255
    # blur + rotation
    a = cv2.GaussianBlur(a, (3, 3), 0)
    M = cv2.getRotationMatrix2D((w/2, h/2), random.uniform(-3, 3), 1)
    return cv2.warpAffine(a, M, (w, h), borderValue=int(a.mean()))

for i in range(100):
    gt = make_gt()
    cv2.imwrite(f"data/images/doc_{i:03d}.png", degrade(draw_doc(gt)))
    json.dump(gt, open(f"data/gt/doc_{i:03d}.json", "w"))
print("done: 100 documents")
```

### `data/requirements.json` (create this file by hand — it is the "university requirement page")
```json
{
  "name": "Applicant full name",
  "passport": "Valid passport number",
  "dob": "Date of birth",
  "email": "Contact email",
  "ielts": "English test (IELTS) score",
  "sop": "Statement of Purpose",
  "transcript": "Academic transcript"
}
```

---

## 4. Pipeline (baseline + improved + extraction + checklist)

### `pipeline.py`
```python
import cv2, re, json, numpy as np, pytesseract
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Windows

REQ = json.load(open("data/requirements.json"))

# ---------- DIP: preprocessing ----------
def baseline(gray):
    return {"gray": gray}, gray

def deskew(bw):
    small = cv2.resize(bw, None, fx=0.5, fy=0.5)
    inv = 255 - small
    best, best_a = -1, 0
    for a in np.arange(-5, 5.01, 0.5):                 # projection-profile method
        M = cv2.getRotationMatrix2D((small.shape[1]/2, small.shape[0]/2), a, 1)
        r = cv2.warpAffine(inv, M, (small.shape[1], small.shape[0]))
        s = np.var(r.sum(axis=1))
        if s > best: best, best_a = s, a
    M = cv2.getRotationMatrix2D((bw.shape[1]/2, bw.shape[0]/2), best_a, 1)
    return cv2.warpAffine(bw, M, (bw.shape[1], bw.shape[0]), flags=cv2.INTER_CUBIC, borderValue=255)

def improved(gray):
    st = {"1_gray": gray}
    # illumination correction: estimate background by morphological closing, divide it out
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41))
    bg = cv2.GaussianBlur(cv2.morphologyEx(gray, cv2.MORPH_CLOSE, k), (0, 0), 15)
    norm = cv2.divide(gray, bg, scale=255); st["2_illum_corrected"] = norm
    den = cv2.medianBlur(norm, 3); st["3_denoised"] = den                 # filtering
    cl = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(den)   # contrast
    st["4_clahe"] = cl
    _, bw = cv2.threshold(cl, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # thresholding
    st["5_otsu"] = bw
    bw = deskew(bw); st["6_deskewed"] = bw
    inv = 255 - bw                                                          # region analysis
    n, lab, stats, _ = cv2.connectedComponentsWithStats(inv)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] < 12: inv[lab == i] = 0              # remove specks
    inv = cv2.morphologyEx(inv, cv2.MORPH_CLOSE, np.ones((2, 2), np.uint8)) # repair strokes
    out = 255 - inv; st["7_morph_clean"] = out
    return st, out

# ---------- OCR with line boxes (for evidence) ----------
def ocr_lines(img):
    d = pytesseract.image_to_data(img, config="--psm 6", output_type=pytesseract.Output.DICT)
    lines = {}
    for i, t in enumerate(d["text"]):
        if not t.strip(): continue
        key = (d["block_num"][i], d["par_num"][i], d["line_num"][i])
        x, y, w, h = d["left"][i], d["top"][i], d["width"][i], d["height"][i]
        L = lines.setdefault(key, {"w": [], "x0": x, "y0": y, "x1": x+w, "y1": y+h})
        L["w"].append(t)
        L["x0"] = min(L["x0"], x); L["y0"] = min(L["y0"], y)
        L["x1"] = max(L["x1"], x+w); L["y1"] = max(L["y1"], y+h)
    return [(" ".join(L["w"]), (L["x0"], L["y0"], L["x1"], L["y1"])) for L in lines.values()]

# ---------- Field extraction (regex "NER") ----------
PAT = {
 "name":       r"name\W*([A-Za-z][A-Za-z .'-]+)",
 "passport":   r"passport\D*?([A-Za-z]\d{7})",
 "dob":        r"birth\W*(\d{2}/\d{2}/\d{4})",
 "email":      r"([\w.\-]+@[\w.\-]+\.[a-z]+)",
 "ielts":      r"ielts\D*?(\d\.\d)",
 "sop":        r"(statement.*attach)",
 "transcript": r"(transcript.*attach)"}

def extract(lines):
    out = {}
    for f, p in PAT.items():
        for text, box in lines:
            m = re.search(p, text, re.I)
            if m:
                v = "attached" if f in ("sop", "transcript") else m.group(1).strip()
                out[f] = (v, (text, box)); break
    return out

# ---------- Requirement checklist with evidence ----------
def build_checklist(ext):
    items = []
    for f, desc in REQ.items():
        if f in ext:
            items.append({"requirement": desc, "status": "OK", "value": ext[f][0],
                          "evidence_text": ext[f][1][0], "evidence_box": ext[f][1][1]})
        else:
            items.append({"requirement": desc, "status": "MISSING", "value": None,
                          "evidence_text": None, "evidence_box": None})
    return items

def norm(s): return re.sub(r"\s+", "", str(s)).lower()
```

---

## 5. Evaluation, figures, results

### `evaluate.py`
```python
import glob, json, time, os, cv2, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pipeline import *            # rename to Name_RollNumber_pipeline if you renamed the file

os.makedirs("results", exist_ok=True)
files = sorted(glob.glob("data/images/*.png"))

def run(method):
    tp = fp = fn = 0; mt = mp = mtrue = 0; grounded = ok_items = 0
    fails = []; t0 = time.time()
    for f in files:
        gray = cv2.imread(f, 0)
        gt = json.load(open(f.replace("images", "gt").replace(".png", ".json")))
        _, img = method(gray)
        ext = extract(ocr_lines(img))
        for fld in REQ:
            if fld in ext:
                if fld in gt and norm(ext[fld][0]) == norm(gt[fld]): tp += 1
                else:
                    fp += 1
                    if fld in gt: fn += 1
                    fails.append((os.path.basename(f), fld, gt.get(fld), ext[fld][0]))
            elif fld in gt:
                fn += 1; fails.append((os.path.basename(f), fld, gt[fld], "NOT FOUND"))
        true_missing = set(REQ) - set(gt); pred_missing = set(REQ) - set(ext)
        mt += len(true_missing & pred_missing); mp += len(pred_missing); mtrue += len(true_missing)
        for fld, (v, (txt, box)) in ext.items():          # groundedness
            ok_items += 1
            if norm(v) in norm(txt) or (v == "attached" and "attach" in txt.lower()): grounded += 1
    P = tp/(tp+fp) if tp+fp else 0; R = tp/(tp+fn) if tp+fn else 0
    F1 = 2*P*R/(P+R) if P+R else 0
    return {"Extraction_Precision": P, "Extraction_Recall": R, "Extraction_F1": F1,
            "Missing_Req_Recall": mt/mtrue if mtrue else 0,
            "Missing_Req_Precision": mt/mp if mp else 0,
            "Groundedness": grounded/ok_items if ok_items else 0,
            "Time_per_doc_s": (time.time()-t0)/len(files)}, fails

rb, fb = run(baseline); ri, fi = run(improved)
df = pd.DataFrame({"Baseline": rb, "Improved": ri}).round(3)
print(df); df.to_csv("results/results.csv")
pd.DataFrame(fi, columns=["image", "field", "truth", "predicted"]).to_csv("results/failure_cases_improved.csv", index=False)

# Figure 1: intermediate stages on one image
g = cv2.imread(files[0], 0); st, _ = improved(g)
fig, ax = plt.subplots(2, 4, figsize=(16, 9))
for a, (k, v) in zip(ax.ravel(), st.items()): a.imshow(v, cmap="gray"); a.set_title(k); a.axis("off")
ax.ravel()[-1].axis("off"); plt.tight_layout(); plt.savefig("results/fig_stages.png", dpi=120); plt.close()

# Figure 2: baseline vs improved bar chart
df.loc[["Extraction_F1", "Missing_Req_Recall", "Groundedness"]].plot.bar(figsize=(7, 4))
plt.ylim(0, 1.05); plt.title("Baseline vs Improved"); plt.tight_layout()
plt.savefig("results/fig_compare.png", dpi=120); plt.close()

# Figure 3: final output - checklist with evidence boxes on 1 image
_, img = improved(g); ext = extract(ocr_lines(img)); vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
for f, (v, (t, b)) in ext.items(): cv2.rectangle(vis, b[:2], b[2:], (0, 160, 0), 2)
cv2.imwrite("results/fig_evidence.png", vis)
json.dump(build_checklist(ext), open("results/example_checklist.json", "w"), indent=2)
print("Saved to results/")
```

### Run order
```bash
python generate_data.py
python evaluate.py
```
Outputs (use these in report/PPT): `results/results.csv`, `fig_stages.png`, `fig_compare.png`, `fig_evidence.png`, `example_checklist.json`, `failure_cases_improved.csv`.

**Troubleshooting:** if everything scores ~0 → Tesseract not found (set `tesseract_cmd`). If improved < baseline, tweak: CLAHE `clipLimit` 1.0–3.0, kernel size 41→61, or remove the 2×2 closing. Tuning a little is normal; just report honest numbers. If baseline already scores ~1.0, make the degradation harsher in `generate_data.py` (more noise, lower contrast `0.45→0.3`, darker gradient).

---

## 6. What to write — the 4-page IEEE paper (2-column, separate PDF)
Use the IEEE Conference template (Word or Overleaf). Sections:

1. **Abstract + Keywords** (150 words)
2. **Introduction / Problem statement** — students submit incomplete applications (Leap Scholar–style study-abroad use case); manual checking is slow; scanned docs are low quality.
3. **State of the art (short)** — Tesseract OCR; Otsu / CLAHE / adaptive thresholding; LayoutLM / Donut / TrOCR for document understanding; RAG for grounded checklists. Cite 5–8 references.
4. **Dataset** — 100 synthetic application forms, 7 fields, ~25% randomly omitted, degraded with illumination, noise, blur, rotation. Ground truth JSON. (State clearly it's synthetic and self-generated.)
5. **Methodology** — block diagram + pseudocode (below).
6. **Novelty / USP using DIP** — missing-requirement detection depends on OCR quality; DIP (illumination correction + CLAHE + Otsu + deskew + morphology/region cleanup) makes OCR reliable and each checklist item carries a bounding-box as visual evidence.
7. **Results** — table (baseline vs improved), fig_stages, fig_compare, fig_evidence.
8. **Failure cases & limitations** — pick 2–3 rows from `failure_cases_improved.csv` (e.g., "0" read as "O" in passport number; very dark shadow causing broken strokes). Limitations: synthetic data, one template, regex extraction instead of NER model, no real RAG over long pages.
9. **Conclusion & future work** — real scans, LayoutLM, full RAG with embeddings.
10. **References**

### Block diagram (draw in PPT/draw.io)
```
Input scanned form → [DIP] Grayscale → [DIP] Illumination correction (morph. closing) 
→ [DIP] Median denoise → [DIP] CLAHE → [DIP] Otsu threshold → [DIP] Deskew 
→ [DIP] Region analysis + morphology cleanup → OCR (Tesseract, line boxes) 
→ Field extraction (regex NER) → Compare with requirements.json 
→ Checklist (OK / MISSING + evidence box) → Evaluation (F1, recall, groundedness)
```
Mark the [DIP] boxes in a different colour.

### Pseudocode
```
for each document image I:
    G = grayscale(I)
    B = closing(G, ellipse 41x41); B = gaussian(B)
    N = G / B * 255                  # remove uneven lighting
    D = median(N, 3)
    C = CLAHE(D)
    T = Otsu(C)
    T = rotate(T, angle maximizing row-projection variance)
    remove connected components with area < 12; closing 2x2
    lines = Tesseract(T) -> text + bounding box
    for each required field f:
        find line matching regex(f); value, box = match
    checklist = {f: OK(value, box) or MISSING}
evaluate against ground truth
```

### Metrics (explain in paper)
- **Extraction F1** — field value exactly matches ground truth (precision/recall/F1).
- **Requirement (missing) recall** — fraction of truly missing requirements that the system flagged.
- **Groundedness** — fraction of OK items whose evidence line actually contains the extracted value.
- Execution time per document.

---

## 7. Final checklist before submitting
- [ ] All files named `Name_RollNumber_*`
- [ ] Code runs from scratch with the 2 commands
- [ ] README: what it is, install (Tesseract!), run commands, dataset description, folder structure
- [ ] 4-page IEEE PDF uploaded separately
- [ ] PPT: problem → dataset → block diagram → intermediate images → baseline vs improved table → success + failure cases → limitations
- [ ] If 2 students: split clearly (e.g., one = dataset + preprocessing, other = OCR/extraction/evaluation) but **both must understand the whole pipeline**
- [ ] Demo: run `evaluate.py`, show `fig_stages.png`, `fig_evidence.png`, and the results table

## 8. References you can cite
1. R. Smith, "An Overview of the Tesseract OCR Engine," ICDAR, 2007.
2. N. Otsu, "A Threshold Selection Method from Gray-Level Histograms," IEEE Trans. SMC, 1979.
3. K. Zuiderveld, "Contrast Limited Adaptive Histogram Equalization," Graphics Gems IV, 1994.
4. Y. Xu et al., "LayoutLM: Pre-training of Text and Layout for Document Image Understanding," KDD, 2020.
5. P. Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," NeurIPS, 2020.
6. G. Bradski, "The OpenCV Library," Dr. Dobb's Journal, 2000.
7. R. Gonzalez and R. Woods, *Digital Image Processing*, 4th ed., Pearson, 2018.
