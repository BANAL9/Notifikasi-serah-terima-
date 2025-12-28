import customtkinter as ctk
from tkinter import messagebox, ttk
import cv2 
from PIL import Image, ImageTk 

class POSGui:
    def __init__(self, root, db, logic):
        self.root = root
        self.db = db
        self.logic = logic
        self.cap = None
        self.setup_ui()
        self.start_camera()
        self.root.bind("<F10>", lambda e: self.handle_pay())

    def setup_ui(self):
        # Header
        header = ctk.CTkFrame(self.root, height=60, fg_color="#E31E24")
        header.pack(side="top", fill="x")
        ctk.CTkLabel(header, text="BANAL SHOP - POS SYSTEM", font=("Arial", 22, "bold"), text_color="white").pack(pady=15)

        main = ctk.CTkFrame(self.root, fg_color="white")
        main.pack(fill="both", expand=True, padx=10, pady=10)

        # Kiri (Panel Scan & Tabel Produk)
        left = ctk.CTkFrame(main, fg_color="#F0F0F0")
        left.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.cam_label = ctk.CTkLabel(left, text="", width=400, height=200, fg_color="black")
        self.cam_label.pack(pady=5)

        # Tombol Manajemen Database
        m_frame = ctk.CTkFrame(left, fg_color="transparent")
        m_frame.pack(fill="x", padx=10)
        ctk.CTkButton(m_frame, text="+ BARANG BARU", command=self.add_product_db).pack(side="left", padx=5)
        ctk.CTkButton(m_frame, text="EDIT DATA BARANG", command=self.edit_product_db, fg_color="#2980b9").pack(side="left", padx=5)

        self.entry_scan = ctk.CTkEntry(left, width=300, placeholder_text="Scan Barcode...")
        self.entry_scan.pack(pady=10); self.entry_scan.bind("<Return>", self.handle_scan)

        self.tree = ttk.Treeview(left, columns=("K", "N", "H", "S"), show='headings')
        for col, head in zip(("K", "N", "H", "S"), ("KODE", "NAMA", "HARGA", "STOK")):
            self.tree.heading(col, text=head)
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.refresh_table()

        # Kanan (Struk & Kontrol Belanja)
        right = ctk.CTkFrame(main, width=350, fg_color="#EEEEEE")
        right.pack(side="right", fill="both", padx=5, pady=5)

        self.lbl_total = ctk.CTkLabel(right, text="Rp 0", font=("Arial", 40, "bold"), text_color="red")
        self.lbl_total.pack(pady=20)

        self.txt_struk = ctk.CTkTextbox(right, height=300)
        self.txt_struk.pack(fill="x", padx=10)

        # Tombol Kontrol Keranjang
        control_frame = ctk.CTkFrame(right, fg_color="transparent")
        control_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(control_frame, text="KURANGI", width=50, fg_color="#e67e22", 
                      command=self.handle_subtract_one).pack(side="left", padx=2)
        ctk.CTkButton(control_frame, text="GANTI QTY", fg_color="#f39c12", 
                      command=self.edit_cart_item).pack(side="left", fill="x", expand=True, padx=2)
        ctk.CTkButton(control_frame, text="CANCEL", width=70, fg_color="#c0392b", 
                      command=self.handle_cancel_item).pack(side="left", padx=2)

        ctk.CTkButton(right, text="[F10] BAYAR", fg_color="#E31E24", height=60, 
                      command=self.handle_pay).pack(pady=10, fill="x", padx=10)

    # --- PERBAIKAN FUNGSI EDIT BARANG ---
    def edit_product_db(self):
        k = ctk.CTkInputDialog(text="Masukkan Kode Barang yang akan di-edit:").get_input()
        if not k: return
        
        p = self.db.search_product(k)
        if p:
            # Edit Nama
            n_in = ctk.CTkInputDialog(text=f"Nama Baru (Lama: {p[1]}):").get_input()
            n = n_in if n_in else p[1]
            
            # Edit Harga dengan validasi angka
            h_in = ctk.CTkInputDialog(text=f"Harga Baru (Lama: {p[2]}):").get_input()
            try:
                h = float(h_in) if h_in else p[2]
            except ValueError:
                messagebox.showerror("Error", "Harga harus berupa angka!")
                return

            # Edit Stok dengan validasi angka
            s_in = ctk.CTkInputDialog(text=f"Stok Baru (Lama: {p[3]}):").get_input()
            try:
                s = int(s_in) if s_in else p[3]
            except ValueError:
                messagebox.showerror("Error", "Stok harus berupa angka!")
                return

            self.db.update_product(k, n, h, s)
            self.refresh_table()
            messagebox.showinfo("Sukses", f"Barang {k} berhasil diperbarui!")
        else:
            messagebox.showerror("Error", "Kode tidak ditemukan")

    # --- FUNGSI PENDUKUNG LAINNYA ---
    def refresh_table(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for row in self.db.get_all_products():
            self.tree.insert("", "end", values=(row[0], row[1], f"Rp {row[2]:,.0f}", row[3]))

    def handle_scan(self, event):
        kode = self.entry_scan.get()
        p = self.db.search_product(kode)
        if p:
            success, msg = self.logic.add_to_cart(p[0], p[1], p[2], p[3])
            if success: 
                self.update_ui()
                self.entry_scan.delete(0, 'end')
            else: messagebox.showwarning("Stok", msg)
        else: messagebox.showerror("Error", "Kode tidak terdaftar")

    def handle_pay(self):
        if not self.logic.keranjang: return
        total = self.logic.total_bayar
        uang = ctk.CTkInputDialog(text=f"Total Rp {total:,.0f}\nUang Tunai:").get_input()
        if uang:
            try:
                bayar = float(uang)
                if bayar >= total:
                    for k, v in self.logic.keranjang.items(): 
                        self.db.update_stock(k, v['qty'])
                    messagebox.showinfo("BANAL SHOP", f"Kembalian: Rp {bayar - total:,.0f}")
                    self.logic.reset_cart()
                    self.update_ui()
                    self.refresh_table()
                else: messagebox.showerror("Gagal", "Uang kurang")
            except ValueError: messagebox.showerror("Error", "Input tidak valid")

    def update_ui(self):
        self.txt_struk.configure(state="normal")
        self.txt_struk.delete("1.0", "end")
        self.txt_struk.insert("end", self.logic.get_receipt_text())
        self.txt_struk.configure(state="disabled")
        self.lbl_total.configure(text=f"Rp {self.logic.total_bayar:,.0f}")

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.update_camera()

    def update_camera(self):
        ret, frame = self.cap.read()
        if ret:
            img = Image.fromarray(cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)).resize((400, 200))
            imgtk = ImageTk.PhotoImage(image=img)
            self.cam_label.imgtk = imgtk
            self.cam_label.configure(image=imgtk)
        self.root.after(10, self.update_camera)

    def add_product_db(self):
        k = ctk.CTkInputDialog(text="Kode Baru:").get_input()
        n = ctk.CTkInputDialog(text="Nama:").get_input()
        h = ctk.CTkInputDialog(text="Harga:").get_input()
        s = ctk.CTkInputDialog(text="Stok:").get_input()
        if k and n and h and s:
            try:
                self.db.add_product(k, n, float(h), int(s))
                self.refresh_table()
            except: messagebox.showerror("Error", "Gagal menambah barang")

    def handle_subtract_one(self):
        k = ctk.CTkInputDialog(text="Kode Barang untuk dikurangi (-1):").get_input()
        if k in self.logic.keranjang:
            new_qty = self.logic.keranjang[k]['qty'] - 1
            p = self.db.search_product(k)
            self.logic.update_qty(k, new_qty, p[3])
            self.update_ui()

    def handle_cancel_item(self):
        k = ctk.CTkInputDialog(text="Kode Barang yang ingin di-CANCEL:").get_input()
        if k in self.logic.keranjang:
            self.logic.remove_item(k)
            self.update_ui()

    def edit_cart_item(self):
        k = ctk.CTkInputDialog(text="Kode Barang di struk:").get_input()
        if k in self.logic.keranjang:
            p = self.db.search_product(k)
            q = ctk.CTkInputDialog(text=f"Masukkan Qty Baru:").get_input()
            if q:
                success, msg = self.logic.update_qty(k, int(q), p[3])
                if success: self.update_ui()
                else: messagebox.showwarning("Gagal", msg)