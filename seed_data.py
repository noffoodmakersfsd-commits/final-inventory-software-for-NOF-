import database

def add_factory_samples():
    print("⏳ Sample data database mein add kiya ja raha hai...")
    
    database.init_db()
    
    products = [
        ("Fruit Up Toffee", "12x50 Box", "Toffee", "Packets", 50, 330),
        ("Jelly Center Filled Gum", "24x20 Jar", "Bubblegum", "Jars", 60, 131),
        ("Nova Custom Shirt", "Single Polybag", "Apparel", "Pcs", 20, 10),
        ("Fruit Up 55 Toffee", "12x100 Box", "Toffee", "Packets", 40, 500),
        ("Center Filled Bubble Gum", "30x20 Jar", "Bubblegum", "Jars", 80, 250)
    ]
    
    for p in products:
        success = database.insert_inventory(
            item_name=p[0], 
            packing=p[1], 
            category=p[2], 
            unit=p[3], 
            safety_stock=p[4], 
            current_stock=p[5]
        )
        if success:
            print(f"✅ Product add ho gaya: {p[0]}")
        else:
            print(f"⚠️ Product pehle se mojood hai: {p[0]}")
            
    customers = [
        ("N Family Distributors", "0300-1234567", "Faisalabad, Pakistan"),
        ("Al-Mehmood Sweets", "0321-7654321", "Lahore, Pakistan"),
        ("Nova Apparel Hub", "0312-9876543", "Karachi, Pakistan")
    ]
    
    for c in customers:
        success = database.insert_customer(customer_name=c[0], phone=c[1], address=c[2])
        if success:
            print(f"✅ Customer register ho gaya: {c[0]}")
        else:
            print(f"⚠️ Customer pehle se mojood hai: {c[0]}")
            
    conn = database.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM orders")
    if cursor.fetchone()[0] == 0:
        sample_orders = [
            ("N Family Distributors", "Jelly Center Filled Gum", 100),
            ("Al-Mehmood Sweets", "Fruit Up Toffee", 250),
            ("Nova Apparel Hub", "Nova Custom Shirt", 50)
        ]
        for o in sample_orders:
            cursor.execute(
                "INSERT INTO orders (customer_name, item_name, qty_ordered, qty_to_produce, status) VALUES (?, ?, ?, ?, 'Pending Production')",
                (o[0], o[1], o[2], o[2])
            )
        conn.commit()
        print("✅ Sample Production Orders book ho gaye hain!")
    else:
        print("⚠️ Orders log mein pehle se data mojood hai.")
        
    cursor.close()
    conn.close()
    print("\n🚀 Saara Sample Data Successfully Inject Ho Gaya!")

if __name__ == "__main__":
    add_factory_samples()
