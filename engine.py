import database

def process_new_order(client_name, item_name, order_qty):
    """
    Order execution core framework mapped exclusively for SQLite database records.
    Calculates absolute current inventory, tracks shortage benchmarks, and automates safety buffering.
    """
    conn = database.get_connection()
    if not conn:
        return "Database integration link broken!"
        
    cursor = conn.cursor()
    cursor.execute(
        "SELECT current_stock, safety_stock FROM inventory WHERE item_name = ?;", 
        (item_name,)
    )
    item_data = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not item_data:
        return f"Product item validation failed. '{item_name}' was not found in logs."
        
    current_stock = item_data['current_stock']
    safety_stock = item_data['safety_stock']
    
    # CASE 1: Full Inventory availability is satisfied 
    if current_stock >= order_qty:
        new_stock = current_stock - order_qty
        
        database.insert_order(client_name, item_name, order_qty, 'Fulfilled')
        database.update_stock_level(item_name, new_stock)
        
        return f"Fulfilled immediately! Internal dispatch completed. Remaining stock: {new_stock} Units."
        
    # CASE 2: Shortage fallback logic triggered
    else:
        deficit = order_qty - current_stock
        total_to_produce = deficit + safety_stock
        
        # Log active request target to live floor pipeline
        database.insert_order(client_name, item_name, order_qty, 'Pending Production')
        
        # Modify remaining live counts to zero
        database.update_stock_level(item_name, 0)
        
        # Modify return response to match frontend text expects
        return f"Shortage of {deficit} units! Automated production floor schedule generated for **{total_to_produce} units** (Includes {safety_stock} safety buffer)."
