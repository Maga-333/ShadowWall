import tkinter as tk
from realtime_monitor import analyze_link

def show_result(url):
    result = analyze_link(url)
    output.delete(1.0, tk.END)
    for key, val in result.items():
        color = "green" if key == "Fake" and not val else "red"
        output.insert(tk.END, f"{key}: {val}\n", key)
        output.tag_config(key, foreground=color)

app = tk.Tk()
app.title("ShadowWall - Real-Time Link Analyzer")

url_entry = tk.Entry(app, width=50)
url_entry.pack(pady=10)

tk.Button(app, text="Scan URL", command=lambda: show_result(url_entry.get())).pack()

output = tk.Text(app, height=15, width=70)
output.pack()

app.mainloop()
