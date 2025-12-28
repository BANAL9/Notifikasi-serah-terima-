import customtkinter as ctk
from database import Database
from kasir_logic import POSLogic
from gui import POSGui

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    root = ctk.CTk()
    root.title("KASIR BANAL SHOP")
    root.geometry("1150x700")
    
    app = POSGui(root, Database(), POSLogic())
    root.mainloop()