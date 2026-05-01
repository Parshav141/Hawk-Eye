import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import hashlib
import time

class HawkEyeTransition:
    def __init__(self, root):
        self.root = root
        self.root.title("HAWK EYE")
        self.root.geometry("450x850")
        self.root.configure(bg="#121212")

        self.img_path = None
        self.tk_img = None
        self.dual_layer_var = tk.BooleanVar(value=False)

        self.main_frame = tk.Frame(root, bg="#121212")
        self.main_frame.pack(fill="both", expand=True)

        self.status_bar = tk.Label(root, text="SYSTEM READY", font=("Segoe UI", 9, "bold"), 
                                   bg="#1c1c1e", fg="#ffffff", pady=10)
        self.status_bar.pack(side="bottom", fill="x")

        # Initial launch
        self.show_home_screen()
    #TRANSITION ENGINE
    def transition_to(self, screen_func):
        """Animates a fade out, executes the screen change, then fades in."""
        def fade_out():
            alpha = self.root.attributes("-alpha")
            if alpha > 0.1:
                alpha -= 0.15
                self.root.attributes("-alpha", alpha)
                self.root.after(20, fade_out)
            else:
                self.root.attributes("-alpha", 0)
                screen_func() # Change the UI while invisible
                fade_in()

        def fade_in():
            alpha = self.root.attributes("-alpha")
            if alpha < 1.0:
                alpha += 0.15
                self.root.attributes("-alpha", alpha)
                self.root.after(20, fade_in)
            else:
                self.root.attributes("-alpha", 1.0)

        fade_out()

    #NOTIFICATIONS & UI HELPERS
    def notify(self, message, type="info"):
        colors = {
            "info": ("#1c1c1e", "#6c757d"),
            "success": ("#c5c5c5", "#000000"),
            "error": ("#bebebe", "#ffffff"),
            "warning": ("#adadad", "#000000")
        }
        bg, fg = colors.get(type, colors["info"])
        self.status_bar.config(text=message.upper(), bg=bg, fg=fg)
        self.root.after(4000, lambda: self.status_bar.config(text="SYSTEM READY", bg="#1c1c1e", fg="#6c757d"))

    def clear_screen(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    #SCREENS (WRAPPED IN TRANSITIONS)

    def show_home_screen(self):
        self.clear_screen()
        tk.Label(self.main_frame, text="HAWK EYE", font=("Segoe UI Light", 40), bg="#121212", fg="#ffffff").pack(pady=(150, 5))
        tk.Frame(self.main_frame, width=40, height=2, bg="#ffffff").pack()
        
        btn_container = tk.Frame(self.main_frame, bg="#121212")
        btn_container.pack(side="bottom", pady=80)

        for text, cmd in [("HIDE MESSAGE", lambda: self.transition_to(self.show_encrypt_screen)), 
                          ("REVEAL MESSAGE", lambda: self.transition_to(self.show_decode_screen))]:
            btn = tk.Button(btn_container, text=text, command=cmd, font=("Segoe UI", 10, "bold"),
                            bg="#ffffff", fg="#000000", activebackground="#adb5bd", relief="flat",
                            width=28, height=2, cursor="hand2", bd=0)
            btn.pack(pady=10)

    def show_encrypt_screen(self):
        self.clear_screen()
        nav = tk.Frame(self.main_frame, bg="#121212", pady=20)
        nav.pack(fill="x")
        tk.Button(nav, text="✕", command=lambda: self.transition_to(self.show_home_screen), 
                  bg="#121212", fg="#6c757d", relief="flat", font=("Arial", 14)).pack(side="right", padx=30)

        body = tk.Frame(self.main_frame, bg="#121212", padx=40)
        body.pack(fill="both", expand=True)
        tk.Label(body, text="ENCRYPT", font=("Segoe UI", 18, "bold"), bg="#121212", fg="white").pack(anchor="w", pady=10)

        self.canvas = tk.Canvas(body, width=320, height=180, bg="#1c1c1e", highlightthickness=1, highlightbackground="#2c2c2e")
        self.canvas.pack(pady=10)
        self.canvas.create_text(160, 90, text="+ SELECT CARRIER", fill="#48484a", font=("Segoe UI", 8, "bold"))
        self.canvas.bind("<Button-1>", lambda e: self.load_img())

        tk.Label(body, text="SECRET MESSAGE", font=("Segoe UI", 8, "bold"), bg="#121212", fg="#48484a").pack(anchor="w")
        self.stego_text = tk.Text(body, height=4, bg="#1c1c1e", fg="white", relief="flat", padx=10, pady=10)
        self.stego_text.pack(fill="x", pady=(0, 10))

        tk.Label(body, text="ACCESS KEY", font=("Segoe UI", 8, "bold"), bg="#121212", fg="#48484a").pack(anchor="w")
        self.pass_image = tk.Entry(body, show="*", bg="#1c1c1e", fg="white", relief="flat", bd=8)
        self.pass_image.pack(fill="x", pady=(0, 10))

        tk.Checkbutton(body, text="Double Security", variable=self.dual_layer_var, command=self.toggle_dual, 
                            bg="#121212", fg="#6c757d", selectcolor="#121212", activebackground="#121212").pack(anchor="w")

        self.pass_cipher = tk.Entry(body, show="*", bg="#1c1c1e", fg="white", relief="flat", bd=8, state="disabled")
        self.pass_cipher.pack(fill="x")

        tk.Button(body, text="GENERATE", command=self.run_hide, bg="#ffffff", fg="#000000", font=("Segoe UI", 10, "bold"), relief="flat", height=2).pack(fill="x", pady=30)

    def show_decode_screen(self):
        self.clear_screen()
        nav = tk.Frame(self.main_frame, bg="#121212", pady=20)
        nav.pack(fill="x")
        tk.Button(nav, text="✕", command=lambda: self.transition_to(self.show_home_screen), 
                  bg="#121212", fg="#6c757d", relief="flat", font=("Arial", 14)).pack(side="right", padx=30)

        self.body = tk.Frame(self.main_frame, bg="#121212", padx=40)
        self.body.pack(fill="both", expand=True)
        tk.Label(self.body, text="DECODE", font=("Segoe UI", 18, "bold"), bg="#121212", fg="white").pack(anchor="w", pady=10)

        self.canvas = tk.Canvas(self.body, width=320, height=150, bg="#1c1c1e", highlightthickness=1, highlightbackground="#2c2c2e")
        self.canvas.pack(pady=10)
        self.canvas.create_text(160, 75, text="SELECT IMAGE", fill="#48484a", font=("Segoe UI", 8, "bold"))
        self.canvas.bind("<Button-1>", lambda e: self.load_img())

        self.pass_image = tk.Entry(self.body, bg="#1c1c1e", fg="#ffffff", relief="flat", font=("Segoe UI", 10), justify="center", bd=10)
        self.pass_image.insert(0, "ENTER PASSWORD")
        self.pass_image.pack(fill="x", pady=10)
        self.pass_image.bind("<FocusIn>", self.clear_placeholder)

        tk.Button(self.body, text="REVEAL", command=self.run_extract, bg="#ffffff", fg="#000000", font=("Segoe UI", 10, "bold"), relief="flat", height=2).pack(fill="x")

        self.reveal_frame = tk.Frame(self.body, bg="#121212")
        self.stego_text = tk.Text(self.reveal_frame, height=5, bg="#1c1c1e", fg="#d2d2d2", relief="flat", font=("Consolas", 10), padx=10, pady=10)
        self.stego_text.pack(fill="x", pady=10)

        self.cipher_frame = tk.Frame(self.body, bg="#121212")
        self.pass_cipher = tk.Entry(self.cipher_frame, show="*", bg="#1c1c1e", fg="white", relief="flat", bd=8)
        self.pass_cipher.pack(fill="x", pady=5)
        tk.Button(self.cipher_frame, text="CIPHER DECRYPT", command=self.manual_decrypt, bg="#c1c1c1", fg="black", font=("Segoe UI", 9, "bold"), relief="flat").pack(fill="x")

    #REMAINING LOGIC (STAYED SAME)
    def clear_placeholder(self, event):
        if self.pass_image.get() == "ENTER PASSWORD":
            self.pass_image.delete(0, "end")
            self.pass_image.config(show="*")

    def toggle_dual(self):
        state = "normal" if self.dual_layer_var.get() else "disabled"
        self.pass_cipher.config(state=state)

    def load_img(self):
        path = filedialog.askopenfilename()
        if path:
            self.img_path = path
            img = Image.open(path).convert("RGB")
            img.thumbnail((320, 180))
            self.tk_img = ImageTk.PhotoImage(img)
            self.canvas.delete("all")
            self.canvas.create_image(160, 90, image=self.tk_img)

    def xor_crypt(self, data_bytes, key_str):
        key = hashlib.sha256(key_str.encode()).digest()
        return bytes([data_bytes[i] ^ key[i % len(key)] for i in range(len(data_bytes))])

    def run_hide(self):
        text, pass1 = self.stego_text.get("1.0", "end-1c"), self.pass_image.get()
        if not self.img_path or not text or not pass1:
            return self.notify("Missing required fields", "error")

        prefix = "P:"
        if self.dual_layer_var.get():
            pass2 = self.pass_cipher.get()
            if not pass2: return self.notify("Cipher key required", "warning")
            payload = self.xor_crypt(text.encode(), pass2).hex()
            prefix = "C:"
        else: payload = text

        key1 = hashlib.sha256(pass1.encode()).digest()
        final_data = (prefix + payload + "###").encode()
        encrypted = bytes([final_data[i] ^ key1[i % len(key1)] for i in range(len(final_data))])
        binary = ''.join(format(b, '08b') for b in encrypted)

        img = Image.open(self.img_path).convert("RGB")
        pixels = list(img.getdata())
        new_pix, idx = [], 0
        for p in pixels:
            p = list(p)
            for i in range(3):
                if idx < len(binary):
                    p[i] = (p[i] & ~1) | int(binary[idx])
                    idx += 1
            new_pix.append(tuple(p))

        res = Image.new("RGB", img.size)
        res.putdata(new_pix)
        out = filedialog.asksaveasfilename(defaultextension=".png")
        if out:
            res.save(out)
            self.notify("Image Saved", "success")
            self.root.after(1500, lambda: self.transition_to(self.show_home_screen))

    def run_extract(self):
        pass1 = self.pass_image.get()
        if not self.img_path: return self.notify("No image selected", "error")
        
        img = Image.open(self.img_path).convert("RGB")
        pixels = list(img.getdata())
        key1 = hashlib.sha256(pass1.encode()).digest()

        bits, decoded_bytes = "", bytearray()
        for p in pixels:
            for ch in p:
                bits += str(ch & 1)
                if len(bits) == 8:
                    decoded_bytes.append(int(bits, 2) ^ key1[len(decoded_bytes) % len(key1)])
                    bits = ""
                    if decoded_bytes.endswith(b"###"):
                        res = decoded_bytes[:-3].decode(errors="ignore")
                        prefix, content = res[:2], res[2:]
                        self.reveal_frame.pack(fill="x")
                        self.stego_text.delete("1.0", "end")
                        self.stego_text.insert("1.0", content)
                        if prefix == "C:": 
                            self.cipher_frame.pack(fill="x")
                            self.notify("Layer 2 Key Needed", "warning")
                        else:
                            self.notify("Data Verified", "success")
                        return
        self.notify("Invalid Key", "error")

    def manual_decrypt(self):
        try:
            data, key = self.stego_text.get("1.0", "end-1c").strip(), self.pass_cipher.get()
            final = self.xor_crypt(bytes.fromhex(data), key).decode()
            self.stego_text.delete("1.0", "end")
            self.stego_text.insert("1.0", final)
            self.cipher_frame.pack_forget()
            self.notify("Decryption Complete", "success")
        except: 
            self.notify("Key Incorrect", "error")

if __name__ == "__main__":
    root = tk.Tk()
    # Crisp DPI scaling
    try: from ctypes import windll; windll.shcore.SetProcessDpiAwareness(1)
    except: pass
    app = HawkEyeTransition(root)
    root.mainloop()