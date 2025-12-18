import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from parser import process_folder

# -----------------------------
# Root Window
# -----------------------------
root = tk.Tk()
root.title("Credit Card PDF Parser")
root.geometry("1000x650")
root.configure(bg="#1e1e2f")
root.resizable(False, False)

# -----------------------------
# Style Configuration
# -----------------------------
style = ttk.Style()
style.theme_use("clam")

style.configure(
    "TButton",
    font=("Segoe UI", 11, "bold"),
    padding=10,
    background="#4CAF50",
    foreground="white"
)

style.map(
    "TButton",
    background=[("active", "#43a047")]
)

style.configure(
    "Header.TLabel",
    font=("Segoe UI", 18, "bold"),
    foreground="white",
    background="#1e1e2f"
)

style.configure(
    "Status.TLabel",
    font=("Segoe UI", 9),
    foreground="#bbbbbb",
    background="#1e1e2f"
)

# -----------------------------
# Header
# -----------------------------
header = ttk.Label(
    root,
    text="💳 Credit Card PDF Parser",
    style="Header.TLabel"
)
header.pack(pady=15)

# -----------------------------
# Main Frame
# -----------------------------
main_frame = tk.Frame(root, bg="#1e1e2f")
main_frame.pack(fill=tk.BOTH, expand=True, padx=15)

# -----------------------------
# Output Text Area
# -----------------------------
output_text = scrolledtext.ScrolledText(
    main_frame,
    width=120,
    height=28,
    font=("Consolas", 10),
    bg="#121212",
    fg="#e0e0e0",
    insertbackground="white",
    relief=tk.FLAT,
    borderwidth=5
)
output_text.pack(pady=10, fill=tk.BOTH, expand=True)

# -----------------------------
# Progress Bar
# -----------------------------
progress = ttk.Progressbar(
    root,
    orient="horizontal",
    length=400,
    mode="indeterminate"
)
progress.pack(pady=5)

# -----------------------------
# Status Bar
# -----------------------------
status_label = ttk.Label(
    root,
    text="Ready",
    style="Status.TLabel",
    anchor="w"
)
status_label.pack(fill=tk.X, padx=10, pady=5)

# -----------------------------
# Display Results
# -----------------------------
def display_results(results):
    output_text.delete(1.0, tk.END)
    for item in results:
        if "error" in item:
            output_text.insert(
                tk.END,
                f"❌ File: {item['file']}\nError: {item['error']}\n\n"
            )
        else:
            output_text.insert(
                tk.END,
                f"📄 File: {item['file']}\n"
                f"🏦 Bank: {item['bank']}\n"
                f"👤 Cardholder Name: {item['cardholder_name']}\n"
                f"💳 Card Last 4: {item['card_last_4']}\n"
                f"💰 Total Amount Due: {item['total_amount_due']}\n"
                f"📉 Minimum Amount Due: {item['minimum_amount_due']}\n"
                + "-" * 70 + "\n"
            )
    output_text.yview(tk.END)

# -----------------------------
# Folder Selection
# -----------------------------
def select_folder():
    folder_path = filedialog.askdirectory(title="Select Folder Containing PDFs")
    if not folder_path:
        return

    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, f"📂 Processing PDFs in:\n{folder_path}\n\n")

    status_label.config(text="Processing PDFs...")
    progress.start(10)
    root.update_idletasks()

    try:
        results = process_folder(folder_path, root)
        display_results(results)
        messagebox.showinfo(
            "Processing Complete",
            f"Processed {len(results)} PDF(s).\nResults saved in output.json"
        )
        status_label.config(text="Completed Successfully")
    except Exception as e:
        messagebox.showerror("Error", str(e))
        status_label.config(text="Error occurred")
    finally:
        progress.stop()

# -----------------------------
# Button Panel
# -----------------------------
button_frame = tk.Frame(root, bg="#1e1e2f")
button_frame.pack(pady=10)

process_btn = ttk.Button(
    button_frame,
    text="📁 Select Folder & Process PDFs",
    command=select_folder
)
process_btn.pack()

# -----------------------------
# Start GUI
# -----------------------------
root.mainloop()
