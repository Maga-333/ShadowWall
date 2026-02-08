import tkinter as tk
import threading
import customtkinter as ctk
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk
from realtime_monitor import analyze_link  # Adjust path if needed

ctk.set_appearance_mode("dark")  # Overall dark mode
ctk.set_default_color_theme("blue")

# ================= CUTE & PROFESSIONAL GUI ================= #
class ShadowWallGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🛡️ ShadowWall - Live Link Analyzer")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        self.cute_font = ("Comic Sans MS", 14)
        self.is_scanning = False
        # Default colors for tags
        self.colors = {
            "safe": "green",
            "danger": "red",
            "info": "blue",
            "success": "darkgreen",
            "redirect": "orange",
            "error": "darkred",
            "header": "darkblue",
            "log": "gray"
        }
        
        # Sidebar
        self.sidebar = ctk.CTkFrame(root, width=220, corner_radius=15)
        self.sidebar.pack(side="left", fill="y", padx=15, pady=15)
        
        # Logo
        try:
            logo_img = Image.open("logo.png").resize((120, 120))
            self.logo = ImageTk.PhotoImage(logo_img)
            logo_label = ctk.CTkLabel(self.sidebar, image=self.logo, text="")
            logo_label.pack(pady=15)
        except:
            pass
        
        # Sidebar Buttons
        self.scan_button = ctk.CTkButton(self.sidebar, text="Scan URL", command=self.start_scan, fg_color="green", hover_color="lightgreen", corner_radius=25, font=self.cute_font)
        self.scan_button.pack(pady=15)
        
        self.clear_button = ctk.CTkButton(self.sidebar, text="Clear Results", command=self.clear_results, fg_color="orange", corner_radius=25, font=self.cute_font)
        self.clear_button.pack(pady=15)
        
        self.export_button = ctk.CTkButton(self.sidebar, text="Export Results", command=self.export_results, fg_color="blue", corner_radius=25, font=self.cute_font)
        self.export_button.pack(pady=15)
        
        self.customize_button = ctk.CTkButton(self.sidebar, text="Customize Colors", command=self.customize_colors, fg_color="purple", corner_radius=25, font=self.cute_font)
        self.customize_button.pack(pady=15)
        
        self.exit_button = ctk.CTkButton(self.sidebar, text="Exit", command=root.quit, fg_color="red", hover_color="pink", corner_radius=25, font=self.cute_font)
        self.exit_button.pack(pady=15)
        
        # Main Frame
        self.main_frame = ctk.CTkFrame(root, corner_radius=15)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=15, pady=15)
        
        # URL Entry (Clear Font)
        self.entry_label = ctk.CTkLabel(self.main_frame, text="Enter URL to Analyze: 🌐", font=self.cute_font)
        self.entry_label.pack(pady=10)
        self.entry = ctk.CTkEntry(self.main_frame, width=700, placeholder_text="Enter a valid URL here (e.g., https://example.com)", font=("Arial", 14, "bold"))
        self.entry.pack(pady=10)
        
        # Analysis Results Tab (Full Light Mode)
        self.results_tab = ctk.CTkTabview(self.main_frame)
        self.results_tab.pack(fill="both", expand=True, padx=15, pady=15)
        
        self.analysis_tab = self.results_tab.add("📊 Analysis Results & Logs")
        # Use standard Tkinter Text for full light mode control, with Arial font
        self.results_text = tk.Text(self.analysis_tab, wrap="word", font=("Arial", 12), bg="white", fg="black", relief="flat", padx=10, pady=10)
        self.results_text.pack(fill="both", expand=True, padx=15, pady=15)
        self.update_tag_colors()  # Apply initial colors
        
        # Progress & Status
        self.progress = ctk.CTkProgressBar(self.main_frame, width=700, corner_radius=15)
        self.progress.pack(pady=15)
        self.progress.set(0)
        
        self.status_label = ctk.CTkLabel(self.main_frame, text="Ready to analyze!", font=self.cute_font)
        self.status_label.pack(pady=10)
        
        # Spinner
        self.spinner = ctk.CTkLabel(self.main_frame, text="⏳", font=("Arial", 24))
        self.spinner.pack(pady=10)
        self.spinner.pack_forget()
    
    def update_tag_colors(self):
        for tag, color in self.colors.items():
            if tag == "header":
                self.results_text.tag_config(tag, foreground=color, font=("Arial", 14, "bold"))
            else:
                self.results_text.tag_config(tag, foreground=color, font=("Arial", 12, "bold"))  # Bold for info
    
    def log(self, message):
        self.results_text.insert("end", f"[LOG] {message}\n", "log")
        self.results_text.see("end")
    
    def update_progress(self, value):
        self.progress.set(value / 100)
        self.status_label.configure(text=f"Analyzing... {int(value)}% complete!")
        if value >= 100:
            self.spinner.pack_forget()
            self.is_scanning = False
    
    def customize_colors(self):
        # Dialog for color selection
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("🎨 Customize Colors")
        dialog.geometry("500x400")
        
        color_options = ["green", "red", "blue", "orange", "purple", "black", "gray", "darkgreen", "darkred", "darkblue", "cyan", "magenta"]
        
        vars = {}
        row = 0
        for key in self.colors:
            ttk.Label(dialog, text=f"{key.capitalize()}:").grid(row=row, column=0, padx=10, pady=5)
            vars[key] = tk.StringVar(value=self.colors[key])
            ttk.Combobox(dialog, textvariable=vars[key], values=color_options).grid(row=row, column=1, padx=10, pady=5)
            row += 1
        
        def apply():
            for key in self.colors:
                self.colors[key] = vars[key].get()
            self.update_tag_colors()
            dialog.destroy()
            messagebox.showinfo("Applied", "Colors updated!")
        
        ttk.Button(dialog, text="Apply", command=apply).grid(row=row, column=0, columnspan=2, pady=10)
    
    def start_scan(self):
        if self.is_scanning:
            messagebox.showwarning("Scanning", "Already scanning! Please wait. 😅")
            return
        url = self.entry.get().strip()
        if not url:
            messagebox.showerror("Invalid URL", "Please enter a valid URL! 😟")
            return
        self.is_scanning = True
        self.progress.set(0)
        self.spinner.pack(pady=10)
        self.status_label.configure(text="Starting analysis... 🔍")
        threading.Thread(target=self.scan_url, args=(url,)).start()
    
    def scan_url(self, url):
        try:
            self.update_progress(25)
            self.log("Fetching link data...")
            result = analyze_link(url)
            self.update_progress(75)
            self.log("Processing results...")
            self.display_results(result)
            self.update_progress(100)
            self.status_label.configure(text="Analysis Complete! 🏆")
        except Exception as e:
            self.log(f"❌ Error: {e}")
            messagebox.showerror("Error", f"Analysis failed: {e} 😵")
            self.update_progress(0)
            self.is_scanning = False
            self.spinner.pack_forget()
    
    def display_results(self, result):
        lines = self.results_text.get(1.0, tk.END).split("\n")
        self.results_text.delete(1.0, tk.END)
        for line in lines:
            if line.startswith("[LOG]"):
                self.results_text.insert("end", line + "\n", "log")
        
        self.results_text.insert("end", "\n--- GENERAL ANALYSIS ---\n", "header")
        for k, v in result.items():
            if k == "Redirections":
                continue
            tag = "safe" if k == "Fake" and not v else "danger" if k == "Fake" and v else "info"
            self.results_text.insert("end", f"{k}: {v}\n", tag)
        
        self.results_text.insert("end", "\n--- REDIRECTION CHAIN ---\n", "header")
        for hop_url, code in result.get("Redirections", []):
            if str(code).startswith("2"):
                tag = "success"
            elif str(code).startswith("3"):
                tag = "redirect"
            elif str(code).startswith("4") or str(code).startswith("5"):
                tag = "error"
            else:
                tag = "info"
            self.results_text.insert("end", f"  → [{code}] {hop_url}\n", tag)
    
    def clear_results(self):
        self.results_text.delete(1.0, tk.END)
        self.progress.set(0)
        self.status_label.configure(text="Results cleared!")
    
    def export_results(self):
        content = self.results_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("No Results", "No results to export! 😟")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "w") as f:
                f.write(content)
            messagebox.showinfo("Exported", "Results exported!")

# ================= START GUI FUNCTION ================= #
def start_gui():
    root = ctk.CTk()
    app = ShadowWallGUI(root)
    root.mainloop()

# If run directly
if __name__ == "__main__":
    start_gui()
