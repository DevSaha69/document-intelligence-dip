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
    a = np.clip(0, 255, a).astype(np.uint8) if False else np.clip(a, 0, 255).astype(np.uint8)
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

