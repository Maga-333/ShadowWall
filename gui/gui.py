import tkinter as tk
from realtime_monitor import analyze_link

def start_gui():
    app = tk.Tk()
    app.title("🛡️ ShadowWall - Live Link Analyzer")
    app.configure(bg="black")
    app.geometry("700x400")

    entry = tk.Entry(app, width=70, bg="white", fg="black")
    entry.pack(pady=10)

    output = tk.Text(app, height=15, width=85, bg="black", fg="white")
    output.pack()

    # ✅ Configure tags once
    output.tag_config("header", foreground="cyan", font=("Courier", 10, "bold"))
    output.tag_config("success", foreground="green")
    output.tag_config("redirect", foreground="pink")
    output.tag_config("error", foreground="red")
    output.tag_config("info", foreground="blue")
    output.tag_config("safe", foreground="green")
    output.tag_config("danger", foreground="red")

    def scan():
        url = entry.get()
        result = analyze_link(url)
        output.delete(1.0, tk.END)

        # 🧠 Display all general data
        for k, v in result.items():
            if k == "Redirections":
                continue  # Skip here; we handle separately
            tag = "safe" if k == "Fake" and not v else "danger" if k == "Fake" and v else "info"
            output.insert(tk.END, f"{k}: {v}\n", tag)

        # 🔁 Redirection chain
        output.insert(tk.END, "\n🔁 Redirection Chain:\n", "header")
        for hop_url, code in result["Redirections"]:
            if str(code).startswith("2"):
                tag = "success"
            elif str(code).startswith("3"):
                tag = "redirect"
            elif str(code).startswith("4") or str(code).startswith("5"):
                tag = "error"
            else:
                tag = "info"
            output.insert(tk.END, f"  → [{code}] {hop_url}\n", tag)

    tk.Button(app, text="Scan URL", command=scan).pack()

    app.mainloop()

