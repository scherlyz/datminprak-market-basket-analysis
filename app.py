from flask import Flask, jsonify, request
from flask_cors import CORS
import json

app = Flask(__name__)
# Mengizinkan Frontend (HTML) untuk mengakses API ini
CORS(app)

# Fungsi untuk membaca data JSON
def load_data():
    try:
        with open('rekomendasi_produk.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Endpoint utama untuk mengecek status server
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "success",
        "message": "API Market Basket Analysis Berjalan!"
    })

# Endpoint untuk mengambil rekomendasi berdasarkan produk
@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    # Mengambil parameter 'product' dari URL (contoh: ?product=CANGKIR)
    product_name = request.args.get('product')
    data = load_data()
    
    if not product_name:
        # Jika tidak ada parameter produk, kembalikan semua data
        return jsonify({
            "status": "success",
            "total_rules": len(data),
            "data": data
        })

    # Mencari rekomendasi yang cocok dengan nama barang utama (case-insensitive)
    hasil = [
        item for item in data 
        if item['barang_utama'].lower() == product_name.lower()
    ]

    # Mengurutkan berdasarkan lift (kekuatan rekomendasi tertinggi)
    hasil = sorted(hasil, key=lambda x: x['lift'], reverse=True)

    return jsonify({
        "status": "success",
        "barang_dicari": product_name.upper(),
        "total_rekomendasi": len(hasil),
        "data": hasil
    })

if __name__ == '__main__':
    # Menjalankan server di port 5000
    app.run(debug=True, port=5000)