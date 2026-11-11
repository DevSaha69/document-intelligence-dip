import glob, json, time, os, cv2, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pipeline import *

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
                if fld in gt and norm(ext[fld][0]) == norm(gt[fld]):
                    tp += 1
                else:
                    fp += 1
                    if fld in gt:
                        fn += 1
                    fails.append((os.path.basename(f), fld, gt.get(fld), ext[fld][0]))
            elif fld in gt:
                fn += 1
                fails.append((os.path.basename(f), fld, gt[fld], "NOT FOUND"))
        true_missing = set(REQ) - set(gt)
        pred_missing = set(REQ) - set(ext)
        mt += len(true_missing & pred_missing)
        mp += len(pred_missing)
        mtrue += len(true_missing)
        for fld, (v, (txt, box)) in ext.items():          # groundedness
            ok_items += 1
            if norm(v) in norm(txt) or (v == "attached" and "attach" in txt.lower()):
                grounded += 1
    P = tp/(tp+fp) if tp+fp else 0
    R = tp/(tp+fn) if tp+fn else 0
    F1 = 2*P*R/(P+R) if P+R else 0
    return {"Extraction_Precision": P, "Extraction_Recall": R, "Extraction_F1": F1,
            "Missing_Req_Recall": mt/mtrue if mtrue else 0,
            "Missing_Req_Precision": mt/mp if mp else 0,
            "Groundedness": grounded/ok_items if ok_items else 0,
            "Time_per_doc_s": (time.time()-t0)/len(files)}, fails

if __name__ == "__main__":
    if len(files) == 0:
        print("No image files found in data/images! Run generate_data.py first.")
        exit(1)
        
    print(f"Running evaluation on {len(files)} documents...")
    print("Evaluating Baseline pipeline...")
    rb, fb = run(baseline)
    print("Evaluating Improved pipeline...")
    ri, fi = run(improved)
    df = pd.DataFrame({"Baseline": rb, "Improved": ri}).round(3)
    print("\n--- Evaluation Results ---")
    print(df)
    df.to_csv("results/results.csv")
    pd.DataFrame(fi, columns=["image", "field", "truth", "predicted"]).to_csv("results/failure_cases_improved.csv", index=False)

    # Figure 1: intermediate stages on one image
    g = cv2.imread(files[0], 0)
    st, _ = improved(g)
    fig, ax = plt.subplots(2, 4, figsize=(16, 9))
    for a, (k, v) in zip(ax.ravel(), st.items()):
        a.imshow(v, cmap="gray")
        a.set_title(k)
        a.axis("off")
    ax.ravel()[-1].axis("off")
    plt.tight_layout()
    plt.savefig("results/fig_stages.png", dpi=120)
    plt.close()

    # Figure 2: baseline vs improved bar chart
    df.loc[["Extraction_F1", "Missing_Req_Recall", "Groundedness"]].plot.bar(figsize=(7, 4))
    plt.ylim(0, 1.05)
    plt.title("Baseline vs Improved")
    plt.tight_layout()
    plt.savefig("results/fig_compare.png", dpi=120)
    plt.close()

    # Figure 3: final output - checklist with evidence boxes on 1 image
    _, img = improved(g)
    ext = extract(ocr_lines(img))
    vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    for f, (v, (t, b)) in ext.items():
        cv2.rectangle(vis, (b[0], b[1]), (b[2], b[3]), (0, 160, 0), 2)
    cv2.imwrite("results/fig_evidence.png", vis)
    json.dump(build_checklist(ext), open("results/example_checklist.json", "w"), indent=2)
    print("\nAll artifacts and figures saved successfully to results/")

