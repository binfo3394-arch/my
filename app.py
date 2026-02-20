#!/usr/bin/env python3
"""
ST Mobile & Designing — POS v19
Flask Backend with SQLite File Database
"""

from flask import Flask, jsonify, request, render_template, send_file, g
import sqlite3, os, json, io
from datetime import datetime

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

# ─── DB CONNECTION ───────────────────────────────────────────
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db: db.close()

def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY, value TEXT
        );
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY, name TEXT, category TEXT,
            price REAL, cost REAL, stock INTEGER, minStock INTEGER, description TEXT
        );
        CREATE TABLE IF NOT EXISTS repairs (
            id INTEGER PRIMARY KEY, customer TEXT, phone TEXT, device TEXT,
            issue TEXT, cost REAL, advance REAL, status TEXT,
            date TEXT, dueDate TEXT, notes TEXT, techNotes TEXT
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY, customer TEXT, phone TEXT, platform TEXT,
            service TEXT, amount REAL, delivery REAL, advance REAL,
            status TEXT, paymentStatus TEXT, date TEXT, dueDate TEXT,
            notes TEXT, items TEXT, payments TEXT
        );
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY, name TEXT, phone TEXT, email TEXT,
            address TEXT, notes TEXT, joined TEXT
        );
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY, invNo TEXT, customer TEXT, items TEXT,
            subtotal REAL, discount REAL, tax REAL, total REAL,
            payment TEXT, date TEXT, note TEXT
        );
        CREATE TABLE IF NOT EXISTS credits (
            id INTEGER PRIMARY KEY, customer TEXT, phone TEXT, nic TEXT,
            item TEXT, total REAL, down REAL, balance REAL, perInst REAL,
            instCount INTEGER, freq TEXT, schedule TEXT, payments TEXT,
            status TEXT, date TEXT, notes TEXT
        );
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY, name TEXT, phone TEXT, email TEXT,
            category TEXT, address TEXT, notes TEXT
        );
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY, supId INTEGER, supName TEXT,
            prodId INTEGER, prodName TEXT, qty INTEGER, cost REAL,
            date TEXT, status TEXT, notes TEXT
        );
        CREATE TABLE IF NOT EXISTS stock_log (
            id INTEGER PRIMARY KEY, prodId INTEGER, prodName TEXT,
            type TEXT, change INTEGER, stockAfter INTEGER, ref TEXT, date TEXT
        );
        CREATE TABLE IF NOT EXISTS pin_store (
            id INTEGER PRIMARY KEY, pin TEXT
        );
    """)
    db.commit()
    db.close()

# ─── HELPERS ─────────────────────────────────────────────────
def row_to_dict(row):
    return dict(row) if row else None

def rows_to_list(rows):
    return [dict(r) for r in rows]

def safe_json(val, default=None):
    if default is None: default = []
    try:
        return json.loads(val) if val else default
    except:
        return default

def ts():
    return int(datetime.now().timestamp() * 1000)

# ─── MAIN PAGE ───────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

# ─── SETTINGS ────────────────────────────────────────────────
@app.route('/api/settings', methods=['GET'])
def get_settings():
    db = get_db()
    rows = db.execute("SELECT key, value FROM settings").fetchall()
    result = {}
    for r in rows:
        try: result[r['key']] = json.loads(r['value'])
        except: result[r['key']] = r['value']
    return jsonify(result)

@app.route('/api/settings', methods=['POST'])
def save_settings():
    db = get_db()
    data = request.json
    for k, v in data.items():
        db.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)",
                   [k, json.dumps(v)])
    db.commit()
    return jsonify({'ok': True})

# ─── PRODUCTS ────────────────────────────────────────────────
@app.route('/api/products', methods=['GET'])
def get_products():
    db = get_db()
    rows = db.execute("SELECT * FROM products ORDER BY name").fetchall()
    return jsonify(rows_to_list(rows))

@app.route('/api/products', methods=['POST'])
def save_product():
    db = get_db()
    d = request.json
    pid = d.get('id') or ts()
    db.execute("INSERT OR REPLACE INTO products VALUES(?,?,?,?,?,?,?,?)",
               [pid, d.get('name',''), d.get('category','Other'),
                d.get('price',0), d.get('cost',0),
                d.get('stock',0), d.get('minStock',2), d.get('desc','')])
    db.commit()
    return jsonify({'ok': True, 'id': pid})

@app.route('/api/products/<int:pid>', methods=['DELETE'])
def delete_product(pid):
    db = get_db()
    db.execute("DELETE FROM products WHERE id=?", [pid])
    db.commit()
    return jsonify({'ok': True})

@app.route('/api/products/<int:pid>/stock', methods=['PATCH'])
def update_stock(pid):
    db = get_db()
    d = request.json
    db.execute("UPDATE products SET stock=? WHERE id=?", [d['stock'], pid])
    db.commit()
    return jsonify({'ok': True})

# ─── REPAIRS ─────────────────────────────────────────────────
@app.route('/api/repairs', methods=['GET'])
def get_repairs():
    db = get_db()
    rows = db.execute("SELECT * FROM repairs ORDER BY id DESC").fetchall()
    return jsonify(rows_to_list(rows))

@app.route('/api/repairs', methods=['POST'])
def save_repair():
    db = get_db()
    d = request.json
    rid = d.get('id') or ts()
    db.execute("INSERT OR REPLACE INTO repairs VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
               [rid, d.get('customer',''), d.get('phone',''), d.get('device',''),
                d.get('issue',''), d.get('cost',0), d.get('advance',0),
                d.get('status','Pending'), d.get('date',''), d.get('dueDate',''),
                d.get('notes',''), d.get('techNotes','')])
    db.commit()
    return jsonify({'ok': True, 'id': rid})

@app.route('/api/repairs/<int:rid>', methods=['DELETE'])
def delete_repair(rid):
    db = get_db()
    db.execute("DELETE FROM repairs WHERE id=?", [rid])
    db.commit()
    return jsonify({'ok': True})

@app.route('/api/repairs/<int:rid>/status', methods=['PATCH'])
def update_repair_status(rid):
    db = get_db()
    d = request.json
    db.execute("UPDATE repairs SET status=? WHERE id=?", [d['status'], rid])
    db.commit()
    return jsonify({'ok': True})

# ─── ORDERS ──────────────────────────────────────────────────
@app.route('/api/orders', methods=['GET'])
def get_orders():
    db = get_db()
    rows = db.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    result = []
    for r in rows:
        o = dict(r)
        o['items'] = safe_json(o.get('items'))
        o['payments'] = safe_json(o.get('payments'))
        result.append(o)
    return jsonify(result)

@app.route('/api/orders', methods=['POST'])
def save_order():
    db = get_db()
    d = request.json
    oid = d.get('id') or ts()
    db.execute("INSERT OR REPLACE INTO orders VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
               [oid, d.get('customer',''), d.get('phone',''), d.get('platform',''),
                d.get('service',''), d.get('amount',0), d.get('delivery',0),
                d.get('advance',0), d.get('status','Received'),
                d.get('paymentStatus','Unpaid'), d.get('date',''), d.get('dueDate',''),
                d.get('notes',''), json.dumps(d.get('items',[])),
                json.dumps(d.get('payments',[]))])
    db.commit()
    return jsonify({'ok': True, 'id': oid})

@app.route('/api/orders/<int:oid>', methods=['DELETE'])
def delete_order(oid):
    db = get_db()
    db.execute("DELETE FROM orders WHERE id=?", [oid])
    db.commit()
    return jsonify({'ok': True})

@app.route('/api/orders/<int:oid>/status', methods=['PATCH'])
def update_order_status(oid):
    db = get_db()
    d = request.json
    db.execute("UPDATE orders SET status=?,paymentStatus=? WHERE id=?",
               [d.get('status'), d.get('paymentStatus'), oid])
    db.commit()
    return jsonify({'ok': True})

# ─── CUSTOMERS ───────────────────────────────────────────────
@app.route('/api/customers', methods=['GET'])
def get_customers():
    db = get_db()
    rows = db.execute("SELECT * FROM customers ORDER BY name").fetchall()
    return jsonify(rows_to_list(rows))

@app.route('/api/customers', methods=['POST'])
def save_customer():
    db = get_db()
    d = request.json
    cid = d.get('id') or ts()
    db.execute("INSERT OR REPLACE INTO customers VALUES(?,?,?,?,?,?,?)",
               [cid, d.get('name',''), d.get('phone',''), d.get('email',''),
                d.get('address',''), d.get('notes',''), d.get('joined','')])
    db.commit()
    return jsonify({'ok': True, 'id': cid})

@app.route('/api/customers/<int:cid>', methods=['DELETE'])
def delete_customer(cid):
    db = get_db()
    db.execute("DELETE FROM customers WHERE id=?", [cid])
    db.commit()
    return jsonify({'ok': True})

# ─── INVOICES ────────────────────────────────────────────────
@app.route('/api/invoices', methods=['GET'])
def get_invoices():
    db = get_db()
    rows = db.execute("SELECT * FROM invoices ORDER BY id DESC").fetchall()
    result = []
    for r in rows:
        inv = dict(r)
        inv['items'] = safe_json(inv.get('items'))
        result.append(inv)
    return jsonify(result)

@app.route('/api/invoices', methods=['POST'])
def save_invoice():
    db = get_db()
    d = request.json
    iid = d.get('id') or ts()
    db.execute("INSERT OR REPLACE INTO invoices VALUES(?,?,?,?,?,?,?,?,?,?,?)",
               [iid, d.get('invNo',''), d.get('customer',''),
                json.dumps(d.get('items',[])), d.get('subtotal',0),
                d.get('discount',0), d.get('tax',0), d.get('total',0),
                d.get('payment',''), d.get('date',''), d.get('note','')])
    # Update product stocks
    for item in d.get('items', []):
        pid = item.get('id')
        qty = item.get('qty', 0)
        if pid:
            db.execute("UPDATE products SET stock = MAX(0, stock - ?) WHERE id=?", [qty, pid])
    db.commit()
    return jsonify({'ok': True, 'id': iid})

@app.route('/api/invoices/clear', methods=['DELETE'])
def clear_invoices():
    db = get_db()
    db.execute("DELETE FROM invoices")
    db.commit()
    return jsonify({'ok': True})

# ─── CREDITS ─────────────────────────────────────────────────
@app.route('/api/credits', methods=['GET'])
def get_credits():
    db = get_db()
    rows = db.execute("SELECT * FROM credits ORDER BY id DESC").fetchall()
    result = []
    for r in rows:
        c = dict(r)
        c['schedule'] = safe_json(c.get('schedule'))
        c['payments'] = safe_json(c.get('payments'))
        result.append(c)
    return jsonify(result)

@app.route('/api/credits', methods=['POST'])
def save_credit():
    db = get_db()
    d = request.json
    cid = d.get('id') or ts()
    db.execute("INSERT OR REPLACE INTO credits VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
               [cid, d.get('customer',''), d.get('phone',''), d.get('nic',''),
                d.get('item',''), d.get('total',0), d.get('down',0),
                d.get('balance',0), d.get('perInst',0), d.get('instCount',1),
                d.get('freq','monthly'), json.dumps(d.get('schedule',[])),
                json.dumps(d.get('payments',[])), d.get('status','Active'),
                d.get('date',''), d.get('notes','')])
    db.commit()
    return jsonify({'ok': True, 'id': cid})

@app.route('/api/credits/<int:cid>', methods=['PATCH'])
def update_credit(cid):
    db = get_db()
    d = request.json
    db.execute("UPDATE credits SET balance=?, payments=?, status=? WHERE id=?",
               [d.get('balance',0), json.dumps(d.get('payments',[])),
                d.get('status','Active'), cid])
    db.commit()
    return jsonify({'ok': True})

@app.route('/api/credits/<int:cid>', methods=['DELETE'])
def delete_credit(cid):
    db = get_db()
    db.execute("DELETE FROM credits WHERE id=?", [cid])
    db.commit()
    return jsonify({'ok': True})

# ─── SUPPLIERS ───────────────────────────────────────────────
@app.route('/api/suppliers', methods=['GET'])
def get_suppliers():
    db = get_db()
    rows = db.execute("SELECT * FROM suppliers ORDER BY name").fetchall()
    return jsonify(rows_to_list(rows))

@app.route('/api/suppliers', methods=['POST'])
def save_supplier():
    db = get_db()
    d = request.json
    sid = d.get('id') or ts()
    db.execute("INSERT OR REPLACE INTO suppliers VALUES(?,?,?,?,?,?,?)",
               [sid, d.get('name',''), d.get('phone',''), d.get('email',''),
                d.get('category',''), d.get('address',''), d.get('notes','')])
    db.commit()
    return jsonify({'ok': True, 'id': sid})

@app.route('/api/suppliers/<int:sid>', methods=['DELETE'])
def delete_supplier(sid):
    db = get_db()
    db.execute("DELETE FROM suppliers WHERE id=?", [sid])
    db.commit()
    return jsonify({'ok': True})

# ─── PURCHASES ───────────────────────────────────────────────
@app.route('/api/purchases', methods=['GET'])
def get_purchases():
    db = get_db()
    rows = db.execute("SELECT * FROM purchases ORDER BY id DESC").fetchall()
    return jsonify(rows_to_list(rows))

@app.route('/api/purchases', methods=['POST'])
def save_purchase():
    db = get_db()
    d = request.json
    pid = d.get('id') or ts()
    db.execute("INSERT OR REPLACE INTO purchases VALUES(?,?,?,?,?,?,?,?,?,?)",
               [pid, d.get('supId',0), d.get('supName',''),
                d.get('prodId',0), d.get('prodName',''), d.get('qty',0),
                d.get('cost',0), d.get('date',''), d.get('status','Ordered'),
                d.get('notes','')])
    if d.get('status') == 'Received':
        db.execute("UPDATE products SET stock = stock + ? WHERE id=?",
                   [d.get('qty',0), d.get('prodId',0)])
    db.commit()
    return jsonify({'ok': True, 'id': pid})

@app.route('/api/purchases/<int:pid>/receive', methods=['PATCH'])
def receive_purchase(pid):
    db = get_db()
    po = db.execute("SELECT * FROM purchases WHERE id=?", [pid]).fetchone()
    if po and po['status'] == 'Ordered':
        db.execute("UPDATE purchases SET status='Received' WHERE id=?", [pid])
        db.execute("UPDATE products SET stock = stock + ? WHERE id=?",
                   [po['qty'], po['prodId']])
        db.commit()
    return jsonify({'ok': True})

# ─── STOCK LOG ───────────────────────────────────────────────
@app.route('/api/stock_log', methods=['GET'])
def get_stock_log():
    db = get_db()
    rows = db.execute("SELECT * FROM stock_log ORDER BY id DESC LIMIT 500").fetchall()
    return jsonify(rows_to_list(rows))

@app.route('/api/stock_log', methods=['POST'])
def add_stock_log():
    db = get_db()
    d = request.json
    db.execute("INSERT INTO stock_log VALUES(?,?,?,?,?,?,?,?)",
               [ts(), d.get('prodId',0), d.get('prodName',''),
                d.get('type',''), d.get('change',0), d.get('stockAfter',0),
                d.get('ref',''), d.get('date','')])
    db.commit()
    return jsonify({'ok': True})

# ─── PIN ─────────────────────────────────────────────────────
@app.route('/api/pin', methods=['GET'])
def get_pin():
    db = get_db()
    r = db.execute("SELECT pin FROM pin_store WHERE id=1").fetchone()
    return jsonify({'pin': r['pin'] if r else None})

@app.route('/api/pin', methods=['POST'])
def set_pin():
    db = get_db()
    pin = request.json.get('pin')
    if pin:
        db.execute("INSERT OR REPLACE INTO pin_store(id,pin) VALUES(1,?)", [pin])
    else:
        db.execute("DELETE FROM pin_store WHERE id=1")
    db.commit()
    return jsonify({'ok': True})

# ─── DATABASE DOWNLOAD ───────────────────────────────────────
@app.route('/api/db/download')
def download_db():
    return send_file(DB_PATH, as_attachment=True,
                     download_name=f'ST-POS-{datetime.now().strftime("%Y-%m-%d")}.db',
                     mimetype='application/octet-stream')

@app.route('/api/db/upload', methods=['POST'])
def upload_db():
    f = request.files.get('file')
    if not f: return jsonify({'ok': False, 'msg': 'No file'}), 400
    f.save(DB_PATH)
    return jsonify({'ok': True})

# ─── CLEAR DATA ──────────────────────────────────────────────
@app.route('/api/clear/<table>', methods=['DELETE'])
def clear_table(table):
    allowed = ['invoices','repairs','orders','credits','purchases','stock_log']
    if table == 'all':
        db = get_db()
        for t in allowed + ['products','customers','suppliers']:
            db.execute(f"DELETE FROM {t}")
        db.commit()
        return jsonify({'ok': True})
    if table not in allowed:
        return jsonify({'ok': False}), 400
    db = get_db()
    db.execute(f"DELETE FROM {table}")
    db.commit()
    return jsonify({'ok': True})

# ─── BULK LOAD ALL DATA ──────────────────────────────────────
@app.route('/api/all', methods=['GET'])
def get_all():
    """Load all data in one request for fast startup"""
    db = get_db()
    def q(sql): return [dict(r) for r in db.execute(sql).fetchall()]

    settings = {}
    for r in db.execute("SELECT key, value FROM settings").fetchall():
        try: settings[r['key']] = json.loads(r['value'])
        except: settings[r['key']] = r['value']

    orders = q("SELECT * FROM orders ORDER BY id DESC")
    for o in orders:
        o['items'] = safe_json(o.get('items'))
        o['payments'] = safe_json(o.get('payments'))

    invoices = q("SELECT * FROM invoices ORDER BY id DESC")
    for inv in invoices:
        inv['items'] = safe_json(inv.get('items'))

    credits = q("SELECT * FROM credits ORDER BY id DESC")
    for c in credits:
        c['schedule'] = safe_json(c.get('schedule'))
        c['payments'] = safe_json(c.get('payments'))

    pin_row = db.execute("SELECT pin FROM pin_store WHERE id=1").fetchone()

    return jsonify({
        'settings': settings,
        'products': q("SELECT * FROM products ORDER BY name"),
        'repairs': q("SELECT * FROM repairs ORDER BY id DESC"),
        'orders': orders,
        'customers': q("SELECT * FROM customers ORDER BY name"),
        'invoices': invoices,
        'credits': credits,
        'suppliers': q("SELECT * FROM suppliers ORDER BY name"),
        'purchases': q("SELECT * FROM purchases ORDER BY id DESC"),
        'stockLog': q("SELECT * FROM stock_log ORDER BY id DESC LIMIT 500"),
        'pin': pin_row['pin'] if pin_row else None
    })

if __name__ == '__main__':
    init_db()
    print("✅ ST Mobile POS — Server starting...")
    print("🌐 Open: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
