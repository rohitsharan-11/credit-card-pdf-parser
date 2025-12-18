import os
import re
import json
import glob
import pdfplumber
from tkinter.simpledialog import askstring

# -----------------------------
# Detect Bank
# -----------------------------
def detect_bank(text):
    t = text.lower()
    if "axis bank" in t:
        return "AXIS"
    elif "yes bank" in t:
        return "YES BANK"
    elif "indusind" in t:
        return "INDUSIND"
    elif "sbi" in t:
        return "SBI"
    elif "icici" in t:
        return "ICICI"
    elif "hdfc" in t:
        return "HDFC"
    else:
        return "UNKNOWN"

# -----------------------------
# Extract text from PDF (password-protected)
# -----------------------------
def extract_text(pdf_path, master_window, password=""):
    try:
        with pdfplumber.open(pdf_path, password=password) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                page_text = re.sub(r'\s+', ' ', page_text)
                text += page_text + "\n"
            return text.strip()
    except Exception:
        # Ask for password
        password = askstring("Password Required", f"Enter password for {os.path.basename(pdf_path)}:", parent=master_window)
        if not password:
            return None
        try:
            with pdfplumber.open(pdf_path, password=password) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    page_text = re.sub(r'\s+', ' ', page_text)
                    text += page_text + "\n"
                return text.strip()
        except:
            return None

# -----------------------------
# Extract Cardholder Name
# -----------------------------
def extract_cardholder_name(text, bank):
    name = ""
    if bank == "YES BANK":
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            # Skip lines with keywords / long sentences / numbers
            if not line or any(k in line.lower() for k in ["click", "email", "form", "address", "mobile", "overview", "statement", "cid"]):
                continue
            if any(c.isalpha() for c in line) and 2 < len(line) < 30:
                name = line
                break
    else:
        match = re.search(r"\b(MR|MRS|MS)\.?\s+([A-Z][A-Z\s]*)(?:\s+[A-Z]?)?\b", text, re.IGNORECASE)
        if match:
            name = match.group(2).strip()

    # Clean up roman numerals and extra spaces
    name = re.sub(r"\b(I|II|III|IV|V)\b", "", name, flags=re.IGNORECASE).strip()
    name = re.sub(r"\s{2,}", " ", name)
    return name

# -----------------------------
# Extract Card Last 4
# -----------------------------
def extract_card_last4(text):
    match = re.search(r"(?:X|x|\*|\s){8,16}(\d{4})", text)
    if match:
        return match.group(1)
    return ""

# -----------------------------
# Extract Amounts
# -----------------------------
def extract_total_due(text):
    match = re.search(
        r"(Total Amount Due|Total Due|Amount Due|Total Outstanding|Total Amount Payable)[^\d]*([\d,]+\.\d{2})",
        text, re.IGNORECASE
    )
    if match:
        return match.group(2).replace(",", "").strip()
    return ""

def extract_min_due(text):
    match = re.search(
        r"(Minimum Amount Due|Min Due|Minimum Payable)[^\d]*([\d,]+\.\d{2})",
        text, re.IGNORECASE
    )
    if match:
        return match.group(2).replace(",", "").strip()
    return ""

# -----------------------------
# Extract details from PDF
# -----------------------------
def extract_details(text, pdf_path):
    bank = detect_bank(text)
    data = {
        "file": os.path.basename(pdf_path),
        "bank": bank,
        "cardholder_name": extract_cardholder_name(text, bank),
        "card_last_4": extract_card_last4(text),
        "total_amount_due": extract_total_due(text),
        "minimum_amount_due": extract_min_due(text)
    }

    # Fallback: check tables if amounts are empty
    if not data["total_amount_due"] or not data["minimum_amount_due"]:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        for row in table:
                            row_text = ' '.join([str(cell) for cell in row if cell])
                            if not data["total_amount_due"]:
                                match = re.search(r"(Total Amount Due|Total Due|Amount Due|Total Outstanding|Total Amount Payable)[^\d]*([\d,]+\.\d{2})", row_text, re.IGNORECASE)
                                if match:
                                    data["total_amount_due"] = match.group(2).replace(',', '').strip()
                            if not data["minimum_amount_due"]:
                                match = re.search(r"(Minimum Amount Due|Min Due|Minimum Payable)[^\d]*([\d,]+\.\d{2})", row_text, re.IGNORECASE)
                                if match:
                                    data["minimum_amount_due"] = match.group(2).replace(',', '').strip()
        except:
            pass

    return data

# -----------------------------
# Process folder
# -----------------------------
def process_folder(folder_path, master_window):
    results = []

    for pdf_file in glob.glob(os.path.join(folder_path, "*.pdf")):
        text = extract_text(pdf_file, master_window)
        if not text or len(text) < 20:
            results.append({"file": os.path.basename(pdf_file), "error": "Could not read PDF or password missing"})
            continue
        details = extract_details(text, pdf_file)
        results.append(details)

    # Save JSON
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    return results
