import os, sys, shutil, argparse

def package(student_name="Student", roll_no="RollNumber"):
    # Clean string for file names (alphanumeric and underscore)
    safe_name = "".join(c if c.isalnum() else "_" for c in student_name.strip())
    safe_roll = "".join(c if c.isalnum() else "_" for c in roll_no.strip())
    prefix = f"{safe_name}_{safe_roll}"
    
    out_dir = f"{prefix}_project"
    print(f"Creating submission package directory: {out_dir}")
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. generate_data.py
    shutil.copy("generate_data.py", os.path.join(out_dir, f"{prefix}_generate_data.py"))
    
    # 2. pipeline.py
    shutil.copy("pipeline.py", os.path.join(out_dir, f"{prefix}_pipeline.py"))
    
    # 3. evaluate.py with updated import
    with open("evaluate.py", "r", encoding="utf-8") as f:
        eval_content = f.read()
    eval_content = eval_content.replace("from pipeline import *", f"from {prefix}_pipeline import *")
    with open(os.path.join(out_dir, f"{prefix}_evaluate.py"), "w", encoding="utf-8") as f:
        f.write(eval_content)
        
    # 4. README.md
    shutil.copy("README.md", os.path.join(out_dir, f"{prefix}_README.md"))
    
    # 5. Generate customized PDF Report with real Name & Roll No
    try:
        from build_pdf_report import generate_pdf
        pdf_path = os.path.join(out_dir, f"{prefix}_Report.pdf")
        generate_pdf(pdf_path, student_name=student_name, roll_no=roll_no)
        print(f"Generated {pdf_path}")
    except Exception as e:
        print(f"Warning: could not build custom PDF: {e}")
        shutil.copy("Report.pdf", os.path.join(out_dir, f"{prefix}_Report.pdf"))
        
    # 6. Generate customized Word Report with real Name & Roll No
    try:
        from build_docx_report import generate_docx
        docx_path = os.path.join(out_dir, f"{prefix}_Report.docx")
        generate_docx(docx_path, student_name=student_name, roll_no=roll_no)
        print(f"Generated {docx_path}")
    except Exception as e:
        print(f"Warning: could not build custom docx: {e}")
        shutil.copy("Report.docx", os.path.join(out_dir, f"{prefix}_Report.docx"))

    # 7. Generate customized Presentation with real Name & Roll No
    try:
        from build_presentation import create_deck
        pptx_path = os.path.join(out_dir, f"{prefix}_Presentation.pptx")
        create_deck(pptx_path, student_name=student_name, roll_no=roll_no)
        print(f"Generated {pptx_path}")
    except Exception as e:
        print(f"Warning: could not build custom pptx: {e}")
        shutil.copy("Presentation.pptx", os.path.join(out_dir, f"{prefix}_Presentation.pptx"))

    # 8. Copy data and results folders
    if os.path.exists("data"):
        dst_data = os.path.join(out_dir, "data")
        if os.path.exists(dst_data): shutil.rmtree(dst_data)
        shutil.copytree("data", dst_data)
        
    if os.path.exists("results"):
        dst_res = os.path.join(out_dir, "results")
        if os.path.exists(dst_res): shutil.rmtree(dst_res)
        shutil.copytree("results", dst_res)
        
    # Copy tesseract folder if present in workspace so package is self-contained
    if os.path.exists("tesseract"):
        dst_tess = os.path.join(out_dir, "tesseract")
        if os.path.exists(dst_tess): shutil.rmtree(dst_tess)
        shutil.copytree("tesseract", dst_tess)

    print("\nSubmission package created successfully!")
    print(f"Directory: {os.path.abspath(out_dir)}")
    print("Contents:")
    for item in sorted(os.listdir(out_dir)):
        print(f"  - {item}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Package project for submission with Name_RollNumber_ prefix")
    parser.add_argument("--name", type=str, default="Student", help="Student Name")
    parser.add_argument("--roll", type=str, default="RollNumber", help="Roll Number")
    args = parser.parse_args()
    package(args.name, args.roll)

