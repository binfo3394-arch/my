# 📱 ST Mobile & Designing — POS v19
### Flask + SQLite Real Web App

---

## 🚀 Quick Start

### Windows
```
START-WINDOWS.bat ➜ double-click කරන්න
```
Browser open කරලා: **http://localhost:5000**

### Linux / Mac
```bash
chmod +x START-LINUX-MAC.sh
./START-LINUX-MAC.sh
```

---

## 📁 File Structure

```
st-pos-webapp/
├── app.py                 ← Flask backend (server)
├── database.db            ← SQLite database (auto-created)
├── requirements.txt       ← Python dependencies
├── START-WINDOWS.bat      ← Windows start script
├── START-LINUX-MAC.sh     ← Linux/Mac start script
├── templates/
│   └── index.html         ← Frontend (UI)
└── README.md
```

---

## 🛠️ Manual Install

```bash
# 1. Python install (https://python.org)

# 2. Flask install
pip install flask

# 3. Server start
python app.py

# 4. Browser open
# http://localhost:5000
```

---

## ✨ Features

| Section | Features |
|---------|----------|
| 🏠 Dashboard | Revenue, Sales, Repairs, Orders stats + Charts |
| 🛒 POS | Cart, Barcode scan, Multiple payments |
| 📦 Inventory | Products, Stock tracking, Low stock alerts |
| 🔧 Repairs | Job tracking, Status updates, Bills |
| 🌐 Online Orders | Multi-item orders, Payment tracking |
| 👥 Customers | Customer database, History |
| 🧾 Invoices | PDF/PNG export, Thermal print |
| 📊 Analytics | Revenue charts, Best sellers |
| 💳 Credit Sales | Installments, Payment schedule |
| 🏭 Suppliers | Supplier management, Purchase orders |
| 📋 Stock History | All stock movements |
| ⚙️ Settings | Shop info, PIN lock, Theme, Backup |

---

## 💾 Data Backup

**Settings page** ➜ **Data Backup** section:
- **Download .db** — SQLite file (complete backup)
- **Restore .db** — Upload previous backup
- **Export JSON** — JSON format backup
- **Import JSON** — Restore from JSON

Database file location: `database.db` (same folder as app.py)

---

## 🔐 PIN Lock

Settings ➜ PIN Lock ➜ 4-digit PIN set කරන්න

---

## 🌐 Network Access (LAN)

Local network eke වෙනත් devices වලින් access කරන්න:

1. `app.py` open කරන්න
2. `app.run(host='0.0.0.0')` — already set
3. Computer IP address find කරන්න:
   - Windows: `ipconfig` 
   - Linux/Mac: `ifconfig`
4. Phone/tablet browser: `http://YOUR-IP:5000`

---

## 🔧 Tech Stack

- **Backend**: Python Flask
- **Database**: SQLite (real file — `database.db`)
- **Frontend**: Pure HTML + CSS + JavaScript
- **Charts**: Chart.js
- **PDF/PNG**: html2canvas

---

## 📱 Mobile Install (PWA)

Android Chrome:
1. http://YOUR-IP:5000 open කරන්න
2. Menu (⋮) → Add to Home Screen

iOS Safari:
1. http://YOUR-IP:5000 open කරන්න
2. Share → Add to Home Screen

---

*ST Mobile & Designing POS v19 — Flask Edition*
