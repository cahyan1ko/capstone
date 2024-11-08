from flask import Flask, render_template, request, jsonify, g
from flask_cors import CORS
import pymysql

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = Flask(__name__)
CORS(app)

model_name = "models/fine_tuned_gpt_neo_poverty_lens"  # Update path sesuai lokasi model Anda
tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
model = AutoModelForCausalLM.from_pretrained(model_name, local_files_only=True)

# Fungsi untuk menghasilkan respons
def generate_response(input_text, max_new_tokens=200):
    # Prompt yang memancing respons
    prompt = (
        f"Anda adalah asisten cerdas dari PovertyLens, aplikasi pemetaan kemiskinan. "
        f"Berikan jawaban informatif terkait pertanyaan pengguna.\n\n"
        f"Pertanyaan: {input_text}\nJawab:"
    )
    
    # Tokenisasi prompt dan input
    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=300)
    
    # Menghasilkan output dari model dengan pengaturan sampling
    outputs = model.generate(
        inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        max_new_tokens=max_new_tokens,
        do_sample=True,
        top_k=50,
        top_p=0.85,
        temperature=0.7,
        pad_token_id=tokenizer.eos_token_id
    )
    
    # Decode hasil output menjadi teks
    response = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
    
    # Jika respons kosong, berikan respons default
    if not response:
        response = "Maaf, saya tidak dapat memahami pertanyaan Anda. Bisa dijelaskan lebih lanjut?"
    
    return response


@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.json['message']
    bot_response = generate_response(user_message)
    return jsonify(response=bot_response)

# Konfigurasi koneksi MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # Ganti dengan password MySQL Anda
app.config['MYSQL_DB'] = 'poverty_lens'

# Fungsi untuk membuka koneksi database
def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
    return g.db

# Menutup koneksi database
@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route("/cekdb")
def cekdb():
    try:
        db = get_db()
        return "Koneksi ke database MySQL berhasil!"
    except Exception as e:
        return f"Gagal menghubungkan ke database: {e}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/pindai-wilayah")
def pindaiWilayah():
    return render_template("pindai-wilayah.html")

@app.route("/daftar-lembaga")
def dtLembaga():
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT id, nama, logo_url FROM lembaga")
        data = cur.fetchall()
        cur.close()
    except Exception as e:
        return str(e)  # Menampilkan pesan error jika ada masalah

    return render_template('dt-lembaga.html', lembaga_data=data)

@app.route("/detail-lembaga/<int:lembaga_id>")
def detailLembaga(lembaga_id):
    try:
        db = get_db()
        cur = db.cursor()
        # Query untuk mengambil data dari tabel lembaga dan detail_lembaga
        cur.execute("""
            SELECT l.nama, l.logo_url, d.alamat_kantor, d.telepon, d.email, 
                   d.web_resmi, d.deskripsi, d.informasi
            FROM lembaga l
            JOIN detail_lembaga d ON l.id = d.lembaga_id
            WHERE l.id = %s
        """, (lembaga_id,))
        
        # Ambil hasil query
        detail = cur.fetchone()
        cur.close()
        
        # Cek apakah data ditemukan
        if detail is None:
            return "Lembaga tidak ditemukan", 404
        
        # Kirim data ke template detail-lembaga.html
        return render_template('detail-lembaga.html', detail=detail)

    except Exception as e:
        return str(e)

# API

@app.route("/api/lembaga", methods=['GET'])
def get_lembaga():
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT id, nama, logo_url FROM lembaga")  # Mengambil ID, nama, dan logo
        lembaga_data = cur.fetchall()
        cur.close()

        lembaga_list = []
        for lembaga in lembaga_data:
            lembaga_dict = {
                'id': lembaga[0],
                'nama': lembaga[1],
                'logo_url': lembaga[2]
            }
            lembaga_list.append(lembaga_dict)

        return jsonify(lembaga_list)  # Mengembalikan data dalam format JSON

    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Mengembalikan error dalam format JSON
    
@app.route("/api/detail-lembaga/<int:lembaga_id>", methods=['GET'])
def api_detail_lembaga(lembaga_id):
    try:
        db = get_db()
        cur = db.cursor()
        # Query untuk mengambil detail lembaga berdasarkan ID
        cur.execute("""
            SELECT l.nama, l.logo_url, d.alamat_kantor, d.telepon, d.email, 
                   d.web_resmi, d.deskripsi, d.informasi
            FROM lembaga l
            JOIN detail_lembaga d ON l.id = d.lembaga_id
            WHERE l.id = %s
        """, (lembaga_id,))
        
        detail = cur.fetchone()
        cur.close()
        
        # Cek apakah data ditemukan
        if detail is None:
            return jsonify({'error': 'Lembaga tidak ditemukan'}), 404
        
        # Mengonversi hasil menjadi dictionary
        detail_dict = {
            'nama': detail[0],
            'logo_url': detail[1],
            'alamat_kantor': detail[2],
            'telepon': detail[3],
            'email': detail[4],
            'web_resmi': detail[5],
            'deskripsi': detail[6],
            'informasi': detail[7]
        }

        return jsonify(detail_dict)  # Mengembalikan data dalam format JSON

    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Mengembalikan error dalam format JSON
    
if __name__ == "__main__":
    app.run(debug=True)
