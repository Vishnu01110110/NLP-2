import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import requests
import PyPDF2
import io
from urllib.parse import urlparse
import ssl

class PDFExtractorGUI:
    def __init__(self, master):
        self.master = master
        master.title("PDF Text Extractor")
        master.geometry("700x600")

        self.url_label = ttk.Label(master, text="Enter PDF URLs (one per line):")
        self.url_label.pack(pady=5)

        self.url_entry = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=80, height=5)
        self.url_entry.pack(pady=5)

        self.ssl_verify_var = tk.BooleanVar(value=True)
        self.ssl_verify_check = ttk.Checkbutton(master, text="Uncheck if error downloading PDFs", 
                                                variable=self.ssl_verify_var)
        self.ssl_verify_check.pack(pady=5)

        self.extract_button = ttk.Button(master, text="Extract Text", command=self.extract_pdfs)
        self.extract_button.pack(pady=5)

        self.save_button = ttk.Button(master, text="Save Content", command=self.save_content)
        self.save_button.pack(pady=5)

        self.content_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=80, height=25)
        self.content_area.pack(pady=10)

        self.status_label = ttk.Label(master, text="")
        self.status_label.pack(pady=5)

        self.extracted_content = {}

    def extract_pdfs(self):
        urls = self.url_entry.get("1.0", tk.END).strip().split("\n")
        self.extracted_content.clear()
        self.content_area.delete("1.0", tk.END)
        self.status_label.config(text="Extraction in progress...")
        self.master.update()

        verify = self.ssl_verify_var.get()

        for url in urls:
            if url.strip():
                try:
                    self.extract_pdf(url.strip(), verify)
                except Exception as e:
                    error_msg = f"Error extracting {url}: {str(e)}"
                    print(error_msg)
                    self.extracted_content[url] = f"EXTRACTION FAILED: {error_msg}"

        all_content = self.format_content()
        self.content_area.insert(tk.END, all_content)
        self.status_label.config(text=f"Extraction complete. Processed {len(self.extracted_content)} PDF(s).")

    def extract_pdf(self, url, verify):
        response = requests.get(url, verify=verify)
        response.raise_for_status()

        pdf_file = io.BytesIO(response.content)
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"

        self.extracted_content[url] = text
        print(f"Extracted: {url}")  # Progress indicator

    def format_content(self):
        formatted_content = ""
        for url, content in self.extracted_content.items():
            formatted_content += f"\n\n{'=' * 50}\n"
            formatted_content += f"PDF URL: {url}\n"
            formatted_content += f"{'=' * 50}\n\n"
            formatted_content += content
        return formatted_content

    def save_content(self):
        if not self.extracted_content:
            self.status_label.config(text="No content to save")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.format_content())
                self.status_label.config(text=f"Content saved to {file_path}")
            except IOError:
                self.status_label.config(text="Error saving file")

root = tk.Tk()
pdf_extractor_gui = PDFExtractorGUI(root)
root.mainloop()