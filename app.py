from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, make_response, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import joblib
import base64
import cv2
import datetime
import pytz


# ppp
from models.model import initialize_llm, initialize_embeddings, initialize_vectorstore, create_rag_chain
from langchain_community.document_loaders import PyPDFLoader
# ppp


from sklearn.feature_extraction.text import CountVectorizer
from datetime import datetime, timezone
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import joinedload
from io import BytesIO
from PIL import Image
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import numpy as np
import os

from flask_migrate import Migrate

app = Flask(__name__)

# ppp
GROQ_API_KEY = "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"
PDF_FILE_PATH = os.path.join(os.path.dirname(__file__), "data/dataset_poverty2.pdf")
# ppp


CORS(app)
WIB = pytz.timezone('Asia/Jakarta')
CSV_FOLDER = os.path.join(app.root_path, 'static', 'csv')

# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://A3CP:S.Tr.Kom2024@194.31.53.102/A3CP"
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://21wQtGdq5xU1Jzz.root:2KXHciu6kxinKNEW@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/povertylens"
)

app.config["SQLALCHEMY_DATABASE_URI"] += "?ssl_ca=C:/tidb_ca/isrgrootx1.pem"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['DEBUG'] = True
app.config.update(
    SECRET_KEY='povertylens',
    SESSION_COOKIE_NAME='session',  # Nama cookie sesi
    SESSION_COOKIE_HTTPONLY=True,   # Pastikan cookie tidak bisa diakses melalui JavaScript
    SESSION_COOKIE_SECURE=False     # Jika aplikasi Anda tidak menggunakan HTTPS, set False
)
app.secret_key = 'povertylens'


db = SQLAlchemy(app)
migrate = Migrate(app, db)

### MODEL DB
### MODEL DB
### MODEL DB
### MODEL DB

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

class Ulasan(db.Model):
    __tablename__ = 'ulasan_pengguna'
    
    id = db.Column(db.Integer, primary_key=True)
    ulasan = db.Column(db.Text, nullable=False)
    label = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return f"<Ulasan {self.id}: {self.ulasan[:20]}...>"

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
    nama_lengkap = db.Column(db.Text, nullable=True)
    kategori = db.Column(db.String(255), nullable=True)

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

class DataPopulasi(db.Model):
    __tablename__ = 'data_populasi'
    id = db.Column(db.Integer, primary_key=True)
    kelurahan = db.Column(db.String(255), nullable=False)
    populasi = db.Column(db.Integer, nullable=False)
    luas_wilayah = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<DataPopulasi {self.kelurahan}, {self.populasi}, {self.luas_wilayah}>"


def handle_none(value):
    """Mengganti nilai None atau undefined dengan nilai default."""
    if value is None or value == 'undefined':
        return ''
    return value

### CHATBOT
### CHATBOT
### CHATBOT
### CHATBOT

def initialize_rag_model():
    """Initialize the RAG model and vector store retriever."""
    try:
        # Initialize LLM and embeddings
        llm = initialize_llm(GROQ_API_KEY)
        embeddings = initialize_embeddings()

        # Load and process PDF documents
        pdf_loader = PyPDFLoader(PDF_FILE_PATH)
        documents = pdf_loader.load()

        # Initialize vector store retriever
        retriever = initialize_vectorstore(documents, embeddings)
        app.config['llm'] = llm
        app.config['retriever'] = retriever
        print("Model and retriever initialized successfully.")
    except Exception as e:
        print(f"Error initializing model: {e}")
        raise e

@app.before_request
def setup_model():
    """Ensure model is initialized before the first request."""
    if 'llm' not in app.config or 'retriever' not in app.config:
        initialize_rag_model()

@app.route('/send_message', methods=['GET'])
def get_response():
    message = request.args.get('msg')

    # Check if message is present
    if not message:
        return "No input received."

    # Ensure model and retriever are initialized
    llm = app.config.get('llm')
    retriever = app.config.get('retriever')
    
    if not llm or not retriever:
        return "Model or retriever is not initialized."

    try:
        # Create the RAG chain with the retriever and llm
        rag_chain = create_rag_chain(retriever, llm)
        response = rag_chain.invoke({"input": message})
        return response['answer']
    except Exception as e:
        return f"Error: {e}"


# model_name = "models/save_model_chatbot"
# tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
# model = AutoModelForCausalLM.from_pretrained(model_name, local_files_only=True)

# def generate_response(input_text, max_new_tokens=100):
#     prompt = (  
#         "Pertanyaan: {input_text}\nJawab:"
#     )
#     inputs = tokenizer(prompt.format(input_text=input_text), return_tensors="pt", padding=True, truncation=True, max_length=350)   
#     outputs = model.generate(
#         inputs["input_ids"],
#         attention_mask=inputs["attention_mask"],
#         max_new_tokens=max_new_tokens,
#         do_sample=False,
#         temperature=0.0,
#         top_k=10,
#         top_p=0.5,
#         pad_token_id=tokenizer.eos_token_id
#     )  
#     response = tokenizer.decode(outputs[0], skip_special_tokens=True).strip() 
#     if not response or len(response.split()) < 3:
#         response = "Maaf, saya tidak dapat memahami pertanyaan Anda. Bisa dijelaskan lebih lanjut?"
#     keywords = ["kemiskinan", "bantuan", "pemetaan", "sosial", "ekonomi"]
#     if not any(keyword in response.lower() for keyword in keywords):
#         response = "Informasi yang relevan tidak ditemukan. Silakan ajukan pertanyaan yang lebih spesifik."
#     response_lines = response.split('.')
#     response = '. '.join([line for line in response_lines if any(keyword in line.lower() for keyword in keywords)])
#     if not response:
#         response = "Jawaban tidak tersedia. Pastikan pertanyaan Anda terkait dengan kemiskinan atau bantuan sosial."
#     return response

# @app.route('/send_message', methods=['POST'])
# def send_message():
#     user_message = request.json.get('message')
#     if not user_message:
#         return jsonify({'error': 'No message provided'}), 400
#     bot_response = generate_response(user_message)
#     return jsonify(response=bot_response)



### BATAS
### IMAGE PROCESSING
### IMAGE PROCESSING
### IMAGE PROCESSING
### IMAGE PROCESSING

model_img_path = "models/img_processing/img_model.joblib"
kmeans_loaded = joblib.load(model_img_path)

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
    "Lahan Terbangun": [210, 180, 140],
    "Lahan Kosong": [152, 251, 152],
    "Jalan Arteri": [255, 160, 122],
    "Rel Kereta": [210, 105, 30],
    "Jalan Biasa": [192, 192, 192],
    "Perairan": [176, 224, 230],
    "Lapangan": [144, 238, 144],
    "Perhutanan": [85, 107, 47]
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
    
### WEB ROUTE
### WEB ROUTE
### WEB ROUTE
### WEB ROUTE

@app.route('/')
def index():
    try:
        ulasan_results = Ulasan.query.filter_by(label='positif').order_by(Ulasan.created_at.desc()).limit(3).all()
        
        ulasan_data = [{
            'ulasan': ulasan.ulasan,
            'created_at': ulasan.created_at
        } for ulasan in ulasan_results]

        results = Kemiskinan.query.all()
        tahun = [record.tahun for record in results]
        presentase_penduduk_miskin = [
            handle_none(record.presentase_penduduk_miskin) for record in results
        ]
        
        return render_template('index.html', 
                               tahun=tahun, 
                               presentase_penduduk_miskin=presentase_penduduk_miskin, 
                               ulasan_data=ulasan_data)
    except Exception as e:
        return str(e), 500

model_sentimen = joblib.load('models/model_sentimen_nb.pkl')
vectorizer = joblib.load('models/vectorizer.pkl')

@app.route('/add_ulasan', methods=['POST'])
def add_ulasan():
    ulasan_text = request.form.get('ulasan')
    email = request.form.get('email')
    
    if not ulasan_text:
        flash("Ulasan tidak ditemukan!", "error")
        return redirect(url_for('index'))
    if not email:
        flash("Email tidak ditemukan!", "error")
        return redirect(url_for('index'))
    
    ulasan_vec = vectorizer.transform([ulasan_text])
    label_prediksi = model_sentimen.predict(ulasan_vec)
    label = 'positif' if label_prediksi[0] == 1 else 'negatif'
    
    ulasan_baru = Ulasan(ulasan=ulasan_text, label=label, email=email)
    db.session.add(ulasan_baru)
    db.session.commit()

    flash("Ulasan berhasil ditambahkan!", "success")
    
    return redirect(url_for('index'))

@app.route("/pindai-wilayah")
def pindaiWilayah():
    return render_template("pindai-wilayah.html")

@app.route("/get_populasi", methods=["GET"])
def get_populasi():
    kelurahan_name = request.args.get("kelurahan").lower()

    data_kelurahan = DataPopulasi.query.filter(func.lower(DataPopulasi.kelurahan) == kelurahan_name).first()

    if not data_kelurahan:
        return jsonify({"error": "Kelurahan tidak ditemukan"}), 404

    populasi = data_kelurahan.populasi
    return jsonify({"kelurahan": kelurahan_name, "populasi": populasi})

@app.route('/get_lembaga', methods=['GET'])
def get_lembag_output():
    kategori = request.args.get('bantuan').lower()

    lembaga = DetailLembaga.query.filter(DetailLembaga.kategori.ilike(kategori)).all()

    result = []
    for lembaga_item in lembaga:
        result.append({
            "nama": lembaga_item.nama_lengkap,
            "alamat": lembaga_item.alamat_kantor,
            "telepon": lembaga_item.telepon,
            "web": lembaga_item.web_resmi
        })

    return jsonify({"lembaga": result})


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

@app.route("/rekap-data", methods=["GET"])
def rekapData():
    selected_range = request.args.get("tahun", "2021-2023")
    start_year, end_year = map(int, selected_range.split('-'))
    data = Kemiskinan.query.filter(Kemiskinan.tahun >= start_year, Kemiskinan.tahun <= end_year).all()
    return render_template("rekap-data.html", data=data, selected_range=selected_range)


@app.route("/rekap-data-ajax", methods=["GET"])
def rekap_data_ajax():
    selected_range = request.args.get("tahun", "2021-2023")
    start_year, end_year = map(int, selected_range.split('-'))
    data = Kemiskinan.query.filter(Kemiskinan.tahun >= start_year, Kemiskinan.tahun <= end_year).all()
    result = [
        {
            "tahun": row.tahun,
            "garis_kemiskinan": row.garis_kemiskinan,
            "jumlah_penduduk_miskin": row.jumlah_penduduk_miskin,
            "presentase_penduduk_miskin": row.presentase_penduduk_miskin,
            "indeks_kedalaman_kemiskinan": row.indeks_kedalaman_kemiskinan,
            "indeks_keparahan_kemiskinan": row.indeks_keparahan_kemiskinan,
            "gini_rasio": row.gini_rasio
        }
        for row in data
    ]
    return jsonify(result)

@app.route("/download-csv", methods=["GET"])
def download_csv():
    selected_range = request.args.get("tahun", "2021-2023")
    file_name = f"Kemiskinan, {selected_range}.csv"
    file_path = os.path.join(CSV_FOLDER, file_name)
    if os.path.exists(file_path):
        return send_from_directory(CSV_FOLDER, file_name, as_attachment=True)
    else:
        return "File tidak ditemukan", 404


### API ENDPOINTS
### API ENDPOINTS
### API ENDPOINTS
### API ENDPOINTS

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
            'nama_lengkap': detail.nama_lengkap,
            'deskripsi': detail.deskripsi,
            'informasi': detail.informasi
        }
        return jsonify(detail_dict)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
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

### ADMIN
### ADMIN
### ADMIN
### ADMIN

admin_registered = False

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        password_hash = generate_password_hash(password)
        new_user = User(username=username, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()
        session['logged_in'] = True
        return redirect(url_for('admin'))
    return render_template("admin/register.html")

@app.route("/KGDgwkfjOD")
def admin_login():
    return render_template("admin/login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return "Login failed, username atau password salah."

    return render_template("admin/login.html")

@app.route("/logout")
def logout():
    # Hapus sesi pengguna
    session.pop('logged_in', None)  # Hapus 'logged_in' dari sesi
    session.clear()  # Hapus seluruh data sesi

    # Buat response redirect ke halaman login
    response = redirect(url_for('login'))

    # Hapus cookie sesi jika ada
    response.delete_cookie('session')  # Menghapus cookie sesi jika diset sebelumnya

    # Menambahkan header untuk mencegah cache pada browser
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response


@app.route("/IRyTFqXOuY")
def admin():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
    
    ulasan_positif = db.session.query(Ulasan).filter(Ulasan.label == 'positif').order_by(Ulasan.created_at.desc()).all()
    ulasan_negatif = db.session.query(Ulasan).filter(Ulasan.label == 'negatif').order_by(Ulasan.created_at.desc()).all()

    positif_count = len(ulasan_positif)
    negatif_count = len(ulasan_negatif)
    return render_template("admin/admin.html",
                           positif_count=positif_count, 
                           negatif_count=negatif_count, 
                           ulasan_positif=ulasan_positif, 
                           ulasan_negatif=ulasan_negatif)

@app.route("/QGZCbFyb5Rj")
def data_lembaga():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
    lembagas = Lembaga.query.options(joinedload(Lembaga.detail)).all()
    return render_template("admin/data-lembaga.html", lembagas=lembagas)

@app.route("/qH4BcxHm8", methods =['GET', 'POST'])
def add_lembaga():
    if request.method == 'POST':
        nama = request.form.get('nama')
        logo_url = request.form.get('logo_url')
        alamat_kantor = request.form.get('alamat_kantor')
        telepon = request.form.get('telepon')
        email = request.form.get('email')
        web_resmi = request.form.get('web_resmi')
        deskripsi = request.form.get('deskripsi')
        informasi = request.form.get('informasi')
        nama_lengkap = request.form.get('nama_lengkap')

        detail_lembaga = DetailLembaga(
            alamat_kantor=alamat_kantor,
            telepon=telepon,
            email=email,
            web_resmi=web_resmi,
            deskripsi=deskripsi,
            informasi=informasi,
            nama_lengkap=nama_lengkap
        )
        lembaga = Lembaga(
            nama=nama,
            logo_url=logo_url,
            detail=detail_lembaga
        )

        db.session.add(lembaga)
        db.session.commit()
        flash('Data lembaga berhasil ditambahkan!', 'success')
        return redirect(url_for('data_lembaga'))
    return render_template("admin/add-lembaga.html")

@app.route('/edit-lembaga/<int:id>', methods=['GET', 'POST'])
def edit_lembaga(id):
    lembaga = Lembaga.query.get_or_404(id)
    detail_lembaga = lembaga.detail
    if request.method == 'POST':
        if 'nama' in request.form:
            lembaga.nama = request.form['nama']
        if 'logo_url' in request.form:
            lembaga.logo_url = request.form['logo_url']
        if 'alamat_kantor' in request.form:
            detail_lembaga.alamat_kantor = request.form['alamat_kantor']
        if 'telepon' in request.form:
            detail_lembaga.telepon = request.form['telepon']
        if 'email' in request.form:
            detail_lembaga.email = request.form['email']
        if 'web_resmi' in request.form:
            detail_lembaga.web_resmi = request.form['web_resmi']
        if 'deskripsi' in request.form:
            detail_lembaga.deskripsi = request.form['deskripsi']
        if 'informasi' in request.form:
            detail_lembaga.informasi = request.form['informasi']
        if 'nama_lengkap' in request.form:
            detail_lembaga.nama_lengkap = request.form['nama_lengkap']

        db.session.commit()
        flash('Data lembaga berhasil diperbarui!', 'success')
        return redirect(url_for('data_lembaga'))

    return render_template('admin/edit-lembaga.html', lembaga=lembaga, detail_lembaga=detail_lembaga)

@app.route('/delete_lembaga/<int:id>', methods=['GET'])
def delete_lembaga(id):
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
    lembaga = Lembaga.query.get(id)
    db.session.delete(lembaga)
    db.session.commit()
    return redirect(url_for('data_lembaga'))

### RUN APP
### RUN APP
### RUN APP
### RUN APP

if __name__ == "__main__":
    app.run(port=5000, debug=True)
