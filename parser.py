import os
import re
import json
import glob
import pdfplumber
from tkinter.simpledialog import askstring


def detect_bank(text: str) -> str:
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
    return "UNKNOWN"



def extract_text(pdf_path, master_window=None, password=""):
    try:
        with pdfplumber.open(pdf_path, password=password) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                page_text = re.sub(r"\s+", " ", page_text)
                text += page_text + "\n"
            return text.strip()

    except Exception:
        try:
            password = askstring(
                "Password Required",
                f"Enter password for {os.path.basename(pdf_path)}:",
                parent=master_window
            )
        except Exception as e:
            print("Password dialog failed:", e)
            return None

        if not password:
            return None

        try:
            with pdfplumber.open(pdf_path, password=password) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    page_text = re.sub(r"\s+", " ", page_text)
                    text += page_text + "\n"
                return text.strip()
        except Exception as e:
            print("Wrong password or unreadable PDF:", e)
            return None



def extract_cardholder_name(text, bank):
    name = ""

    if bank == "YES BANK":
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue
            if any(
                k in line.lower()
                for k in ["email", "address", "mobile", "statement", "overview"]
            ):
                continue
            if any(c.isalpha() for c in line) and 2 < len(line) < 30:
                name = line
                break
    else:
        match = re.search(
            r"\b(MR|MRS|MS)\.?\s+([A-Z][A-Z\s]+)\b",
            text,
            re.IGNORECASE
        )
        if match:
            name = match.group(2).strip()

    name = re.sub(r"\b(I|II|III|IV|V)\b", "", name)
    name = re.sub(r"\s{2,}", " ", name).strip()
    return name


def extract_card_last4_digits(text):
    match = re.search(r"(?:X|\*|\s){6,16}(\d{4})", text)
    return match.group(1) if match else ""


def extract_total_due(text):
    match = re.search(
        r"(Total Amount Due|Total Due|Amount Due|Total Outstanding|Total Amount Payable)[^\d]*([\d,]+\.\d{2})",
        text,
        re.IGNORECASE
    )
    return match.group(2).replace(",", "") if match else ""


def extract_minimum_due(text):
    match = re.search(
        r"(Minimum Amount Due|Min Due|Minimum Payable)[^\d]*([\d,]+\.\d{2})",
        text,
        re.IGNORECASE
    )
    return match.group(2).replace(",", "") if match else ""



def extract_details(text, pdf_path):
    bank = detect_bank(text)

    data = {
        "file": os.path.basename(pdf_path),
        "bank": bank,
        "cardholder_name": extract_cardholder_name(text, bank),
        "card_last4_digits": extract_card_last4_digits(text),
        "total_amount_due": extract_total_due(text),
        "minimum_amount_due": extract_minimum_due(text)
    }

    if bank == "INDUSIND":
        data["minimum_amount_due"] = "NA"


    if not data["total_amount_due"] or (
        bank != "INDUSIND" and not data["minimum_amount_due"]
    ):
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables() or []
                    for table in tables:
                        for row in table:
                            row_text = " ".join(str(c) for c in row if c)

                            if not data["total_amount_due"]:
                                m = re.search(
                                    r"(Total Amount Due|Total Due|Amount Due)[^\d]*([\d,]+\.\d{2})",
                                    row_text,
                                    re.IGNORECASE
                                )
                                if m:
                                    data["total_amount_due"] = m.group(2).replace(",", "")

                            if bank != "INDUSIND" and not data["minimum_amount_due"]:
                                m = re.search(
                                    r"(Minimum Amount Due|Min Due)[^\d]*([\d,]+\.\d{2})",
                                    row_text,
                                    re.IGNORECASE
                                )
                                if m:
                                    data["minimum_amount_due"] = m.group(2).replace(",", "")
        except Exception as e:
            print("Table extraction error:", e)

    return data


# -------------------------------------------------
# Process Folder & Save JSON
# -------------------------------------------------
def process_folder(folder_path, master_window=None):
    results = []

    for pdf_file in glob.glob(os.path.join(folder_path, "*.pdf")):
        text = extract_text(pdf_file, master_window)

        if not text or len(text) < 20:
            results.append({
                "file": os.path.basename(pdf_file),
                "error": "Could not read PDF or password missing"
            })
            continue

        results.append(extract_details(text, pdf_file))

    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, "output.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    print("JSON saved at:", output_path)
    return results
