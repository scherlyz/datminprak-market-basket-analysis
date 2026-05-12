import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
import json

print("1. Membaca dataset...")
# Sesuaikan nama file dengan dataset kamu
df = pd.read_csv('online_retail_II.xlsx - Year 2009-2010.csv')

print("2. Membersihkan data...")
# Hapus spasi berlebih di nama barang
df['Description'] = df['Description'].str.strip()
# Hapus baris yang tidak punya nomor invoice
df.dropna(axis=0, subset=['Invoice'], inplace=True)
df['Invoice'] = df['Invoice'].astype('str')
# Hapus transaksi yang dibatalkan (biasanya diawali huruf 'C')
df = df[~df['Invoice'].str.contains('C')]

print("3. Menyiapkan keranjang belanja (Basket)...")
# Agar proses tidak terlalu berat, kita ambil contoh data dari 'United Kingdom' saja
# karena mayoritas data dari sana.
basket = (df[df['Country'] == "United Kingdom"]
          .groupby(['Invoice', 'Description'])['Quantity']
          .sum().unstack().reset_index().fillna(0)
          .set_index('Invoice'))

# Ubah nilai quantity menjadi 1 (jika beli) dan 0 (jika tidak beli)
def encode_units(x):
    if x <= 0:
        return 0
    if x >= 1:
        return 1

# PERUBAHAN DI SINI: applymap diganti menjadi map untuk Pandas v3 ke atas
basket_sets = basket.map(encode_units)

# Hapus kolom 'POSTAGE' jika tidak dianggap sebagai barang
if 'POSTAGE' in basket_sets.columns:
    basket_sets.drop('POSTAGE', inplace=True, axis=1)

print("4. Menjalankan Algoritma Apriori...")
# Mencari kombinasi barang yang sering dibeli (minimal support 2%)
# Proses ini mungkin memakan waktu beberapa saat (1-3 menit) tergantung spesifikasi laptop
frequent_itemsets = apriori(basket_sets, min_support=0.02, use_colnames=True)

# Membuat aturan asosiasi (Association Rules)
rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)

# Filter aturan yang kuat (misal: confidence minimal 40%)
rules = rules[(rules['confidence'] >= 0.4) & (rules['lift'] >= 1)]

# Urutkan berdasarkan lift tertinggi (paling relevan)
rules = rules.sort_values('lift', ascending=False)

print("5. Menyimpan hasil untuk Backend...")
# Format ulang data agar mudah dibaca oleh Backend (JSON)
hasil_backend = []
for index, row in rules.iterrows():
    # mlxtend mengembalikan tipe frozenset, jadi harus diubah ke list/string
    barang_a = list(row['antecedents'])[0] # Barang yang dibeli
    barang_b = list(row['consequents'])[0] # Barang rekomendasi
    
    hasil_backend.append({
        "barang_utama": barang_a,
        "rekomendasi": barang_b,
        "confidence": round(row['confidence'], 2), # Seberapa yakin (%) barang B dibeli jika A dibeli
        "lift": round(row['lift'], 2) # Kekuatan hubungan keterkaitan
    })

# Simpan ke JSON
with open('rekomendasi_produk.json', 'w') as f:
    json.dump(hasil_backend, f, indent=4)

print("Selesai! File 'rekomendasi_produk.json' berhasil dibuat.")