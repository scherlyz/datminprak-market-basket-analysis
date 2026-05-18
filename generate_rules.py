import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
import json

print("1. Membaca dataset...")
df = pd.read_csv('online_retail_II.xlsx - Year 2009-2010.csv')

print("2. Membersihkan data...")
df['Description'] = df['Description'].str.strip()
df.dropna(axis=0, subset=['Invoice'], inplace=True)
df['Invoice'] = df['Invoice'].astype('str')
df = df[~df['Invoice'].str.contains('C')]

print("3. Menyiapkan keranjang belanja (Basket)...")
basket = (df[df['Country'] == "United Kingdom"]
          .groupby(['Invoice', 'Description'])['Quantity']
          .sum().unstack().reset_index().fillna(0)
          .set_index('Invoice'))

def encode_units(x):
    if x <= 0:
        return 0
    if x >= 1:
        return 1
    
basket_sets = basket.map(encode_units)

if 'POSTAGE' in basket_sets.columns:
    basket_sets.drop('POSTAGE', inplace=True, axis=1)

print("4. Menjalankan Algoritma Apriori...")
frequent_itemsets = apriori(basket_sets, min_support=0.02, use_colnames=True)
rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)
rules = rules[(rules['confidence'] >= 0.4) & (rules['lift'] >= 1)]
rules = rules.sort_values('lift', ascending=False)

print("5. Menyimpan hasil untuk Backend...")
hasil_backend = []
for index, row in rules.iterrows():
    barang_a = list(row['antecedents'])[0] # Barang yang dibeli
    barang_b = list(row['consequents'])[0] # Barang rekomendasi
    
    hasil_backend.append({
        "barang_utama": barang_a,
        "rekomendasi": barang_b,
        "confidence": round(row['confidence'], 2), 
        "lift": round(row['lift'], 2)
    })
with open('rekomendasi_produk.json', 'w') as f:
    json.dump(hasil_backend, f, indent=4)

print("Selesai! File 'rekomendasi_produk.json' berhasil dibuat.")