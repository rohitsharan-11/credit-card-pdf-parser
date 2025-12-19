Credit Card PDF Parser

A Python GUI application to automatically extract credit card statement details from PDF files across multiple banks.

🔹 Features

Extracts key details from PDF credit card statements:

Bank Name

Cardholder Name

Last 4 Digits of Card

Total Amount Due

Minimum Amount Due

Supports password-protected PDFs

Processes multiple PDFs at once

User-friendly GUI with progress bar and output log

Saves results in output.json for easy use

🔹 Supported Banks

AXIS Bank

YES Bank

INDUSIND Bank

SBI

ICICI Bank

HDFC Bank

Unknown / Other banks (labeled as UNKNOWN)





🔹 Installation

Clone the repository:

git clone https://github.com/rohitsharan-11/credit-card-pdf-parser.git
cd credit-card-pdf-parser


Create a virtual environment (optional but recommended):

python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux / Mac


Install dependencies:

pip install -r requirements.txt


Dependencies: tkinter, pdfplumber

🔹 Usage

Run the application:

python app.py


Click 📁 Select Folder to choose a folder containing your PDF statements.

The application will process all PDFs and display the results in the GUI.

Results are also saved in output.json in the project folder.



🔹 Notes

For password-protected PDFs, the app will prompt you to enter the password.

If a PDF cannot be read or is missing required data, it will be logged as an error in the output.
