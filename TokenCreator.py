import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import subprocess
import pyperclip
import os
import json
import io
import requests
import random
import string
import shutil

# === INITIALIZE ROOT FIRST ===
root = tk.Tk()
root.withdraw()  # Hide root window during variable setup

# === GLOBALS ===
token_name = None
token_symbol = None
token_supply = None
token_decimals = None
output_box = None
setup_output = None
wallet_address = tk.StringVar()

# === UTILITIES ===
def get_balance(pubkey):
    try:
        result = subprocess.check_output(["solana", "balance", pubkey])
        return result.decode().strip()
    except:
        return "Error"

def generate_wallet():
    wallet_filename = f"wallet_{''.join(random.choices(string.ascii_lowercase + string.digits, k=6))}.json"
    wallet_path = os.path.join(os.getcwd(), wallet_filename)
    try:
        result = subprocess.run(
            ["solana-keygen", "new", "--no-bip39-passphrase", "--outfile", wallet_path],
            capture_output=True, text=True, input="y\n"
        )
        if result.returncode == 0:
            pubkey = subprocess.check_output(["solana-keygen", "pubkey", wallet_path]).decode().strip()
            wallet_address.set(pubkey)
            output_box.insert(tk.END, f"\n✅ Wallet Generated\nAddress: {pubkey}\nSaved to: {wallet_path}\n")
        else:
            messagebox.showerror("Error", result.stderr)
    except FileNotFoundError:
        messagebox.showerror("Missing CLI", "solana-keygen not found. Please run the Setup Install to fix this.")

def run_setup():
    try:
        if output_box:
            output_box.insert(tk.END, "\n⚙️ Running setup-install.sh script...\n")
        if setup_output:
            setup_output.insert(tk.END, "Launching bash setup script...\n")

        result = subprocess.run(["bash", "setup-install.sh"], capture_output=True, text=True)

        if setup_output:
            setup_output.insert(tk.END, result.stdout)
            if result.stderr:
                setup_output.insert(tk.END, f"\nWarnings/Errors:\n{result.stderr}\n")

    except Exception as e:
        if setup_output:
            setup_output.insert(tk.END, f"❌ Setup script error: {str(e)}\n")
        else:
            messagebox.showerror("Setup Script Error", str(e))



def select_image():
    path = filedialog.askopenfilename(filetypes=[("PNG Images", "*.png")])
    if path:
        logo_path.set(path)
        logo_url_input.delete(0, tk.END)
        img = Image.open(path).resize((100, 100))
        img = ImageTk.PhotoImage(img)
        logo_preview.config(image=img)
        logo_preview.image = img

def preview_url_logo(event=None):
    url = logo_url_input.get()
    if url:
        try:
            response = requests.get(url)
            img = Image.open(io.BytesIO(response.content)).resize((100, 100))
            img = ImageTk.PhotoImage(img)
            logo_preview.config(image=img)
            logo_preview.image = img
        except:
            messagebox.showerror("Image Error", "Unable to load image from URL.")

def create_token():
    name = token_name.get()
    symbol = token_symbol.get()
    supply = token_supply.get()
    decimals = token_decimals.get()
    logo_url = logo_url_input.get()
    pubkey = wallet_address.get()

    if not all([name, symbol, supply, decimals, pubkey]):
        messagebox.showerror("Missing Info", "Please fill in all token fields.")
        return

    try:
        balance_str = get_balance(pubkey)
        balance = float(balance_str.split()[0])
        if balance < 0.01:
            messagebox.showerror("Insufficient SOL", "Wallet must have ≥ 0.01 SOL.")
            return
    except:
        messagebox.showerror("Balance Error", "Unable to check balance.")
        return

    try:
        output = subprocess.check_output(["spl-token", "create-token"])
        mint = output.decode().split("\n")[-1].strip()

        subprocess.check_output(["spl-token", "create-account", mint])
        subprocess.check_output(["spl-token", "mint", mint, supply])
        subprocess.check_output(["spl-token", "authorize", mint, "mint", "--disable"])

        logo_uri = logo_url if logo_url else "https://yourdomain.com/logo.png"
        metadata = {
            "chainId": 101,
            "address": mint,
            "symbol": symbol,
            "name": name,
            "decimals": int(decimals),
            "logoURI": logo_uri,
            "tags": ["utility-token"]
        }
        with open(f"{symbol.lower()}-token.json", "w") as f:
            json.dump(metadata, f, indent=4)

        output_box.insert(tk.END, f"\n✅ Token Created\nMint: {mint}\nMetadata saved as {symbol.lower()}-token.json\n")

    except subprocess.CalledProcessError as e:
        messagebox.showerror("Token Creation Error", e.output.decode())

# === GUI SETUP ===
root = tk.Tk()
root.title("MysteryMM's Solana Token Creator")
root.geometry("800x1100")
root.configure(bg="#111827")

canvas = tk.Canvas(root, bg="#111827")
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="#111827")

scrollable_frame.bind(
    "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

wallet_address = tk.StringVar()
logo_path = tk.StringVar()

header = tk.Label(scrollable_frame, text="🧬 MysteryMM Solana Token Creator", fg="#38bdf8", bg="#111827", font=("Segoe UI", 20, "bold"))
header.pack(pady=15)

tk.Button(scrollable_frame, text="⚙️ Run Setup Install", command=run_setup, bg="#22d3ee", fg="black", font=("Segoe UI", 10, "bold"), padx=5).pack(pady=5)

setup_output = scrolledtext.ScrolledText(scrollable_frame, height=6, bg="#0f172a", fg="#facc15", font=("Consolas", 10))
setup_output.pack(fill=tk.BOTH, padx=10, pady=5, expand=False)

form_frame = tk.Frame(scrollable_frame, bg="#111827")
form_frame.pack(pady=10, padx=20, fill="both", expand=True)

# === Images ===
solana_img = Image.open("solana.png").resize((100, 100))
solana_photo = ImageTk.PhotoImage(solana_img)
tk.Label(form_frame, image=solana_photo, bg="#111827").pack(side="left", padx=10)

form_fields = tk.Frame(form_frame, bg="#111827")
form_fields.pack(side="left", expand=True)

tk.Label(form_fields, text="Enter Wallet Address or Generate One", fg="#e0f2fe", bg="#111827", font=("Segoe UI", 10)).pack()
tk.Entry(form_fields, textvariable=wallet_address, width=55, bg="#1e293b", fg="#93c5fd", insertbackground="#93c5fd", font=("Consolas", 10)).pack(pady=2)
tk.Button(form_fields, text="📋 Copy Address", command=lambda: pyperclip.copy(wallet_address.get()), bg="#334155", fg="white", font=("Segoe UI", 9)).pack(pady=3)
tk.Button(form_fields, text="⚙️ Generate Wallet", command=generate_wallet, bg="#6366f1", fg="white", font=("Segoe UI", 10, "bold")).pack(pady=5)

balance_label = tk.Label(form_fields, text=f"Balance: N/A", fg="#fcd34d", bg="#111827", font=("Consolas", 10))
balance_label.pack()
tk.Button(form_fields, text="🔁 Refresh Balance", command=lambda: balance_label.config(text=f"Balance: {get_balance(wallet_address.get())}"), bg="#0f172a", fg="white").pack(pady=5)

# === Token Input Fields ===
for label, var in [("Token Name", "token_name"), ("Token Symbol", "token_symbol"), ("Total Supply", "token_supply"), ("Decimals (usually 9)", "token_decimals")]:
    tk.Label(form_fields, text=label, fg="#e0f2fe", bg="#111827").pack()
    entry = tk.Entry(form_fields, bg="#1e293b", fg="#93c5fd")
    entry.pack(pady=2)
    globals()[var] = entry

token_decimals.insert(0, "9")

# === Logo Input ===
tk.Label(form_fields, text="Token Logo URL (Optional)", fg="#e0f2fe", bg="#111827").pack()
logo_url_input = tk.Entry(form_fields, width=60, bg="#1e293b", fg="#93c5fd")
logo_url_input.pack(pady=2)
logo_url_input.bind("<FocusOut>", preview_url_logo)

tk.Label(form_fields, text="OR Upload Local PNG", fg="#e0f2fe", bg="#111827").pack()
tk.Button(form_fields, text="Upload PNG", command=select_image, bg="#4b5563", fg="white").pack()
logo_preview = tk.Label(form_fields, bg="#111827")
logo_preview.pack(pady=5)

# === Right Solana Image ===
tk.Label(form_frame, image=solana_photo, bg="#111827").pack(side="left", padx=10)

# === Token Create Button ===
tk.Button(scrollable_frame, text="🚀 Create Token", command=create_token, bg="#10b981", fg="#0f0f0f", font=("Segoe UI", 14, "bold"), padx=10, pady=6).pack(pady=20)

# === Output Console ===
tk.Label(scrollable_frame, text="Console Output", fg="#e0f2fe", bg="#111827").pack()
output_box = scrolledtext.ScrolledText(scrollable_frame, height=10, bg="#0f172a", fg="#4ade80", font=("Consolas", 10))
output_box.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)

# === Footer ===
tk.Label(scrollable_frame, text="MysteryMM's Futuristic Solana Token Creator", fg="#64748b", bg="#111827", font=("Segoe UI", 9)).pack(side="bottom", pady=5)

root.mainloop()
