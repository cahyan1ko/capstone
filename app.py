from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import joblib
import base64
import cv2

from io import BytesIO
from PIL import Image
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import numpy as np

from flask_migrate import Migrate

app = Flask(__name__)
CORS(app)

# Konfigurasi SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://A3CP:S.Tr.Kom2024@194.31.53.102/A3CP"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inisialisasi SQLAlchemy dan Flask-Migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Definisi Model
class Lembaga(db.Model):
    __tablename__ = 'lembaga'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(255), nullable=False)
    logo_url = db.Column(db.String(255), nullable=True)
    detail = db.relationship('DetailLembaga', backref='lembaga', uselist=False)

class DetailLembaga(db.Model):
    __tablename__ = 'detail_lembaga'
    id = db.Column(db.Integer, primary_key=True)
    lembaga_id = db.Column(db.Integer, db.ForeignKey('lembaga.id'), nullable=False)
    alamat_kantor = db.Column(db.String(255), nullable=True)
    telepon = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    web_resmi = db.Column(db.String(255), nullable=True)
    deskripsi = db.Column(db.Text, nullable=True)
    informasi = db.Column(db.Text, nullable=True)

class Kemiskinan(db.Model):
    __tablename__ = 'kemiskinan'
    
    id = db.Column(db.Integer, primary_key=True)
    tahun = db.Column(db.Integer, nullable=False)
    garis_kemiskinan = db.Column(db.String(50), nullable=True)
    jumlah_penduduk_miskin = db.Column(db.String(50), nullable=True)
    presentase_penduduk_miskin = db.Column(db.String(50), nullable=True)
    indeks_kedalaman_kemiskinan = db.Column(db.String(50), nullable=True)
    indeks_keparahan_kemiskinan = db.Column(db.String(50), nullable=True)
    gini_rasio = db.Column(db.String(50), nullable=True)

def handle_none(value):
    """Mengganti nilai None atau undefined dengan nilai default."""
    if value is None or value == 'undefined':
        return ''  # Ganti dengan string kosong atau nilai default lainnya
    return value

@app.route('/api/data-kemiskinan', methods=['GET'])
def get_data_kemiskinan():
    try:
        results = Kemiskinan.query.all()

        data = [
            {
                'tahun': record.tahun,
                'presentase_penduduk_miskin': handle_none(record.presentase_penduduk_miskin)
            }
            for record in results
        ]
        
        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Load Model dan KMeans
model_name = "models/fine_tuned_gpt_neo_poverty_lens"
tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
model = AutoModelForCausalLM.from_pretrained(model_name, local_files_only=True)

model_img_path = "models/img_processing/img_model.joblib"
kmeans_loaded = joblib.load(model_img_path)

# Kategori dan Warna Overlay
categories = {
    "Lahan Terbangun": [194, 187, 181],
    "Lahan Kosong": [242, 239, 232],
    "Jalan Arteri": [255, 174, 185],
    "Rel Kereta": [119, 105, 102],
    "Jalan Biasa": [255, 255, 255],
    "Perairan": [174, 210, 221],
    "Lapangan": [201, 249, 203],
    "Perhutanan": [165, 197, 159],
}
overlay_colors = {
    "Lahan Terbangun": [0, 255, 0],
    "Lahan Kosong": [255, 255, 0],
    "Jalan Arteri": [255, 105, 180],
    "Rel Kereta": [255, 140, 0],
    "Jalan Biasa": [128, 128, 128],
    "Perairan": [0, 255, 255],
    "Lapangan": [144, 238, 144],
    "Perhutanan": [34, 139, 34],
}
tolerance = 60

def assign_category(color, categories, tolerance):
    min_distance = float("inf")
    best_category = "Tidak Dikenal"
    for category, reference_color in categories.items():
        distance = np.sqrt(np.sum((np.array(color) - np.array(reference_color)) ** 2))
        if distance < min_distance and distance < tolerance:
            min_distance = distance
            best_category = category
    return best_category

@app.route("/process", methods=["POST"])
def process_image():
    data = request.form.get("image")
    if not data:
        return jsonify({"error": "No image provided"}), 400

    try:
        image_data = base64.b64decode(data.split(",")[1])
        image = Image.open(BytesIO(image_data))
        image = np.array(image)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)

        pixel_values = image_rgb.reshape((-1, 3))
        pixel_values = np.float32(pixel_values)

        labels = kmeans_loaded.predict(pixel_values)
        centers = np.uint8(kmeans_loaded.cluster_centers_)

        overlay_image = np.zeros_like(image_rgb)
        category_counts = {category: 0 for category in categories.keys()}
        total_pixels = pixel_values.shape[0]

        for i, color in enumerate(centers):
            category = assign_category(color, categories, tolerance)
            color_overlay = overlay_colors.get(category, [0, 0, 0])
            category_mask = (labels == i)
            overlay_image[category_mask.reshape(image_rgb.shape[:2])] = color_overlay
            if category in category_counts:
                category_counts[category] += np.sum(category_mask)

        category_percentages = {
            category: (count / total_pixels) * 100 for category, count in category_counts.items()
        }

        overlay_image_pil = Image.fromarray(overlay_image)
        buffered = BytesIO()
        overlay_image_pil.save(buffered, format="PNG")
        overlay_base64 = base64.b64encode(buffered.getvalue()).decode()

        return jsonify({"overlay_image": overlay_base64, "percentages": category_percentages})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generate_response(input_text, max_new_tokens=100):
    prompt = (
        "Anda adalah asisten cerdas PovertyLens, aplikasi pemetaan kemiskinan. "
        "Jawaban Anda harus singkat, jelas, dan hanya fokus pada informasi yang relevan dengan kemiskinan, pemetaan sosial, atau bantuan sosial. "
        "Jangan berikan informasi umum atau yang tidak terkait.\n\n"
        
        "Contoh Pertanyaan dan Jawaban:\n"
        "Pertanyaan: Apa itu kemiskinan absolut?\n"
        "Jawab: Kemiskinan absolut adalah keadaan hidup di bawah garis kemiskinan dengan akses yang sangat terbatas ke kebutuhan dasar.\n\n"
        
        "Pertanyaan: Bagaimana aplikasi ini membantu menemukan lokasi bantuan sosial?\n"
        "Jawab: Aplikasi ini menunjukkan peta lembaga bantuan sosial terdekat yang dapat diakses oleh masyarakat.\n\n"
        
        "Pertanyaan: {input_text}\nJawab:"
    )
    
    inputs = tokenizer(prompt.format(input_text=input_text), return_tensors="pt", padding=True, truncation=True, max_length=350)
    
    outputs = model.generate(
        inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        max_new_tokens=max_new_tokens,
        do_sample=False,
        temperature=0.0,
        top_k=10,
        top_p=0.5,
        pad_token_id=tokenizer.eos_token_id
    )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
    
    if not response or len(response.split()) < 3:
        response = "Maaf, saya tidak dapat memahami pertanyaan Anda. Bisa dijelaskan lebih lanjut?"
    
    keywords = ["kemiskinan", "bantuan", "pemetaan", "sosial", "ekonomi"]
    if not any(keyword in response.lower() for keyword in keywords):
        response = "Informasi yang relevan tidak ditemukan. Silakan ajukan pertanyaan yang lebih spesifik."

    response_lines = response.split('.')
    response = '. '.join([line for line in response_lines if any(keyword in line.lower() for keyword in keywords)])
    
    if not response:
        response = "Jawaban tidak tersedia. Pastikan pertanyaan Anda terkait dengan kemiskinan atau bantuan sosial."

    return response

@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    bot_response = generate_response(user_message)
    return jsonify(response=bot_response)

@app.route('/')
def index():
    try:
        # Ambil data tahun dan presentase_penduduk_miskin
        results = Kemiskinan.query.all()

        # Siapkan data untuk dikirim ke template
        tahun = [record.tahun for record in results]
        presentase_penduduk_miskin = [
            handle_none(record.presentase_penduduk_miskin) for record in results
        ]

        return render_template('index.html', tahun=tahun, presentase_penduduk_miskin=presentase_penduduk_miskin)
    
    except Exception as e:
        return str(e), 500

@app.route("/pindai-wilayah")
def pindaiWilayah():
    return render_template("pindai-wilayah.html")

@app.route("/daftar-lembaga")
def dtLembaga():
    lembaga_data = Lembaga.query.all()
    return render_template("dt-lembaga.html", lembaga_data=lembaga_data)

@app.route("/detail-lembaga/<int:lembaga_id>")
def detailLembaga(lembaga_id):
    try:
        lembaga = Lembaga.query.get(lembaga_id)
        if lembaga is None or lembaga.detail is None:
            return "Lembaga tidak ditemukan", 404
        
        detail = lembaga.detail
        return render_template('detail-lembaga.html', detail=detail)
    except Exception as e:
        return str(e)

@app.route("/rekap-data")
def rekapData():
    return render_template("rekap-data.html")

# API Endpoints

@app.route("/api/lembaga", methods=['GET'])
def get_lembaga():
    try:
        lembaga_data = Lembaga.query.all()
        lembaga_list = [{
            'id': lembaga.id,
            'nama': lembaga.nama,
            'logo_url': lembaga.logo_url
        } for lembaga in lembaga_data]
        return jsonify(lembaga_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/detail-lembaga/<int:lembaga_id>", methods=['GET'])
def api_detail_lembaga(lembaga_id):
    try:
        lembaga = Lembaga.query.get(lembaga_id)
        if lembaga is None or lembaga.detail is None:
            return jsonify({'error': 'Lembaga tidak ditemukan'}), 404
        
        detail = lembaga.detail
        detail_dict = {
            'nama': lembaga.nama,
            'logo_url': lembaga.logo_url,
            'alamat_kantor': detail.alamat_kantor,
            'telepon': detail.telepon,
            'email': detail.email,
            'web_resmi': detail.web_resmi,
            'deskripsi': detail.deskripsi,
            'informasi': detail.informasi
        }
        return jsonify(detail_dict)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
