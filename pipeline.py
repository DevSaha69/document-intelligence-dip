import os, shutil, cv2, re, json, numpy as np, pytesseract

# Configure Tesseract path
_DIR = os.path.dirname(os.path.abspath(__file__))
TESSERACT_CANDIDATES = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    os.path.join(_DIR, "tesseract", "tesseract.exe"),
    r"C:\Users\HP\Tesseract-OCR\tesseract.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
]
for cand in TESSERACT_CANDIDATES:
    if os.path.exists(cand):
        pytesseract.pytesseract.tesseract_cmd = cand
        tessdata_dir = os.path.join(os.path.dirname(cand), "tessdata")
        if os.path.exists(tessdata_dir):
            os.environ["TESSDATA_PREFIX"] = tessdata_dir
        break
else:
    which_tess = shutil.which("tesseract")
    if which_tess:
        pytesseract.pytesseract.tesseract_cmd = which_tess

REQ = json.load(open("data/requirements.json"))

# ---------- DIP: preprocessing ----------
def baseline(gray):
    return {"gray": gray}, gray

def deskew(bw):
    small = cv2.resize(bw, None, fx=0.5, fy=0.5)
    inv = 255 - small
    best, best_a = -1, 0
    for a in np.arange(-5, 5.01, 0.5):                 # projection-profile method
        M = cv2.getRotationMatrix2D((small.shape[1]/2, small.shape[0]/2), float(a), 1.0)
        r = cv2.warpAffine(inv, M, (small.shape[1], small.shape[0]))
        s = np.var(r.sum(axis=1))
        if s > best: best, best_a = s, a
    M = cv2.getRotationMatrix2D((bw.shape[1]/2, bw.shape[0]/2), float(best_a), 1.0)
    return cv2.warpAffine(bw, M, (bw.shape[1], bw.shape[0]), flags=cv2.INTER_CUBIC, borderValue=255)

def improved(gray):
    st = {"1_gray": gray}
    # illumination correction: estimate background by morphological closing, divide it out
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (51, 51))
    bg = cv2.GaussianBlur(cv2.morphologyEx(gray, cv2.MORPH_CLOSE, k), (0, 0), 15)
    norm_img = cv2.divide(gray, bg, scale=255)
    st["2_illum_corrected"] = norm_img
    den = cv2.medianBlur(norm_img, 3)                  # filtering
    st["3_denoised"] = den
    cl = cv2.createCLAHE(clipLimit=1.0, tileGridSize=(4, 4)).apply(den)   # contrast
    st["4_clahe"] = cl
    
    # Interior Otsu thresholding: avoids boundary skew
    th, _ = cv2.threshold(cl[40:-40, 40:-40], 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    th = min(th, 185.0)
    _, bw = cv2.threshold(cl, th, 255, cv2.THRESH_BINARY)
    # Clear outer border padding to eliminate rotation/warp artifacts
    bw[:35, :] = 255; bw[-35:, :] = 255; bw[:, :35] = 255; bw[:, -35:] = 255
    st["5_otsu"] = bw
    
    bw = deskew(bw)
    st["6_deskewed"] = bw
    inv = 255 - bw                                                          # region analysis
    n, lab, stats, _ = cv2.connectedComponentsWithStats(inv)
    h_img, w_img = bw.shape[:2]
    for i in range(1, n):
        area = stats[i, cv2.CC_STAT_AREA]
        x, y, w_b, h_b = stats[i, :4]
        # Remove small specks (< 15 px) and boundary-touching large artifacts
        if area < 15 or ((x <= 5 or y <= 5 or x + w_b >= w_img - 5 or y + h_b >= h_img - 5) and (w_b > w_img * 0.4 or h_b > h_img * 0.4)):
            inv[lab == i] = 0
    inv = cv2.morphologyEx(inv, cv2.MORPH_CLOSE, np.ones((2, 2), np.uint8)) # repair strokes
    out = 255 - inv
    st["7_morph_clean"] = out
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
        L["x0"] = min(L["x0"], x)
        L["y0"] = min(L["y0"], y)
        L["x1"] = max(L["x1"], x+w)
        L["y1"] = max(L["y1"], y+h)
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
                out[f] = (v, (text, box))
                break
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
