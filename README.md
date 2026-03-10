# 🖼 Placeholder Image Service

A fast, fully-featured placeholder image generator with a REST API and a polished Web UI.  
Built with **FastAPI**, **Pillow**, and **Docker**.

---

## ✨ Features

| Feature | Details |
|---|---|
| **Custom size** | Any width × height up to 5000 px |
| **Solid background** | Any HEX color |
| **Linear gradient** | 2–5 color stops, any angle (0–360°) |
| **Text overlay** | Custom text, color, font size (or auto), centered |
| **Output formats** | PNG · JPEG · WebP |
| **Direct URL** | Embed as `<img src="/api/gen?...">` |
| **Download** | One-click file download |

---

## 🚀 Quick Start

### Option A — Docker Compose (recommended)

```bash
git clone https://github.com/YOUR_USER/placeholder-service.git
cd placeholder-service
docker compose up --build
```

Open **http://localhost:8000** in your browser.

---

### Option B — Local Python

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## 📡 API Reference

### `GET /api/gen`

Generate a placeholder image. All parameters are optional.

| Param | Type | Default | Description |
|---|---|---|---|
| `w` | int | 400 | Width in pixels |
| `h` | int | 300 | Height in pixels |
| `bg` | string | `cccccc` | Background HEX (no `#`) |
| `gradient` | bool | false | Enable gradient |
| `gc` | string | `4facfe,00f2fe` | Gradient colors (comma-separated HEX) |
| `ga` | int | 135 | Gradient angle in degrees |
| `text` | string | `{w}×{h}` | Overlay text |
| `tc` | string | `333333` | Text color HEX |
| `fs` | int | 0 | Font size (0 = auto) |
| `fmt` | string | `PNG` | Output format: `PNG`, `JPEG`, `WEBP` |
| `q` | int | 90 | JPEG/WebP quality (1–100) |
| `download` | bool | false | Force file download |

#### Examples

```html
<!-- Simple size label -->
<img src="http://localhost:8000/api/gen?w=800&h=600" />

<!-- Custom text & color -->
<img src="http://localhost:8000/api/gen?w=400&h=200&text=Hello&bg=1a1a2e&tc=ffffff" />

<!-- Gradient -->
<img src="http://localhost:8000/api/gen?w=600&h=400&gradient=true&gc=ff6b6b,ffd93d,6bcb77&ga=45" />

<!-- JPEG download -->
<a href="http://localhost:8000/api/gen?w=1920&h=1080&fmt=JPEG&download=true">Download</a>
```

---

## 🗂 Project Structure

```
placeholder-service/
├── app/
│   ├── main.py               # FastAPI app + routes
│   ├── api/
│   │   └── routes.py         # GET /api/gen endpoint
│   ├── core/
│   │   └── generator.py      # Pillow image generation logic
│   ├── templates/
│   │   └── index.html        # Jinja2 + TailwindCSS UI
│   └── static/               # Static assets (optional)
├── tests/
│   └── test_service.py       # pytest unit & API tests
├── .github/
│   └── workflows/
│       └── ci.yml            # GitHub Actions CI/CD
├── Dockerfile                # Multi-stage build
├── docker-compose.yml
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🧪 Running Tests

```bash
pip install pytest httpx
pytest tests/ -v
```

---

## 🐳 Docker Details

The `Dockerfile` uses a **multi-stage build**:

1. **`builder`** — installs all Python dependencies into `/venv`  
2. **`runtime`** — copies only the venv + app source; no build tools

This keeps the final image lean (~180 MB vs ~450 MB).

---

## 📄 License

MIT
