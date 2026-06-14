# GroomX v6 — Flask + MongoDB Backend

```
groomx_backend/
├── app.py                   ← Flask entry point  (run this)
├── requirements.txt         ← Python dependencies
├── .env.example             ← Copy to .env and fill in
├── config/
│   ├── settings.py          ← App config (MongoDB URI, secrets…)
│   └── database.py          ← PyMongo init + seed data
├── routes/
│   ├── auth.py              ← /api/auth/*
│   ├── bookings.py          ← /api/bookings/*
│   ├── home_visits.py       ← /api/home-visits/*
│   ├── beard_styles.py      ← /api/beard-styles/*
│   ├── salons.py            ← /api/salons/*
│   ├── ai_scans.py          ← /api/ai-scans/*
│   └── dashboard.py         ← /api/dashboard/*
├── utils.py                 ← JWT, bcrypt, helpers
├── static/
│   └── groomx_api.js        ← Drop into your frontend folder
└── templates/
    └── index.html           ← (optional) serve frontend from Flask
```

---

## 1 — Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.9+ | python.org |
| MongoDB | 6+ | mongodb.com/try/download/community |
| pip | latest | bundled with Python |

---

## 2 — Setup

```bash
# 1. Open the groomx_backend folder in VS Code
cd groomx_backend

# 2. Create a virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your .env file
cp .env.example .env
# Edit .env — at minimum set MONGO_URI if not using localhost

# 5. Make sure MongoDB is running
# Windows: start the MongoDB service in Services panel
# Mac:     brew services start mongodb-community
# Linux:   sudo systemctl start mongod
```

---

## 3 — Run the Server

```bash
python app.py
```

You should see:
```
==================================================
  GroomX v6 Backend Starting...
  http://localhost:5000
==================================================
  ✦ MongoDB connected successfully
  ✦ Database seeded with demo data
```

Open http://localhost:5000 in your browser to confirm the API is running.

---

## 4 — Connect the Frontend

**Option A — Serve the frontend from Flask (recommended):**

Copy your `groomx_v6.html` into the `templates/` folder and rename it `index.html`.

Then add this line just before `</body>` in `index.html`:
```html
<script src="/static/groomx_api.js"></script>
```

Now visit http://localhost:5000 — Flask serves the frontend AND the API.

**Option B — Open the HTML file directly:**

Add this line before `</body>` in `groomx_v6.html`:
```html
<script src="groomx_api.js"></script>
```

Copy `static/groomx_api.js` next to `groomx_v6.html` and open the HTML file in Chrome.

> The API client will show a banner if the backend is unreachable, and gracefully fall back to the built-in localStorage mode.

---

## 5 — Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Customer | customer@groomx.com | pass123 |
| Owner    | admin@groomx.com    | admin123 |

Or use the **Customer Demo** / **Salon Owner Demo** buttons on the login screen.

---

## 6 — API Reference

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Create account |
| POST | /api/auth/login | Sign in → get token |
| GET  | /api/auth/me | Current user info |
| POST | /api/auth/demo | Demo login (body: `{"role":"customer"}`) |
| POST | /api/auth/logout | Sign out |

### Bookings
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | /api/bookings/ | List bookings |
| POST | /api/bookings/ | Create booking |
| GET  | /api/bookings/{id} | Get one booking |
| PATCH| /api/bookings/{id} | Update status |
| DELETE | /api/bookings/{id} | Delete |
| GET  | /api/bookings/slots?date=&stylist= | Available slots |

### Home Visits
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | /api/home-visits/ | List visits |
| POST | /api/home-visits/ | Create visit |
| GET  | /api/home-visits/{id} | Get one |
| PATCH| /api/home-visits/{id} | Update |
| DELETE | /api/home-visits/{id} | Cancel |
| GET  | /api/home-visits/calculate-fee?distance_km=&service= | Fee calculator |

### Beard Styles
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/beard-styles/ | All styles (optional: ?category=classic) |
| GET | /api/beard-styles/{id} | Single style |

### Salons
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | /api/salons/ | List salons (filter: open, home_visit, min_rating) |
| GET  | /api/salons/{id} | Single salon |
| PATCH| /api/salons/{id} | Update (owner only) |

### Dashboard (owner only)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | /api/dashboard/stats | Key metrics |
| GET  | /api/dashboard/charts | Chart data |
| GET  | /api/dashboard/pending | Pending queue |
| POST | /api/dashboard/pending/{id}/accept | Accept |
| POST | /api/dashboard/pending/{id}/decline | Decline |

---

## 7 — MongoDB Collections

| Collection | Description |
|------------|-------------|
| `users` | Registered accounts |
| `bookings` | Studio bookings |
| `home_visits` | Doorstep appointments |
| `beard_styles` | 16 beard style catalogue |
| `salons` | 8 Nagpur salon locations |
| `ai_scans` | Face analysis logs |

View data in **MongoDB Compass** → connect to `mongodb://localhost:27017` → select `groomx_db`.

---

## 8 — Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | (set this!) | Flask session secret |
| `MONGO_URI` | `mongodb://localhost:27017/groomx_db` | MongoDB connection |
| `JWT_SECRET` | (set this!) | JWT signing key |
| `ANTHROPIC_API_KEY` | — | For server-side AI (optional) |
| `DEBUG` | `True` | Flask debug mode |

---

## 9 — Troubleshooting

**MongoDB connection error:**
```
Make sure MongoDB is running:
  Windows: Open Services → MongoDB → Start
  Mac:     brew services start mongodb-community
  Linux:   sudo systemctl start mongod
```

**Port 5000 already in use:**
```bash
# Change the port in app.py:
app.run(debug=True, host="0.0.0.0", port=5001)
# And update BASE in groomx_api.js:
BASE: "http://localhost:5001/api"
```

**CORS error in browser:**
```
The backend already allows all origins in dev mode.
If still getting CORS errors, check that Flask-CORS is installed:
  pip install flask-cors
```

**ModuleNotFoundError:**
```bash
# Make sure your virtual environment is activated:
venv\Scripts\activate    # Windows
source venv/bin/activate # Mac/Linux
pip install -r requirements.txt
```
