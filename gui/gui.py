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

    def scan():
        url = entry.get()
        result = analyze_link(url)
        output.delete(1.0, tk.END)
        for k, v in result.items():
            color = "green" if k == "Fake" and not v else "red" if v else "yellow"
            output.insert(tk.END, f"{k}: {v}\n", k)
            output.tag_config(k, foreground=color)

    tk.Button(app, text="Scan URL", command=scan).pack()

    app.mainloop()
