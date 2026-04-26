# VerbQuest 🎯

> An interactive English irregular verbs learning app built with Django.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Django](https://img.shields.io/badge/Django-5.x-green?style=flat-square&logo=django)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## ✨ Features

- 🎮 **Interactive quiz** — Practice Past Simple, Past Participle, or both
- ⚡ **Instant feedback** — Sound effects and color-coded results per answer
- 📊 **Score tracking** — Every session saved to the database
- 👤 **Personalized results** — Player name and score percentage shown at the end
- 🔐 **Admin panel** — Manage verbs and view all session history
- 📱 **Mobile-friendly** — Responsive design for all screen sizes

---

## 📸 Pages

| Route | Description |
|---|---|
| `/` | Main game (Landing → Setup → Quiz → Results) |
| `/admin-panel/login/` | Custom admin login |
| `/admin-panel/` | Dashboard — stats overview |
| `/admin-panel/verbs/` | Add / delete irregular verbs |
| `/admin-panel/sessions/` | View all completed sessions |
| `/api/verbs/` | JSON API — returns all verbs |
| `/api/save-session/` | POST — saves a completed session |
| `/django-admin/` | Django built-in admin |

---

## 🚀 Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/verbquest.git
cd verbquest

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate        # Linux / Mac
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply database migrations
python manage.py migrate

# 5. Seed the database with 66 irregular verbs
python manage.py seed_verbs

# 6. Create a superuser (admin account)
python manage.py createsuperuser

# 7. Start the development server
python manage.py runserver
```

Open **http://127.0.0.1:8000** in your browser.

Admin panel: **http://127.0.0.1:8000/admin-panel/login/**

---

## 🌐 Production Deployment (Nginx + Gunicorn)

### 1. Install production dependencies

```bash
pip install gunicorn psycopg2-binary
```

### 2. Update `settings.py`

```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.uz', 'your-server-ip']
SECRET_KEY = 'your-strong-random-secret-key'

# PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'verbquest_db',
        'USER': 'verbquest_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 3. Collect static files

```bash
python manage.py collectstatic
```

### 4. Gunicorn systemd service

Create `/etc/systemd/system/verbquest.service`:

```ini
[Unit]
Description=VerbQuest Gunicorn Daemon
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/verbquest
ExecStart=/var/www/verbquest/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/run/verbquest.sock \
          verbquest.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable verbquest
sudo systemctl start verbquest
```

### 5. Nginx config

```nginx
server {
    listen 80;
    server_name your-domain.uz;

    location /static/ {
        alias /var/www/verbquest/staticfiles/;
    }

    location / {
        proxy_pass http://unix:/run/verbquest.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 6. SSL with Certbot

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.uz
```

---

## 📁 Project Structure

```
verbquest/
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── verbquest/                  # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── game/                       # Main application
│   ├── models.py               # IrregularVerb, GameSession
│   ├── views.py                # Game views + Admin panel views
│   ├── urls.py
│   ├── admin.py
│   └── management/
│       └── commands/
│           └── seed_verbs.py   # python manage.py seed_verbs
│
├── templates/
│   ├── game/
│   │   └── index.html          # SPA — the full game UI
│   └── admin_panel/
│       ├── base.html
│       ├── login.html
│       ├── dashboard.html
│       ├── verbs.html
│       └── sessions.html
│
└── static/
    ├── css/
    │   ├── verbquest.css       # Game styles
    │   └── admin_panel.css     # Admin styles
    └── js/
        └── verbquest.js        # Game logic + API calls
```

---

## 🗄️ Database Models

### `IrregularVerb`
| Field | Type | Description |
|---|---|---|
| `base` | CharField | Base form — e.g. `go` |
| `past` | CharField | Past Simple — e.g. `went` |
| `pp` | CharField | Past Participle — e.g. `gone` |
| `created_at` | DateTimeField | Auto timestamp |

### `GameSession`
| Field | Type | Description |
|---|---|---|
| `player_name` | CharField | Name entered by the user |
| `mode` | CharField | `past`, `pp`, or `both` |
| `total` | IntegerField | Total questions answered |
| `correct` | IntegerField | Number of correct answers |
| `wrong` | IntegerField | Number of wrong answers |
| `score_pct` | IntegerField | Score percentage (0–100) |
| `played_at` | DateTimeField | Auto timestamp |

---

## 🔧 Management Commands

```bash
# Seed 66 common irregular verbs into the database
python manage.py seed_verbs
```

---

## 🛠️ Tech Stack

- **Backend:** Django 5.x, Python 3.10+
- **Database:** SQLite (dev) / PostgreSQL (production)
- **Frontend:** Vanilla HTML + CSS + JavaScript (SPA)
- **Fonts:** Nunito, Space Mono (Google Fonts)
- **Server:** Gunicorn + Nginx

---

## 📄 License

MIT License — free to use, modify, and distribute.