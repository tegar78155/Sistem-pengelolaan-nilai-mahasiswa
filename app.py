from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os

app = Flask(__name__)
app.secret_key = 'rahasia'  # Ganti dengan kunci rahasia di produksi

# Dummy login
USERNAME = "admin"
PASSWORD = "admin123"

# Load dan simpan data
def load_data():
    if not os.path.exists("data"):
        os.makedirs("data")
    if os.path.exists("data/data.json"):
        with open("data/data.json", "r") as f:
            return json.load(f)
    return {"mahasiswa": [], "nilai": [], "ekskul": []}

def simpan_data(data):
    with open("data/data.json", "w") as f:
        json.dump(data, f, indent=4)

# ------------------------
# Login
# ------------------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_input = request.form['username']
        password_input = request.form['password']

        if username_input == USERNAME and password_input == PASSWORD:
            session['user'] = username_input
            return redirect(url_for('dashboard'))
        else:
            flash("Username atau password salah!")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# ------------------------
# Dashboard
# ------------------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    data = load_data()
    mahasiswa = data["mahasiswa"]
    nilai = data["nilai"]

    total_mahasiswa = len(mahasiswa)
    total_matkul = len(set([n['matakuliah'] for n in nilai]))
    rata_nilai = round(sum([n['nilai'] for n in nilai]) / len(nilai), 2) if nilai else 0

    return render_template('dashboard.html',
                           total_mahasiswa=total_mahasiswa,
                           total_matkul=total_matkul,
                           rata_nilai=rata_nilai)

# ------------------------
# Mahasiswa
# ------------------------
@app.route('/mahasiswa')
def kelola_mahasiswa():
    if 'user' not in session:
        return redirect(url_for('login'))

    data = load_data()
    return render_template("mahasiswa.html", mahasiswa=data['mahasiswa'])

@app.route('/tambah_mahasiswa', methods=['POST'])
def tambah_mahasiswa():
    if 'user' not in session:
        return redirect(url_for('login'))

    nama = request.form['nama']
    nim = request.form['nim']

    data = load_data()
    mahasiswa = data['mahasiswa']

    # Validasi NIM unik
    if any(m['nim'] == nim for m in mahasiswa):
        flash("NIM sudah digunakan!")
        return redirect(url_for('kelola_mahasiswa'))

    new_id = max([m['id'] for m in mahasiswa], default=0) + 1
    mahasiswa.append({"id": new_id, "nama": nama, "nim": nim})
    simpan_data(data)
    return redirect(url_for('kelola_mahasiswa'))

@app.route('/hapus_mahasiswa/<int:id>')
def hapus_mahasiswa(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    data = load_data()
    data['mahasiswa'] = [m for m in data['mahasiswa'] if m['id'] != id]
    data['nilai'] = [n for n in data['nilai'] if n['id_mahasiswa'] != id]
    simpan_data(data)
    return redirect(url_for('kelola_mahasiswa'))

# ------------------------
# Nilai
# ------------------------
@app.route('/nilai', methods=['GET'])
def kelola_nilai():
    if 'user' not in session:
        return redirect(url_for('login'))

    data = load_data()
    mahasiswa = data['mahasiswa']
    nilai = data['nilai']

    id_mhs = request.args.get('id_mahasiswa')
    selected_mhs = None
    nilai_mhs = []
    rata_rata = 0

    if id_mhs:
        id_mhs = int(id_mhs)
        selected_mhs = next((m for m in mahasiswa if m['id'] == id_mhs), None)
        nilai_mhs = [n for n in nilai if n['id_mahasiswa'] == id_mhs]
        if nilai_mhs:
            rata_rata = round(sum(n['nilai'] for n in nilai_mhs) / len(nilai_mhs), 2)

    return render_template('nilai.html',
                           mahasiswa=mahasiswa,
                           selected_mhs=selected_mhs,
                           selected_id=id_mhs,
                           nilai=nilai_mhs,
                           rata_nilai=rata_rata)

@app.route('/tambah_nilai/<int:id_mahasiswa>', methods=['POST'])
def tambah_nilai(id_mahasiswa):
    if 'user' not in session:
        return redirect(url_for('login'))

    matkul = request.form['matakuliah']
    nilai = int(request.form['nilai'])

    data = load_data()
    id_baru = max([n['id'] for n in data['nilai']], default=0) + 1
    data['nilai'].append({
        "id": id_baru,
        "id_mahasiswa": id_mahasiswa,
        "matakuliah": matkul,
        "nilai": nilai
    })
    simpan_data(data)
    return redirect(url_for('kelola_nilai', id_mahasiswa=id_mahasiswa))

@app.route('/hapus_nilai/<int:id>')
def hapus_nilai(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    data = load_data()
    nilai = data['nilai']
    nilai_dihapus = next((n for n in nilai if n['id'] == id), None)

    if nilai_dihapus:
        id_mhs = nilai_dihapus['id_mahasiswa']
        data['nilai'] = [n for n in nilai if n['id'] != id]
        simpan_data(data)
        return redirect(url_for('kelola_nilai', id_mahasiswa=id_mhs))
    return redirect(url_for('kelola_nilai'))

# ------------------------
# Ekstrakurikuler
# ------------------------
@app.route('/ekskul')
def ekstrakurikuler():
    if 'user' not in session:
        return redirect(url_for('login'))

    data = load_data()
    ekskul = data.get("ekskul", [])
    return render_template("ekstrakurikuler.html", ekskul=ekskul)

@app.route('/tambah_ekskul', methods=['POST'])
def tambah_ekskul():
    if 'user' not in session:
        return redirect(url_for('login'))

    nama = request.form['nama']
    pembina = request.form['pembina']
    data = load_data()

    new_id = max([e['id'] for e in data.get('ekskul', [])], default=0) + 1
    if "ekskul" not in data:
        data["ekskul"] = []

    data["ekskul"].append({"id": new_id, "nama": nama, "pembina": pembina})
    simpan_data(data)
    return redirect(url_for('ekstrakurikuler'))

@app.route('/hapus_ekskul/<int:id>')
def hapus_ekskul(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    data = load_data()
    data["ekskul"] = [e for e in data.get("ekskul", []) if e['id'] != id]
    simpan_data(data)
    return redirect(url_for('ekstrakurikuler'))

# ------------------------
# Jalankan Aplikasi
# ------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
