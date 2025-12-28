from datetime import datetime

class POSLogic:
    def __init__(self):
        self.keranjang = {}
        self.total_bayar = 0

    def add_to_cart(self, kode, nama, harga, stok_db):
        qty_skrg = self.keranjang.get(kode, {}).get('qty', 0)
        if qty_skrg + 1 > stok_db:
            return False, f"STOK HABIS! (Sisa: {stok_db})"
            
        if kode in self.keranjang:
            self.keranjang[kode]['qty'] += 1
        else:
            self.keranjang[kode] = {'nama': nama, 'harga': harga, 'qty': 1}
        
        self.calculate_total()
        return True, "OK"

    def remove_item(self, kode):
        if kode in self.keranjang:
            del self.keranjang[kode]
            self.calculate_total()
            return True
        return False

    def update_qty(self, kode, qty_baru, stok_db):
        if kode in self.keranjang:
            if qty_baru > stok_db: return False, "Stok tidak cukup"
            if qty_baru <= 0: del self.keranjang[kode]
            else: self.keranjang[kode]['qty'] = qty_baru
            self.calculate_total()
            return True, "Update berhasil"
        return False, "Barang tidak ada"

    def calculate_total(self):
        self.total_bayar = sum(v['harga'] * v['qty'] for v in self.keranjang.values())

    def reset_cart(self):
        self.keranjang = {}; self.total_bayar = 0

    def get_receipt_text(self):
        now = datetime.now().strftime('%d/%m/%y %H:%M')
        text = f"{'BANAL SHOP':^38}\n{'JL. RAYA BEKASI KM.12':^38}\n{now:^38}\n" + "="*38 + "\n"
        for k, v in self.keranjang.items():
            text += f"{v['nama'][:25]:<25}\n  {v['qty']} X {v['harga']:>8,.0f} = {v['qty']*v['harga']:>10,.0f}\n"
        text += "-"*38 + f"\nTOTAL{'':>17}Rp {self.total_bayar:>10,.0f}\n"
        return text