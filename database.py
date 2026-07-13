import sqlite3
import pandas as pd
import os

# Database path fix: Data hamesha script ke folder mein save hoga
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "factory_backup.db")

def get_connection():
    """Local SQLite Database Connection"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"❌ Database Connection Error: {e}")
        return None

def init_db():
    """Tables initialization schema for SQLite with tracking layers"""
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()
    
    # 1. Inventory Table (Finished Goods)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT UNIQUE,
            packing TEXT,
            category TEXT,
            unit TEXT,
            safety_stock INTEGER,
            current_stock INTEGER DEFAULT 0
        );
    """)
    
    # 2. Materials Table (Universal Store for Dept Materials, Cartons, Reels)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            material_name TEXT UNIQUE,
            department TEXT,
            unit TEXT,
            current_stock REAL DEFAULT 0.0
        );
    """)

    # 3. Materials Historical Logs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS material_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            material_name TEXT,
            department TEXT,
            action_type TEXT,
            quantity REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # 4. Customers Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT UNIQUE,
            phone TEXT,
            email TEXT DEFAULT 'N/A',
            address TEXT
        );
    """)
    
    # 5. Orders Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            item_name TEXT,
            qty_ordered INTEGER DEFAULT 0,
            qty_to_produce INTEGER DEFAULT 0,
            status TEXT DEFAULT 'Pending Production',
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 6. NEW: System Users Management Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,          -- 'Master', 'Secondary', 'Worker'
            assigned_dept TEXT           -- 'All', 'Raw Material', 'Empty Carton', 'Paper Reels'
        );
    """)
    
    # Default admin user agar exist nahi karta tu create karein
    cursor.execute("SELECT * FROM system_users WHERE username='admin';")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO system_users (username, password, role, assigned_dept) 
            VALUES ('admin', 'admin123', 'Master', 'All');
        """)
        
    conn.commit()
    cursor.close()
    conn.close()

# --- NEW: SYSTEM USERS FUNCTIONS ---
def fetch_all_users():
    conn = get_connection()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM system_users ORDER BY username ASC;")
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    cursor.close()
    conn.close()
    return data

def insert_user(username, password, role, assigned_dept):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO system_users (username, password, role, assigned_dept) 
            VALUES (?, ?, ?, ?);
        """, (username, password, role, assigned_dept))
        conn.commit()
        cursor.close()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def update_user(user_id, username, password, role, assigned_dept):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE system_users 
            SET username=?, password=?, role=?, assigned_dept=? 
            WHERE id=?;
        """, (username, password, role, assigned_dept, user_id))
        conn.commit()
        cursor.close()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def delete_user(user_id):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM system_users WHERE id=?;", (user_id,))
        conn.commit()
        cursor.close()
        return True
    except Exception:
        return False
    finally:
        conn.close()

# --- NEW: EDIT & DELETE BACKEND FUNCTIONS FOR CHARTS/LOGS ---
def delete_inventory_item(item_id):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventory WHERE id=?;", (item_id,))
        conn.commit()
        cursor.close()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def update_inventory_item(item_id, item_name, packing, category, unit, safety_stock, current_stock):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE inventory 
            SET item_name=?, packing=?, category=?, unit=?, safety_stock=?, current_stock=? 
            WHERE id=?;
        """, (item_name, packing, category, unit, safety_stock, current_stock, item_id))
        conn.commit()
        cursor.close()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def delete_material_item(mat_id):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM materials WHERE id=?;", (mat_id,))
        conn.commit()
        cursor.close()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def update_material_item(mat_id, material_name, current_stock, unit):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE materials 
            SET material_name=?, current_stock=?, unit=? 
            WHERE id=?;
        """, (material_name, current_stock, unit, mat_id))
        conn.commit()
        cursor.close()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def delete_material_log(log_id):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM material_logs WHERE id=?;", (log_id,))
        conn.commit()
        cursor.close()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def delete_customer(cust_id):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM customers WHERE id=?;", (cust_id,))
        conn.commit()
        cursor.close()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def delete_order_record(order_id):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders WHERE id=?;", (order_id,))
        conn.commit()
        cursor.close()
        return True
    except Exception:
        return False
    finally:
        conn.close()

# --- OLD & ORIGINAL CORE FUNCTIONS (RETAINED PERFECTLY) ---
def fetch_materials_by_dept(dept_name):
    conn = get_connection()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM materials WHERE department = ? ORDER BY material_name ASC;", (dept_name,))
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    cursor.close()
    conn.close()
    return data

def fetch_all_materials():
    """Fetch all materials from all departments"""
    conn = get_connection()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM materials ORDER BY department, material_name ASC;")
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    cursor.close()
    conn.close()
    return data

def insert_or_update_material(mat_name, dept_name, unit_type, qty, action_context):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        
        # Pehle check karo ke material exists karta hai ya nahi
        cursor.execute("SELECT current_stock FROM materials WHERE material_name = ? AND department = ?;", (mat_name, dept_name))
        existing = cursor.fetchone()
        
        if existing:
            # Agar exists karta hai, toh stock update karo
            if "CONSUMPTION" in action_context:
                cursor.execute("UPDATE materials SET current_stock = current_stock - ? WHERE material_name = ? AND department = ?;", (qty, mat_name, dept_name))
            else:
                cursor.execute("UPDATE materials SET current_stock = current_stock + ? WHERE material_name = ? AND department = ?;", (qty, mat_name, dept_name))
        else:
            # Naya material insert karo
            cursor.execute("""
                INSERT INTO materials (material_name, department, unit, current_stock) 
                VALUES (?, ?, ?, ?);
            """, (mat_name, dept_name, unit_type, qty if "CONSUMPTION" not in action_context else 0))
        
        # Log entry
        cursor.execute("""
            INSERT INTO material_logs (material_name, department, action_type, quantity)
            VALUES (?, ?, ?, ?);
        """, (mat_name, dept_name, action_context, qty))
        
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error in insert_or_update_material: {e}")
        return False
    finally:
        conn.close()

def fetch_material_logs(dept_name, start_str, end_str, search_query=""):
    conn = get_connection()
    if not conn: return []
    cursor = conn.cursor()
    
    query = """
        SELECT id, material_name, action_type, quantity, timestamp 
        FROM material_logs 
        WHERE department = ? AND timestamp BETWEEN ? AND ?
    """
    params = [dept_name, start_str, end_str]
    
    if search_query:
        query += " AND (material_name LIKE ? OR action_type LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])
        
    query += " ORDER BY id DESC;"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    cursor.close()
    conn.close()
    return data

def fetch_all_inventory():
    conn = get_connection()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory ORDER BY item_name ASC;")
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    cursor.close()
    conn.close()
    return data

def insert_inventory(item_name, packing, category, unit, safety_stock, current_stock=0):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO inventory (item_name, packing, category, unit, safety_stock, current_stock) 
            VALUES (?, ?, ?, ?, ?, ?) 
            ON CONFLICT(item_name) DO UPDATE SET packing=excluded.packing, category=excluded.category, safety_stock=excluded.safety_stock;
        """, (item_name, packing, category, unit, safety_stock, current_stock))
        conn.commit()
        cursor.close()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def update_stock_level(item_name, new_stock):
    conn = get_connection()
    if not conn: return False
    cursor = conn.cursor()
    cursor.execute("UPDATE inventory SET current_stock = ? WHERE item_name = ?;", (new_stock, item_name))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def insert_customer(customer_name, phone, address, email='N/A'):
    conn = get_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO customers (customer_name, phone, email, address) VALUES (?, ?, ?, ?);",
            (customer_name, phone, email, address)
        )
        conn.commit()
        cursor.close()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def fetch_all_customers():
    conn = get_connection()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers ORDER BY customer_name ASC;")
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    cursor.close()
    conn.close()
    return data

def insert_order(client_name, product_name, quantity, status='Pending Production'):
    conn = get_connection()
    if not conn: return None
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO orders (customer_name, item_name, qty_ordered, qty_to_produce, status) VALUES (?, ?, ?, ?, ?);",
        (client_name, product_name, quantity, quantity, status)
    )
    last_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return last_id

def fetch_all_orders():
    conn = get_connection()
    if not conn: return []
    cursor = conn.cursor()
    query = """
        SELECT 
            MIN(id) as id, 
            customer_name, 
            group_concat(item_name || ' (' || qty_ordered || ')', ', ') as combined_products,
            SUM(qty_ordered) as total_qty,
            status, 
            order_date 
        FROM orders 
        GROUP BY customer_name, order_date, status
        ORDER BY id DESC;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    data = []
    for row in rows:
        data.append({
            'Order ID': row['id'],
            'Client Name': row['customer_name'],
            'Product Name': row['combined_products'],
            'Quantity Ordered': row['total_qty'],
            'Fulfillment Status': row['status'],
            'Date Created': row['order_date']
        })
    cursor.close()
    conn.close()
    return data

def fetch_pending_production():
    conn = get_connection()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("SELECT id as schedule_id, item_name, qty_to_produce, status FROM orders WHERE status = 'Pending Production' ORDER BY id DESC;")
    rows = cursor.fetchall()
    data = [dict(row) for row in rows]
    cursor.close()
    conn.close()
    return data

# Server build trigger
init_db()
