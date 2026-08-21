# Rizal Portfolio

Fondasi website portofolio pribadi multilingual berbasis Flask. Proyek ini disiapkan untuk menampilkan Home, Projects, CV, dan Blog dalam bahasa Indonesia, Inggris, serta Jepang, dengan area admin yang akan dikembangkan secara bertahap.

Status saat ini masih **Foundation/MVP awal**. Halaman publik dasar dan autentikasi Admin sudah tersedia. CRUD konten, upload, API key, serta translation database belum diimplementasikan.

## Teknologi

- Python 3.12
- Flask 3
- SQLAlchemy 2 melalui Flask-SQLAlchemy
- Flask-Migrate/Alembic
- SQLite
- Jinja, semantic HTML, CSS, dan JavaScript vanilla
- pytest

## Arsitektur

MVP menggunakan **modular monolith** dengan `app.py` sebagai entry point tipis dan `create_app()` sebagai application factory.

Boundary utama:

- `public_web`: halaman yang dapat diakses pengunjung;
- `admin_web`: fondasi antarmuka admin;
- `api/public`: API publik read-only;
- `api/admin`: namespace API admin tanpa write endpoint sebelum autentikasi tersedia;
- `domains/content`: boundary untuk Home, Projects, Blog, navigation, media, dan CV;
- `domains/identity_access`: boundary untuk user admin, role, session, dan API access;
- `shared`: layout, error handling, request ID, security headers, dan design tokens.

Public dan Admin dipisahkan pada level Blueprint, template, dan static assets, tetapi masih berjalan dalam satu aplikasi dan satu deployment. Satu aplikasi menjadi satu-satunya pemilik file SQLite.

Penjelasan arsitektur lengkap tersedia di [Portfolio Flask Agent Architecture Blueprint](docs/architecture/Portfolio_Flask_Agent_Architecture_Blueprint.md).

## Prasyarat

- Python `3.12.x`
- Git
- PowerShell untuk command Windows di bawah

Pastikan Python yang digunakan benar:

```powershell
py -3.12 --version
```

## Instalasi lokal

Jalankan dari root repository.

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
Copy-Item .env.example .env
```

### macOS/Linux

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
cp .env.example .env
```

## Konfigurasi environment

Edit `.env` setelah menyalin `.env.example`:

```dotenv
APP_ENV=development
SECRET_KEY=
DATABASE_URL=
STORAGE_ROOT=
MAX_CONTENT_LENGTH=16777216
AUTH_SESSION_LIFETIME_SECONDS=28800
LOGIN_RATE_LIMIT_MAX_ATTEMPTS=5
LOGIN_RATE_LIMIT_WINDOW_SECONDS=900
```

Keterangan:

- `APP_ENV`: `development`, `testing`, atau `production`;
- `SECRET_KEY`: secret lokal yang kuat; jangan commit nilainya;
- `DATABASE_URL`: kosong pada development untuk memakai `instance/portfolio.sqlite3`;
- `STORAGE_ROOT`: kosong pada development untuk memakai folder `storage/`;
- `MAX_CONTENT_LENGTH`: batas request/upload dalam byte, default 16 MiB.
- `AUTH_SESSION_LIFETIME_SECONDS`: masa berlaku session Admin, default 8 jam;
- `LOGIN_RATE_LIMIT_MAX_ATTEMPTS`: jumlah gagal login yang diizinkan dalam satu window, default 5;
- `LOGIN_RATE_LIMIT_WINDOW_SECONDS`: panjang window rate limit login, default 15 menit.

Untuk membuat secret development:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Salin hasilnya ke `SECRET_KEY` dalam `.env`. Production tidak akan start bila secret, database URI, atau storage path tidak dikonfigurasi secara eksplisit.

## Menjalankan project

Aktifkan virtual environment, lalu jalankan:

```powershell
python -m flask --app app run --host 127.0.0.1 --port 5000 --no-debugger --no-reload
```

Buka:

- Website: <http://127.0.0.1:5000/>
- Health API: <http://127.0.0.1:5000/api/v1/public/health>
- Login Admin: <http://127.0.0.1:5000/login> (diakses langsung, tidak ada di navigasi publik)

Command alternatif untuk development interaktif:

```powershell
python app.py
```

`python app.py` mengaktifkan konfigurasi development, termasuk debugger/reloader Flask. Jangan gunakan development server untuk production.

## Route yang tersedia

| Method | Route | Keterangan |
|---|---|---|
| `GET` | `/` | Home foundation |
| `GET` | `/projects` | Projects placeholder |
| `GET` | `/cv` | CV placeholder |
| `GET` | `/blog` | Blog placeholder |
| `GET` | `/login` | Form login Admin |
| `POST` | `/login` | Verifikasi credential dan membuat session baru |
| `GET` | `/admin/dashboard` | Dashboard minimum; wajib session valid |
| `POST` | `/logout` | Mencabut session backend dan menghapus cookie |
| `GET` | `/api/v1/public/health` | Health response publik |
| `GET` | `/api/v1/admin` | Wajib session valid; status `501` karena write API belum tersedia |

Untuk melihat route map langsung:

```powershell
python -m flask --app app routes
```

## Database dan migrasi

Revision `20260820_01` menambahkan `admin_user`, `auth_session`, dan `security_audit_event`. Jalankan migration sebelum membuat Admin:

```powershell
python -m flask --app app db upgrade
```

Migration tidak membuat credential default dan tidak menyimpan password.

## Membuat Admin awal

Setelah migration selesai, buat Admin melalui prompt tersembunyi (password tidak menjadi argumen CLI atau shell history):

```powershell
python -m flask --app app create-admin --email muhammadrizalm0109@gmail.com
```

Password minimum 12 karakter dan harus memuat huruf kecil, huruf besar, angka, serta simbol. Command menolak email duplikat tanpa menimpa hash existing.

## Desain session Admin

- Browser menyimpan raw session token hanya dalam cookie session Flask yang `HttpOnly`, `SameSite=Lax`, dan `Path=/`; mode production juga menetapkan `Secure`.
- Database hanya menyimpan SHA-256 token, expiration, last-seen, dan waktu pencabutan.
- Login membersihkan browser session sebelumnya, membuat token acak baru, dan mencabut token lama browser tersebut bila masih ada.
- Session pada perangkat lain tetap aktif sampai logout dari perangkat itu, kedaluwarsa, Admin dinonaktifkan, atau dicabut oleh proses administratif di masa depan.
- Login dan Dashboard mengirim `Cache-Control: no-store`; logout mencabut record backend lalu membuat cookie kedaluwarsa.
- Rate limit menggunakan security audit records yang persisten pada database aplikasi, dihitung per hash alamat sumber; alamat lengkap dan credential tidak disimpan.

Untuk membuat revision schema berikutnya:

Setelah model pertama ditambahkan pada tahap berikutnya:

```powershell
python -m flask --app app db migrate -m "Describe schema change"
python -m flask --app app db upgrade
```

Jangan memakai `db.create_all()` sebagai strategi migrasi production. File SQLite berada di `instance/` dan tidak boleh masuk Git.

## Menjalankan test

```powershell
python -m pytest
```

Pemeriksaan syntax tambahan:

```powershell
python -m compileall -q app.py portfolio tests migrations
```

Test foundation mencakup:

- application factory;
- isolasi testing database;
- route Home, Projects, CV, dan Blog;
- admin/API boundary;
- health endpoint;
- safe `404` dan `500` responses;
- production configuration yang fail-closed.

## Struktur ringkas

```text
app.py
pyproject.toml
migrations/
portfolio/
  public_web/
  admin_web/
  api/
  domains/
    content/
    identity_access/
  shared/
tests/
instance/       # runtime, diabaikan Git
storage/        # media/CV runtime, diabaikan Git
```

## Batas fitur saat ini

Belum tersedia:

- role Owner/Editor dan pengelolaan session lintas perangkat;
- admin CRUD dan draft/publish;
- data Projects, Blog, Home, navigation, dan CV;
- translation database dan locale routing;
- upload gambar/PDF;
- API key management;
- production WSGI server, container, atau deployment.

Tahap berikutnya yang direkomendasikan adalah secure Home vertical slice: role/permission, Home revision/translation, Editor draft, Owner publish, public published-only reads, dan test keamanan terkait.

## Keamanan repository

Jangan commit:

- `.env` atau secret;
- `.venv`;
- SQLite database;
- media/CV upload;
- backup dan log runtime.

Aturan tersebut sudah tercantum dalam `.gitignore`.
