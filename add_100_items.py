import database

def bulk_add_100_items():
    print("⏳ Database mein 100 items add kiye ja rahe hain...")
    
    database.init_db()
    
    flavors = ["Mango", "Orange", "Strawberry", "Blueberry", "Cola", "Kacha Aam", "Mix Fruit", "Lychee", "Pineapple", "Chocolate"]
    packings = ["12x50 Box", "24x20 Jar", "30x20 Jar", "Single Polybag", "12x100 Box", "Packet Pack"]
    
    items_to_add = []
    
    for i in range(1, 41):
        flavor = flavors[(i - 1) % len(flavors)]
        packing = packings[(i - 1) % 3]
        items_to_add.append((f"Fruit Up {flavor} Toffee v{i}", packing, "Toffee", "Packets", 50, 150 + (i * 5)))
        
    for i in range(41, 81):
        flavor = flavors[(i - 41) % len(flavors)]
        packing = packings[(i - 41) % 3 + 1]
        items_to_add.append((f"{flavor} Center Filled Gum v{i}", packing, "Bubblegum", "Jars", 60, 100 + (i * 3)))
        
    colors = ["Black", "White", "Navy Blue", "Maroon", "Charcoal", "Olive"]
    sizes = ["S", "M", "L", "XL"]
    for i in range(81, 101):
        color = colors[(i - 81) % len(colors)]
        size = sizes[(i - 81) % len(sizes)]
        items_to_add.append((f"Nova Custom Shirt {color} ({size})", "Single Polybag", "Apparel", "Pcs", 20, 10 + (i - 80)))

    success_count = 0
    duplicate_count = 0
    
    for item in items_to_add:
        success = database.insert_inventory(
            item_name=item[0],
            packing=item[1],
            category=item[2],
            unit=item[3],
            safety_stock=item[4],
            current_stock=item[5]
        )
        if success:
            success_count += 1
        else:
            duplicate_count += 1

    print("\n--------------------------------------------------")
    print(f"🚀 Bulk Insertion Complete!")
    print(f"✅ Naye items kamyabi se add huay: {success_count}")
    print(f"⚠️ Pehle se mojood items (Skip ya Update huay): {duplicate_count}")
    print("--------------------------------------------------")

if __name__ == "__main__":
    bulk_add_100_items()
