import streamlit as st
import serial
import serial.tools.list_ports
import threading
import time

# Data produk berdasarkan UID
products = {
    "75 A0 7B 00": ("Produk A", 50000),
    "EF A7 53 1F": ("Produk B", 75000),
    "FF 5E 98 1F": ("Produk C", 100000),
}

# Variabel untuk menyimpan daftar item dan total harga
if "transaction_items" not in st.session_state:
    st.session_state["transaction_items"] = []
if "total_price" not in st.session_state:
    st.session_state["total_price"] = 0
if "arduino" not in st.session_state:
    st.session_state["arduino"] = []

# Fungsi untuk mencoba koneksi ke RFID
def connect_to_rfid():
    ports = serial.tools.list_ports.comports()
    connections = []
    for port in ports:
        try:
            ser = serial.Serial(port.device, 9600, timeout=1)
            time.sleep(2)  # Tunggu koneksi stabil
            connections.append(ser)
            st.success(f"Berhasil terhubung ke {port.device}")
        except serial.SerialException as e:
            st.warning(f"Gagal terhubung ke {port.device}: {e}")
    return connections

# Fungsi untuk membaca data RFID dari port yang diberikan
def read_rfid(arduino):
    while True:
        if arduino.in_waiting > 0:
            line = arduino.readline().decode("utf-8").strip()
            if "UID:" in line:
                uid = line.replace("UID:", "").strip()
                add_product_to_cart(uid)
        time.sleep(0.1)

# Fungsi untuk menambahkan produk berdasarkan UID ke keranjang
def add_product_to_cart(uid):
    if uid in products:
        product_name, product_price = products[uid]
        st.session_state["transaction_items"].append((product_name, product_price))
        st.session_state["total_price"] += product_price
        st.success(f"{product_name} telah ditambahkan ke keranjang.")
    else:
        st.warning("Produk dengan UID tersebut tidak ditemukan.")

# Fungsi untuk mereset transaksi
def reset_transaction():
    st.session_state["transaction_items"] = []
    st.session_state["total_price"] = 0

# Fungsi utama aplikasi
def main():
    st.title("Aplikasi Kasir RFID")

    # Tampilkan keranjang belanja
    st.subheader("Keranjang Belanja")
    transaction_items = st.session_state["transaction_items"]
    if transaction_items:
        for idx, (name, price) in enumerate(transaction_items, start=1):
            st.write(f"{idx}. {name} - Rp {price}")
    else:
        st.write("Keranjang kosong.")

    # Tampilkan total harga
    st.subheader(f"Total: Rp {st.session_state['total_price']}")

    # Tombol kontrol
    if st.button("Reset"):
        reset_transaction()
        st.success("Keranjang berhasil direset!")

    if st.button("Selesai"):
        if transaction_items:
            st.success("Transaksi selesai. Terima kasih!")
            reset_transaction()
        else:
            st.warning("Keranjang kosong.")

# Menghubungkan ke RFID
if not st.session_state["arduino"]:
    arduino_connections = connect_to_rfid()
    
    if arduino_connections:
        for arduino in arduino_connections:
            threading.Thread(target=read_rfid, args=(arduino,), daemon=True).start()
    else:
        st.error("Tidak ada port yang terhubung dengan RFID reader.")

# Jalankan aplikasi
main()