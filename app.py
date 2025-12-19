import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from parser import process_folder


root = tk.Tk()
root.title("Credit Card PDF Parser")
root.geometry("1200x720")
root.minsize(1100, 650)
root.configure(bg="#0f1220")

style = ttk.Style()
style.theme_use("clam")

PRIMARY = "#6c63ff"
BG_DARK = "#0f1220"
BG_PANEL = "#161a2b"
FG_TEXT = "#e6e6eb"
FG_MUTED = "#9aa0b4"
SUCCESS = "#4caf50"
ERROR = "#f44336"

style.configure("TFrame", background=BG_DARK)
style.configure("Panel.TFrame", background=BG_PANEL)

style.configure(
    "Header.TLabel",
    font=("Segoe UI", 20, "bold"),
    foreground=FG_TEXT,
    background=BG_DARK
)

style.configure(
    "SubHeader.TLabel",
    font=("Segoe UI", 11),
    foreground=FG_MUTED,
    background=BG_DARK
)

style.configure(
    "Sidebar.TButton",
    font=("Segoe UI", 11, "bold"),
    padding=14,
    background=PRIMARY,
    foreground="white"
)

style.map(
    "Sidebar.TButton",
    background=[("active", "#5a52e0")]
)

style.configure(
    "Status.TLabel",
    font=("Segoe UI", 9),
    foreground=FG_MUTED,
    background=BG_PANEL
)



root.columnconfigure(1, weight=1)
root.rowconfigure(0, weight=1)



sidebar = ttk.Frame(root, width=260, style="Panel.TFrame")
sidebar.grid(row=0, column=0, sticky="ns")
sidebar.grid_propagate(False)

ttk.Label(
    sidebar,
    text="💳 PDF Parser",
    font=("Segoe UI", 18, "bold"),
    foreground=FG_TEXT,
    background=BG_PANEL
).pack(pady=(30, 5))

ttk.Label(
    sidebar,
    text="Extract credit card\nstatement details",
    font=("Segoe UI", 10),
    foreground=FG_MUTED,
    background=BG_PANEL,
    justify="center"
).pack(pady=(0, 30))

process_btn = ttk.Button(
    sidebar,
    text="📁 Select Folder",
    style="Sidebar.TButton"
)
process_btn.pack(fill="x", padx=25)

ttk.Label(
    sidebar,
    text="Supported:\n• PDF Statements\n• Multiple Banks",
    font=("Segoe UI", 9),
    foreground=FG_MUTED,
    background=BG_PANEL,
    justify="left"
).pack(side="bottom", pady=20, padx=20)



content = ttk.Frame(root, padding=20)
content.grid(row=0, column=1, sticky="nsew")
content.columnconfigure(0, weight=1)
content.rowconfigure(2, weight=1)

ttk.Label(
    content,
    text="Credit Card PDF Parser",
    style="Header.TLabel"
).grid(row=0, column=0, sticky="w")

ttk.Label(
    content,
    text="Select a folder to extract statement details automatically",
    style="SubHeader.TLabel"
).grid(row=1, column=0, sticky="w", pady=(0, 10))


output_frame = ttk.Frame(content, style="Panel.TFrame", padding=10)
output_frame.grid(row=2, column=0, sticky="nsew")
output_frame.columnconfigure(0, weight=1)
output_frame.rowconfigure(0, weight=1)

output_text = ScrolledText(
    output_frame,
    font=("Consolas", 10),
    bg="#0b0e19",
    fg=FG_TEXT,
    insertbackground="white",
    relief=tk.FLAT,
    wrap=tk.WORD
)
output_text.grid(row=0, column=0, sticky="nsew")

output_text.tag_config("error", foreground=ERROR)
output_text.tag_config("header", foreground=PRIMARY, font=("Consolas", 11, "bold"))



footer = ttk.Frame(root, style="Panel.TFrame")
footer.grid(row=1, column=0, columnspan=2, sticky="ew")
footer.columnconfigure(1, weight=1)

progress = ttk.Progressbar(
    footer,
    orient="horizontal",
    mode="indeterminate",
    length=200
)
progress.grid(row=0, column=0, padx=15, pady=8)

status_label = ttk.Label(
    footer,
    text="Ready",
    style="Status.TLabel"
)
status_label.grid(row=0, column=1, sticky="w")


def log(text, tag=None):
    output_text.insert(tk.END, text + "\n", tag)
    output_text.yview(tk.END)


def display_results(results):
    output_text.delete(1.0, tk.END)

    for item in results:
        if "error" in item:
            log(f"❌ {item['file']}", "error")
            log(f"   {item['error']}\n", "error")
        else:
            log(f"📄 {item['file']}", "header")
            log(f"🏦 Bank: {item.get('bank', '')}")
            log(f"👤 Cardholder: {item.get('cardholder_name', '')}")
            log(f"💳 Last 4 Digits: {item.get('card_last4_digits', '')}")
            log(f"💰 Total Due: {item.get('total_amount_due', '')}")
            log(f"📉 Minimum Due: {item.get('minimum_amount_due', '')}\n")

    status_label.config(text="Completed Successfully")



def select_folder():
    folder = filedialog.askdirectory()
    if not folder:
        return

    output_text.delete(1.0, tk.END)
    log(f"📂 Processing folder:\n{folder}\n", "header")

    status_label.config(text="Processing PDFs...")
    progress.start(10)
    root.update_idletasks()

    try:
        results = process_folder(folder, root)
        display_results(results)
        messagebox.showinfo(
            "Processing Complete",
            f"Processed {len(results)} PDF(s).\nResults saved to output.json"
        )
    except Exception as e:
        messagebox.showerror("Error", str(e))
        status_label.config(text="Error occurred")
    finally:
        progress.stop()


process_btn.config(command=select_folder)


root.mainloop()
