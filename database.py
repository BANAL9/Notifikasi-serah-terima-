import sqlite3

class Database:
    def __init__(self, db_name="banal_shop.db"):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS produk 
                              (kode TEXT PRIMARY KEY, nama TEXT, harga REAL, stok INTEGER)''')
            
            sample_produk = [
                ('1001', 'AMIDIS AIR MINUM 600ML', 5000, 100),
                ('1002', 'BANAL TISSUE FACIAL', 12500, 50),
                ('1003', 'INDOMIE GORENG SPESIAL', 3100, 200),
                ('1004', 'BEAR BRAND 189ML', 10500, 40),
                ('1005', 'ULTRA MILK', 15000, 30),  
                ('1006', 'JAS HUJAN BANAL', 100000, 30)   
            ]
            try:
                cursor.executemany("INSERT INTO produk VALUES (?, ?, ?, ?)", sample_produk)
                conn.commit()
            except sqlite3.IntegrityError:
                pass 

    def get_all_products(self):
        with sqlite3.connect(self.db_name) as conn:
            return conn.execute("SELECT * FROM produk").fetchall()

    def search_product(self, kode):
        with sqlite3.connect(self.db_name) as conn:
            return conn.execute("SELECT * FROM produk WHERE kode=?", (kode,)).fetchone()

    def add_product(self, kode, nama, harga, stok):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("INSERT INTO produk VALUES (?, ?, ?, ?)", (kode, nama, harga, stok))
            conn.commit()

    def update_product(self, kode, nama, harga, stok):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("UPDATE produk SET nama=?, harga=?, stok=? WHERE kode=?", (nama, harga, stok, kode))
            conn.commit()

    def update_stock(self, kode, qty):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("UPDATE produk SET stok = stok - ? WHERE kode = ?", (qty, kode))
            conn.commit()