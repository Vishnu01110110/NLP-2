import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse
import chardet
import urllib3


# Disable InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WebScraperGUI:
    def __init__(self, master):
        self.master = master
        master.title("Web Scraper with Consolidated Output")
        master.geometry("700x550")  

        self.url_label = ttk.Label(master, text="Enter URL:")
        self.url_label.pack(pady=5)

        self.url_entry = ttk.Entry(master, width=70)
        self.url_entry.pack(pady=5)

        self.subpage_var = tk.BooleanVar()
        self.subpage_check = ttk.Checkbutton(master, text="Scrape Subpages", variable=self.subpage_var)
        self.subpage_check.pack(pady=5)

        self.ignore_ssl_var = tk.BooleanVar(value=True)  
        self.ignore_ssl_check = ttk.Checkbutton(master, text="If issue scraping uncheck", variable=self.ignore_ssl_var)
        self.ignore_ssl_check.pack(pady=5)

        self.scrape_button = ttk.Button(master, text="Scrape", command=self.scrape_url)
        self.scrape_button.pack(pady=5)

        self.save_button = ttk.Button(master, text="Save Content", command=self.save_content)
        self.save_button.pack(pady=5)

        self.content_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=80, height=25)
        self.content_area.pack(pady=10)

        self.status_label = ttk.Label(master, text="")
        self.status_label.pack(pady=5)

        self.scraped_content = {}

    def scrape_url(self):
        url = self.url_entry.get()
        if not url:
            self.status_label.config(text="Please enter a URL")
            return

        self.scraped_content.clear()
        self.content_area.delete(1.0, tk.END)
        self.status_label.config(text="Scraping in progress...")
        self.master.update()

        try:
            self.scrape_page(url)
            if self.subpage_var.get():
                self.scrape_subpages(url)
            
            all_content = self.format_content()
            self.content_area.insert(tk.END, all_content)
            self.status_label.config(text=f"Scraping successful. Scraped {len(self.scraped_content)} page(s).")
        except requests.RequestException as e:
            self.status_label.config(text=f"Error: {str(e)}")

    def scrape_page(self, url):
        try:
            verify_ssl = not self.ignore_ssl_var.get()
            response = requests.get(url, timeout=10, verify=verify_ssl)
            response.raise_for_status()
            
            # Detect encoding
            encoding = chardet.detect(response.content)['encoding']
            
            if encoding is None:
                print(f"Warning: Unable to detect encoding for {url}. Skipping.")
                return
            
            # Decode content with detected encoding
            try:
                html_content = response.content.decode(encoding, errors='replace')
            except (LookupError, TypeError):
                print(f"Warning: Error decoding content from {url}. Skipping.")
                return
            
            soup = BeautifulSoup(html_content, 'html.parser')
            content = ' '.join([tag.get_text().strip() for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])])
            self.scraped_content[url] = content
            print(f"Scraped: {url}")  # Progress indicator
        except requests.RequestException as e:
            print(f"Error scraping {url}: {str(e)}")

    def scrape_subpages(self, base_url):
        base_domain = urlparse(base_url).netloc
        try:
            verify_ssl = not self.ignore_ssl_var.get()
            response = requests.get(base_url, timeout=10, verify=verify_ssl)  
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                subpage_url = urljoin(base_url, link['href'])
                if urlparse(subpage_url).netloc == base_domain and subpage_url not in self.scraped_content:
                    self.scrape_page(subpage_url)
        except requests.RequestException as e:
            print(f"Error fetching subpages from {base_url}: {str(e)}")

    def format_content(self):
        formatted_content = ""
        for url, content in self.scraped_content.items():
            formatted_content += f"\n\n{'=' * 50}\n"
            formatted_content += f"URL: {url}\n"
            formatted_content += f"{'=' * 50}\n\n"
            formatted_content += content
        return formatted_content

    def save_content(self):
        if not self.scraped_content:
            self.status_label.config(text="No content to save")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.format_content())
                self.status_label.config(text=f"Content saved to {file_path}")
                
                # Open the file for the user
                os.startfile(file_path)
            except IOError as e:
                self.status_label.config(text=f"Error saving file: {str(e)}")

root = tk.Tk()
scraper_gui = WebScraperGUI(root)
root.mainloop()