import streamlit as st
import pandas as pd
import database
import engine
import os

# Page configurations for a premium industrial look
st.set_page_config(page_title="Smart Factory OS", page_icon="🏭", layout="wide")

# Ensure DB initialization gets triggered
if 'db_initialized' not in st.session_state:
    database.init_db()
    st.session_state.db_initialized = True

# Premium CSS Styling
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetricValue"] { font-size: 32px; font-weight: 700; color: #1e3d59; }
    div[data-testid="stMetricLabel"] { font-size: 14px; font-weight: 600; color: #5c6b73; }
    .stButton>button, .stDownloadButton>button { border-radius: 6px; font-weight: bold; }
    div.stDownloadButton > button {
        background-color: #2e7d32 !important;
        color: white !important;
        border: none !important;
        padding: 10px 20px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 🖨️ NATIVE DOWNLOAD-TO-PRINT ENGINE
def display_print_engine(dataframe, report_title):
    if dataframe.empty: return
    html_table = dataframe.to_html(index=False, classes='table')
    html_document = f"""
    <!DOCTYPE html><html><head><title>{report_title}</title>
    <style>body{{font-family:'Segoe UI',sans-serif;padding:35px;color:#222;}} table{{width:100%;border-collapse:collapse;margin-top:20px;font-size:13px;}} th,td{{border:1px solid #bbb;padding:10px;text-align:left;}} th{{background-color:#1e3d59;color:white;}} h2{{color:#1e3d59;}}</style>
    </head><body onload="window.print();"><h2>🏭 Smart Factory OS</h2><h4>Report Target: {report_title}</h4><hr/>{html_table}</body></html>
    """
    st.download_button(
        label="🖨️ Generate & Print Report (HTML/PDF)", data=html_document,
        file_name=f"{report_title.replace(' ', '_').lower()}.html", mime="text/html",
        key=f"dl_{report_title.replace(' ', '_')}_{len(dataframe)}"
    )

# --- SECURITY APP STATES CONFIGURATION ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = "Worker"
if 'user_dept' not in st.session_state: st.session_state.user_dept = "All"
if 'active_username' not in st.session_state: st.session_state.active_username = ""

# --- DROPDOWN LOGIN SYSTEM PANEL ---
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; margin-top:50px;'>🔐 Factory Management System Login</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("login_form"):
            system_users_list = database.fetch_all_users()
            user_dropdown_options = [user['username'] for user in system_users_list]
            
            selected_user = st.selectbox("Select Your User Profile:", user_dropdown_options)
            password = st.text_input("Password:", type="password")
            
            if st.form_submit_button("Sign In", use_container_width=True):
                matched_account = next((u for u in system_users_list if u['username'] == selected_user), None)
                if matched_account and matched_account['password'] == password:
                    st.session_state.logged_in = True
                    st.session_state.active_username = matched_account['username']
                    st.session_state.user_role = matched_account['role']
                    st.session_state.user_dept = matched_account['assigned_dept']
                    st.success("Welcome! Authentication Successful.")
                    st.rerun()
                else:
                    st.error("❌ Invalid Password. Please check and try again.")
else:
    # --- CONTROL BAR ---
    title_col, logout_col = st.columns([5, 1])
    with title_col:
        st.title("🏭 Smart Factory OS")
        st.caption(f"👤 User: **{st.session_state.active_username}** | 🔑 Role: **{st.session_state.user_role}** | 📦 Dept: **{st.session_state.user_dept}**")
    with logout_col:
        st.write("")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
            
    st.write("---")

    # --- Sidebar Navigation Routing ---
    master_pages_hub = [
        "📊 Stock Dashboard", "🍏 Add New Item (Universal)", 
        "🌾 Raw Materials Dept", "📦 Empty Cartons Dept", "📜 Paper Reels Dept", "📦 Finished Goods Dept",
        "📦 Place New Order", "⚙️ Production Floor & Orders Log", 
        "👤 Add New Customer", "⚙️ System Settings", "👤 About Developer"
    ]
    
    if st.session_state.user_role == "Worker":
        if st.session_state.user_dept == "Raw Material": 
            allowed_screens = ["🌾 Raw Materials Dept"]
        elif st.session_state.user_dept == "Empty Carton": 
            allowed_screens = ["📦 Empty Cartons Dept"]
        elif st.session_state.user_dept == "Paper Reels": 
            allowed_screens = ["📜 Paper Reels Dept"]
        elif st.session_state.user_dept == "Finished Goods":
            allowed_screens = ["📦 Finished Goods Dept"]
        else: 
            allowed_screens = ["👤 About Developer"]
    elif st.session_state.user_role == "Secondary":
        allowed_screens = [p for p in master_pages_hub if p != "⚙️ System Settings"]
    else:
        allowed_screens = master_pages_hub

    st.sidebar.markdown("### 🗺️ Navigation Hub")
    page = st.sidebar.radio("Select Screen Mode:", allowed_screens)

    if 'order_cart' not in st.session_state:
        st.session_state.order_cart = []

    # ==========================================
    # 1. CENTRAL MASTER STOCK DASHBOARD
    # ==========================================
    if page == "📊 Stock Dashboard":
        st.subheader("📋 Centralized Searchable Stock Analytics Grid")
        d_tab1, d_tab2, d_tab3, d_tab4 = st.tabs(["📦 Finished Goods", "🌾 Raw Materials Stock", "📦 Empty Cartons Stock", "📜 Paper Reels Stock"])
        
        with d_tab1:
            raw_data = database.fetch_all_inventory()
            if raw_data:
                df_stock = pd.DataFrame(raw_data)
                f_col1, f_col2, f_col3 = st.columns(3)
                search_query_fg = f_col1.text_input("Search Product Name:", key="search_fg")
                selected_packing = f_col2.selectbox("Filter by Packing:", ["All Packings"] + sorted(df_stock['packing'].dropna().unique().tolist()))
                selected_unit = f_col3.selectbox("Filter by Unit Measure:", ["All Units"] + sorted(df_stock['unit'].dropna().unique().tolist()))
                
                if search_query_fg:
                    df_stock = df_stock[df_stock['item_name'].str.contains(search_query_fg, case=False, na=False)]
                if selected_packing != "All Packings":
                    df_stock = df_stock[df_stock['packing'] == selected_packing]
                if selected_unit != "All Units":
                    df_stock = df_stock[df_stock['unit'] == selected_unit]
                
                if not df_stock.empty:
                    # Create display DataFrame with original column names for styling
                    df_display = df_stock[['id', 'item_name', 'packing', 'category', 'current_stock', 'safety_stock', 'unit']].copy()
                    
                    # Apply styling - Red background for low stock (using original column names)
                    def highlight_low_stock(row):
                        if row['current_stock'] <= row['safety_stock']:
                            return ['background-color: #ffebee; color: #c62828; font-weight: bold'] * len(row)
                        return [''] * len(row)
                    
                    # Display with styling
                    styled_df = df_display.style.apply(highlight_low_stock, axis=1)
                    st.dataframe(styled_df, use_container_width=True, hide_index=True)
                    
                    # Show low stock items separately with generate order button
                    low_stock_items = df_stock[df_stock['current_stock'] <= df_stock['safety_stock']]
                    if not low_stock_items.empty:
                        st.warning("🚨 LOW STOCK ALERT - The following items need production:")
                        for index, row in low_stock_items.iterrows():
                            deficit = row['safety_stock'] - row['current_stock'] + 100
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"**{row['item_name']}** - Current: `{row['current_stock']}` | Safety: `{row['safety_stock']}` | Need: `{deficit}` units")
                            with col2:
                                if st.button(f"Generate Order", key=f"gen_{row['id']}"):
                                    database.insert_order("Auto-System", row['item_name'], deficit, 'Pending Production')
                                    st.success(f"✅ Order generated for {row['item_name']}!")
                                    st.rerun()
                    
                    # Print engine with renamed columns
                    df_print = df_display[['id', 'item_name', 'packing', 'category', 'current_stock', 'safety_stock', 'unit']].copy()
                    df_print.columns = ['ID', 'Product Name', 'Packing Spec', 'Category', 'Current Stock', 'Safety Threshold', 'Unit']
                    display_print_engine(df_print, "Finished Goods Live Stock Status")
                    
                    if st.session_state.user_role in ["Master", "Secondary"]:
                        with st.expander("🛠️ Edit / Delete Product Stock Record Line"):
                            selected_id_fg = st.selectbox("Select Product ID to Modify/Delete:", df_stock['id'].tolist(), key="sb_edit_fg")
                            target_fg = df_stock[df_stock['id'] == selected_id_fg].iloc[0]
                            
                            ec1, ec2, ec3 = st.columns(3)
                            edit_fg_name = ec1.text_input("Edit Product Name:", value=str(target_fg['item_name']))
                            edit_fg_pack = ec2.text_input("Edit Packing Spec:", value=str(target_fg['packing']))
                            edit_fg_cat = ec3.text_input("Edit Category:", value=str(target_fg['category']))
                            
                            ec4, ec5, ec6 = st.columns(3)
                            edit_fg_unit = ec4.text_input("Edit Unit Type:", value=str(target_fg['unit']))
                            edit_fg_safety = ec5.number_input("Edit Safety Threshold:", min_value=0, value=int(target_fg['safety_stock']))
                            edit_fg_stock = ec6.number_input("Edit Current Stock Balance:", min_value=0, value=int(target_fg['current_stock']))
                            
                            btn_col1, btn_col2 = st.columns(2)
                            if btn_col1.button("Formally Save Stock Modifications", use_container_width=True):
                                if database.update_inventory_item(selected_id_fg, edit_fg_name, edit_fg_pack, edit_fg_cat, edit_fg_unit, edit_fg_safety, edit_fg_stock):
                                    st.success("SKU record updated successfully!")
                                    st.rerun()
                            if btn_col2.button("🗑️ Delete Product from Database", use_container_width=True):
                                if database.delete_inventory_item(selected_id_fg):
                                    st.warning("Product removed completely.")
                                    st.rerun()
                else:
                    st.warning("No records matched filters.")
            else:
                st.info("No items registered in Finished Goods yet.")

        def render_dept_stock_tab(dept_name, search_key):
            rm_data = database.fetch_materials_by_dept(dept_name)
            if rm_data:
                df_rm = pd.DataFrame(rm_data)
                sc1, sc2 = st.columns(2)
                q_txt = sc1.text_input(f"Search {dept_name} Name:", key=f"s_{search_key}")
                q_unit = sc2.selectbox(f"Filter by Unit ({dept_name}):", ["All Units"] + sorted(df_rm['unit'].unique().tolist()), key=f"u_{search_key}")
                
                if q_txt: df_rm = df_rm[df_rm['material_name'].str.contains(q_txt, case=False, na=False)]
                if q_unit != "All Units": df_rm = df_rm[df_rm['unit'] == q_unit]
                
                if not df_rm.empty:
                    def highlight_low_stock_mat(row):
                        safety = 10
                        if row['current_stock'] <= safety:
                            return ['background-color: #ffebee; color: #c62828; font-weight: bold'] * len(row)
                        return [''] * len(row)
                    
                    df_rm_display = df_rm[['id', 'material_name', 'current_stock', 'unit']].copy()
                    styled_df = df_rm_display.style.apply(highlight_low_stock_mat, axis=1)
                    st.dataframe(styled_df, use_container_width=True, hide_index=True)
                    
                    df_print = df_rm_display.copy()
                    df_print.columns = ['ID', 'Material Component Name', 'Available Balanced Stock', 'Measurement Unit']
                    display_print_engine(df_print, f"{dept_name} Stock Status Report")
                    
                    if st.session_state.user_role in ["Master", "Secondary"]:
                        with st.expander(f"🛠️ Edit or Delete {dept_name} Item Entry"):
                            selected_id_mat = st.selectbox("Select Item ID to Modify/Delete:", df_rm['id'].tolist(), key=f"sb_edit_mat_{search_key}")
                            target_mat = df_rm[df_rm['id'] == selected_id_mat].iloc[0]
                            
                            mc1, mc2, mc3 = st.columns(3)
                            edit_mat_name = mc1.text_input("Edit Item Name:", value=str(target_mat['material_name']), key=f"name_mat_{selected_id_mat}")
                            edit_mat_stock = mc2.number_input("Edit Stock Balance Amount:", value=float(target_mat['current_stock']), key=f"stock_mat_{selected_id_mat}")
                            edit_mat_unit = mc3.text_input("Edit Unit Measure:", value=str(target_mat['unit']), key=f"unit_mat_{selected_id_mat}")
                            
                            mb1, mb2 = st.columns(2)
                            if mb1.button("💾 Apply Inventory Updates", use_container_width=True, key=f"save_mat_btn_{selected_id_mat}"):
                                if database.update_material_item(selected_id_mat, edit_mat_name, edit_mat_stock, edit_mat_unit):
                                    st.success("Material stock entry adjusted!")
                                    st.rerun()
                            if mb2.button("🗑️ Delete Item Entry Matrix", use_container_width=True, key=f"del_mat_btn_{selected_id_mat}"):
                                if database.delete_material_item(selected_id_mat):
                                    st.warning("Material cleared from data log registry.")
                                    st.rerun()
                else:
                    st.warning("No records found.")
            else:
                st.info(f"No records found for {dept_name}.")

        with d_tab2: render_dept_stock_tab("Raw Material", "rm")
        with d_tab3: render_dept_stock_tab("Empty Carton", "ec")
        with d_tab4: render_dept_stock_tab("Paper Reels", "pr")

    # ==========================================
    # DEPARTMENTS LOGS ENGINE (Worker View Isolation)
    # ==========================================
    elif page in ["🌾 Raw Materials Dept", "📦 Empty Cartons Dept", "📜 Paper Reels Dept"]:
        target_dept = ""
        default_unit = ""
        if page == "🌾 Raw Materials Dept": target_dept, default_unit = "Raw Material", "Kg"
        elif page == "📦 Empty Cartons Dept": target_dept, default_unit = "Empty Carton", "Pcs"
        elif page == "📜 Paper Reels Dept": target_dept, default_unit = "Paper Reels", "Rolls"
            
        st.title(f"🏭 {target_dept} Department Operations Dashboard")
        sub_tab1, sub_tab2 = st.tabs(["📥 Inward Stock Load (Maal Aaya)", "📤 Internal Consumption (Kharch)"])
        
        cust_list = database.fetch_all_customers()
        cust_names = [c['customer_name'] for c in cust_list] if cust_list else []
        existing_items = [r['material_name'] for r in database.fetch_materials_by_dept(target_dept)]
        
        with sub_tab1:
            with st.form(f"in_form_{target_dept}", clear_on_submit=True):
                m_name = st.selectbox("Select Target Registered Item:", existing_items) if existing_items else st.text_input("Enter Product Name:")
                col_in1, col_in2 = st.columns(2)
                m_qty = col_in1.number_input("Quantity Received:", min_value=0.1, step=0.5, value=10.0)
                source_supplier = col_in2.selectbox("Received From:", cust_names) if cust_names else col_in2.text_input("Source Vendor Name (Manual):", value="External Vendor")
                
                if st.form_submit_button("💾 RECORD INWARD LOG TRANSACTION", use_container_width=True) and m_name:
                    items_all = database.fetch_materials_by_dept(target_dept)
                    matched_unit = next((i['unit'] for i in items_all if i['material_name'] == m_name), default_unit)
                    logged_action = f"IN [From Vendor: {source_supplier}]"
                    if database.insert_or_update_material(m_name, target_dept, matched_unit, m_qty, logged_action):
                        st.success("✅ Stock transaction logged into ledger.")
                        st.rerun()

        with sub_tab2:
            with st.form(f"out_form_{target_dept}", clear_on_submit=True):
                m_name = st.selectbox("Select Consumed Stock Component:", existing_items) if existing_items else None
                m_qty = st.number_input("Quantity Consumed:", min_value=0.1, step=0.5, value=1.0)
                
                # OUT Type Selection with dynamic customer visibility
                out_type = st.radio("Out Type:", ["Factory Use", "Sale"], horizontal=True)
                
                # Show customer details ONLY if Sale is selected
                customer_name = ""
                if out_type == "Sale":
                    st.markdown("---")
                    st.markdown("### 👤 Customer Details")
                    cust_names_local = [c['customer_name'] for c in cust_list] if cust_list else []
                    if cust_names_local:
                        customer_name = st.selectbox("Select Customer:", cust_names_local)
                    else:
                        customer_name = st.text_input("Customer Name:", value="Walk-in Customer")
                    st.markdown("---")
                else:
                    # Factory Use - auto set
                    customer_name = "Factory Use [Internal]"
                
                if st.form_submit_button("🔥 COMMENCE CONSUMPTION RELEASE", use_container_width=True) and m_name:
                    items_all = database.fetch_materials_by_dept(target_dept)
                    matched_unit = next((i['unit'] for i in items_all if i['material_name'] == m_name), default_unit)
                    
                    # Log action with customer detail if Sale
                    if out_type == "Sale":
                        action_context = f'SALE [Customer: {customer_name}]'
                    else:
                        action_context = 'FACTORY USE [Internal Consumption]'
                    
                    if database.insert_or_update_material(m_name, target_dept, matched_unit, m_qty, action_context):
                        st.warning(f"⚠️ Stock reduced! ({out_type})")
                        st.rerun()
                            
        st.write("---")
        st.subheader("🔍 Historical Audit Ledger Analytics")
        col_f1, col_f2, col_f3 = st.columns([2, 2, 3])
        start_date = col_f1.date_input("From (Start Date):", value=pd.Timestamp.now() - pd.Timedelta(days=30), key=f"sd_{target_dept}")
        end_date = col_f2.date_input("To (End Date):", value=pd.Timestamp.now(), key=f"ed_{target_dept}")
        search_item = col_f3.text_input("🔍 Filter Ledger:", placeholder="Search item name...", key=f"sh_{target_dept}")
        
        s_str = start_date.strftime("%Y-%m-%d 00:00:00")
        e_str = end_date.strftime("%Y-%m-%d 23:59:59")
        
        logs = database.fetch_material_logs(target_dept, start_str=s_str, end_str=e_str, search_query=search_item)
        
        if logs:
            df_logs = pd.DataFrame(logs)
            df_logs.columns = ['Log Transaction ID', 'Material Specs Name', 'Transaction Event / Context', 'Delta Qty Change', 'Timestamp Logged']
            display_print_engine(df_logs, f"{target_dept} Audit Tracking Ledger")
            st.dataframe(df_logs, use_container_width=True, hide_index=True)
            
            if st.session_state.user_role in ["Master", "Secondary"]:
                with st.expander("🚨 Void / Delete Specific Log Entry Row"):
                    target_log_id = st.selectbox("Choose Transaction ID to Drop/Void:", df_logs['Log Transaction ID'].tolist(), key=f"sb_log_{target_dept}")
                    if st.button("Permanent Delete Selected Log Line Record", use_container_width=True):
                        if database.delete_material_log(target_log_id):
                            st.warning(f"Log index reference key {target_log_id} cleared out.")
                            st.rerun()
        else:
            st.info("No transaction history recorded for selected inputs.")

    # ==========================================
    # 2. FINISHED GOODS DEPT (WITH EDIT/DELETE)
    # ==========================================
    elif page == "📦 Finished Goods Dept":
        st.title("🏭 Finished Goods Operations Dashboard")
        
        inventory = database.fetch_all_inventory()
        inv_names = [item['item_name'] for item in inventory] if inventory else []
        
        sub_tab1, sub_tab2 = st.tabs(["📥 Stock IN (Production Added)", "📤 Stock OUT (Dispatch/Sale)"])
        
        cust_list = database.fetch_all_customers()
        cust_names = [c['customer_name'] for c in cust_list] if cust_list else []
        
        with sub_tab1:
            with st.form("fg_in_form", clear_on_submit=True):
                item_name = st.selectbox("Select Product:", inv_names) if inv_names else st.text_input("Enter Product Name:")
                col1, col2 = st.columns(2)
                qty_in = col1.number_input("Quantity Produced/Received:", min_value=0.1, step=0.5, value=10.0)
                source = col2.selectbox("Source:", cust_names) if cust_names else col2.text_input("Source:", value="Production Floor")
                
                if st.form_submit_button("💾 RECORD STOCK IN", use_container_width=True) and item_name:
                    target_item = next((i for i in inventory if i['item_name'] == item_name), None)
                    if target_item:
                        new_stock = target_item['current_stock'] + qty_in
                        if database.update_stock_level(item_name, new_stock):
                            st.success(f"✅ Stock added! New balance: {new_stock}")
                            st.rerun()
                    else:
                        st.error("Item not found in inventory!")

        with sub_tab2:
            with st.form("fg_out_form", clear_on_submit=True):
                item_name = st.selectbox("Select Product:", inv_names) if inv_names else st.text_input("Enter Product Name:")
                col1, col2 = st.columns(2)
                qty_out = col1.number_input("Quantity Dispatched/Sold:", min_value=0.1, step=0.5, value=1.0)
                
                # OUT Type Selection with dynamic customer visibility
                out_type = st.radio("Out Type:", ["Factory Use", "Sale"], horizontal=True)
                
                # Show customer details ONLY if Sale is selected
                customer_name = ""
                if out_type == "Sale":
                    st.markdown("---")
                    st.markdown("### 👤 Customer Details")
                    if cust_names:
                        customer_name = st.selectbox("Select Customer:", cust_names)
                    else:
                        customer_name = st.text_input("Customer Name:", value="Walk-in Customer")
                    st.markdown("---")
                else:
                    # Factory Use - auto set
                    customer_name = "Factory Use [Internal]"
                
                if st.form_submit_button("🔥 RECORD STOCK OUT", use_container_width=True) and item_name:
                    target_item = next((i for i in inventory if i['item_name'] == item_name), None)
                    if target_item:
                        if target_item['current_stock'] >= qty_out:
                            new_stock = target_item['current_stock'] - qty_out
                            if database.update_stock_level(item_name, new_stock):
                                # Create order entry with proper status
                                if out_type == "Sale":
                                    status = "Fulfilled"
                                else:
                                    status = "Factory Use"
                                database.insert_order(customer_name, item_name, qty_out, status)
                                st.warning(f"⚠️ Stock deducted! New balance: {new_stock} ({out_type})")
                                st.rerun()
                        else:
                            st.error(f"❌ Insufficient stock! Available: {target_item['current_stock']}")
                    else:
                        st.error("Item not found in inventory!")
        
        st.write("---")
        st.subheader("📊 Current Finished Goods Inventory")
        if inventory:
            df_inv = pd.DataFrame(inventory)
            df_display = df_inv[['id', 'item_name', 'packing', 'category', 'current_stock', 'safety_stock', 'unit']]
            df_display.columns = ['ID', 'Product Name', 'Packing', 'Category', 'Current Stock', 'Safety Stock', 'Unit']
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # EDIT/DELETE SECTION - LIKE OTHER DEPARTMENTS
            if st.session_state.user_role in ["Master", "Secondary"]:
                with st.expander("🛠️ Edit / Delete Finished Goods Item"):
                    sel_id = st.selectbox("Select Product ID to Modify/Delete:", df_inv['id'].tolist(), key="edit_fg_dept")
                    target = df_inv[df_inv['id'] == sel_id].iloc[0]
                    
                    c1, c2, c3 = st.columns(3)
                    new_name = c1.text_input("Product Name:", value=target['item_name'])
                    new_pack = c2.text_input("Packing Spec:", value=target['packing'])
                    new_cat = c3.text_input("Category:", value=target['category'])
                    c4, c5, c6 = st.columns(3)
                    new_unit = c4.text_input("Unit Type:", value=target['unit'])
                    new_safety = c5.number_input("Safety Stock:", min_value=0, value=int(target['safety_stock']))
                    new_stock = c6.number_input("Current Stock:", min_value=0, value=int(target['current_stock']))
                    
                    btn1, btn2 = st.columns(2)
                    if btn1.button("💾 Update Item", key="update_fg_dept"):
                        if database.update_inventory_item(sel_id, new_name, new_pack, new_cat, new_unit, new_safety, new_stock):
                            st.success("✅ Item updated successfully!")
                            st.rerun()
                    if btn2.button("🗑️ Delete Item", key="del_fg_dept"):
                        if database.delete_inventory_item(sel_id):
                            st.warning("⚠️ Item deleted successfully!")
                            st.rerun()
        else:
            st.info("No finished goods in inventory.")

    # ==========================================
    # 3. UNIVERSAL PRODUCT REGISTRY
    # ==========================================
    elif page == "🍏 Add New Item (Universal)":
        st.subheader("🍏 Centralized Universal Product & Item Registry Form")
        with st.form("universal_add_item_form", clear_on_submit=True):
            col_u1, col_u2 = st.columns(2)
            item_name_input = col_u1.text_input("Enter Item / Product Name:")
            selected_dept = col_u2.selectbox("Select Destination Department:", ["Finished Goods (Products)", "Raw Material", "Empty Carton", "Paper Reels"])
            
            col_u3, col_u4, col_u5 = st.columns(3)
            if selected_dept == "Finished Goods (Products)":
                pack_details = col_u3.text_input("Packing Details:", value="12x50 Box")
                prod_cat = col_u4.selectbox("Product Category:", ["Toffee", "Bubblegum", "Chocolates", "Others"])
                unit_type = col_u5.text_input("Unit Type:", value="Jars")
                safety_stock_input = st.number_input("Safety Stock Limit:", min_value=1, value=50)
            else:
                pack_details, prod_cat, safety_stock_input = "", "", 0
                unit_type = col_u3.text_input("Unit Type:", value="Kg" if selected_dept == "Raw Material" else ("Pcs" if selected_dept == "Empty Carton" else "Rolls"))
                
            if st.form_submit_button("💾 Save Item Data into Core Database", use_container_width=True) and item_name_input:
                if selected_dept == "Finished Goods (Products)":
                    database.insert_inventory(item_name_input, pack_details, prod_cat, unit_type, safety_stock_input, 0)
                else:
                    database.insert_or_update_material(item_name_input, selected_dept, unit_type, 0.0, 'INITIAL REGISTRATION')
                st.success(f"🎉 Item '{item_name_input}' registered safely!")
                st.rerun()

        # REGISTERED ITEMS WITH DEPARTMENT FILTERS (FIXED)
        st.write("---")
        st.subheader("📜 Currently Registered Items (Department Wise)")
        
        # Fetch all data
        all_inv = database.fetch_all_inventory()
        all_raw = database.fetch_materials_by_dept("Raw Material")
        all_carton = database.fetch_materials_by_dept("Empty Carton")
        all_reels = database.fetch_materials_by_dept("Paper Reels")
        
        # Convert to DataFrames with consistent column names
        def normalize_inventory_data(data_list, dept_name):
            """Convert inventory/materials data to consistent format"""
            normalized = []
            for item in data_list:
                row = {
                    'id': item.get('id', ''),
                    'item_name': item.get('item_name') or item.get('material_name', ''),
                    'packing': item.get('packing', '-'),
                    'category': item.get('category', '-'),
                    'unit': item.get('unit', '-'),
                    'current_stock': item.get('current_stock', 0),
                    'safety_stock': item.get('safety_stock', 0),
                    'department': dept_name
                }
                # Agar name empty hai toh "Unnamed" set karo
                if not row['item_name'] or row['item_name'] == '':
                    row['item_name'] = f"Unnamed Item (ID: {row['id']})"
                normalized.append(row)
            return normalized
        
        # Normalize all data
        inv_data = normalize_inventory_data(all_inv, "Finished Goods")
        raw_data = normalize_inventory_data(all_raw, "Raw Material")
        carton_data = normalize_inventory_data(all_carton, "Empty Carton")
        reels_data = normalize_inventory_data(all_reels, "Paper Reels")
        
        # Create DataFrames
        df_inv = pd.DataFrame(inv_data) if inv_data else pd.DataFrame()
        df_raw = pd.DataFrame(raw_data) if raw_data else pd.DataFrame()
        df_carton = pd.DataFrame(carton_data) if carton_data else pd.DataFrame()
        df_reels = pd.DataFrame(reels_data) if reels_data else pd.DataFrame()
        
        # Department filter
        dept_filter = st.selectbox("Filter by Department:", ["All", "Finished Goods", "Raw Material", "Empty Carton", "Paper Reels"])
        
        # Search bar
        search_item = st.text_input("🔍 Search Item Name:", placeholder="Type to search...")
        
        # Show data based on filter
        if dept_filter == "All":
            # Combine all data
            combined_data = []
            if not df_inv.empty:
                combined_data.append(df_inv)
            if not df_raw.empty:
                combined_data.append(df_raw)
            if not df_carton.empty:
                combined_data.append(df_carton)
            if not df_reels.empty:
                combined_data.append(df_reels)
            
            if combined_data:
                df_all = pd.concat(combined_data, ignore_index=True)
                
                # Filter by search
                if search_item:
                    df_all = df_all[df_all['item_name'].str.contains(search_item, case=False, na=False)]
                
                # Display columns with consistent names
                display_cols = ['item_name', 'department', 'packing', 'category', 'unit', 'current_stock', 'safety_stock']
                df_display = df_all[display_cols].copy()
                df_display.columns = ['Item Name', 'Department', 'Packing', 'Category', 'Unit', 'Current Stock', 'Safety Stock']
                
                # Replace empty/None values with '-'
                df_display = df_display.fillna('-')
                
                st.dataframe(df_display, use_container_width=True, hide_index=True)
            else:
                st.info("No items registered yet.")
        
        else:
            # Show specific department
            if dept_filter == "Finished Goods":
                df_show = df_inv
            elif dept_filter == "Raw Material":
                df_show = df_raw
            elif dept_filter == "Empty Carton":
                df_show = df_carton
            elif dept_filter == "Paper Reels":
                df_show = df_reels
            else:
                df_show = pd.DataFrame()
            
            if not df_show.empty:
                # Filter by search
                if search_item:
                    df_show = df_show[df_show['item_name'].str.contains(search_item, case=False, na=False)]
                
                # Display columns
                if dept_filter == "Finished Goods":
                    display_cols = ['id', 'item_name', 'packing', 'category', 'unit', 'current_stock', 'safety_stock']
                    col_names = ['ID', 'Item Name', 'Packing', 'Category', 'Unit', 'Current Stock', 'Safety Stock']
                else:
                    display_cols = ['id', 'item_name', 'unit', 'current_stock']
                    col_names = ['ID', 'Item Name', 'Unit', 'Current Stock']
                
                df_display = df_show[display_cols].copy()
                df_display.columns = col_names
                
                # Replace empty/None values with '-'
                df_display = df_display.fillna('-')
                
                st.dataframe(df_display, use_container_width=True, hide_index=True)
                
                # EDIT/DELETE SECTION
                if st.session_state.user_role in ["Master", "Secondary"]:
                    with st.expander(f"🛠️ Edit / Delete {dept_filter} Item"):
                        sel_id = st.selectbox("Select Item ID:", df_show['id'].tolist(), key=f"edit_{dept_filter.replace(' ', '_')}")
                        target = df_show[df_show['id'] == sel_id].iloc[0]
                        
                        if dept_filter == "Finished Goods":
                            c1, c2, c3 = st.columns(3)
                            new_name = c1.text_input("Name:", value=target['item_name'])
                            new_pack = c2.text_input("Packing:", value=target['packing'] if target['packing'] != '-' else '')
                            new_cat = c3.text_input("Category:", value=target['category'] if target['category'] != '-' else '')
                            c4, c5, c6 = st.columns(3)
                            new_unit = c4.text_input("Unit:", value=target['unit'] if target['unit'] != '-' else '')
                            new_safety = c5.number_input("Safety Stock:", min_value=0, value=int(target['safety_stock']))
                            new_stock = c6.number_input("Current Stock:", min_value=0, value=int(target['current_stock']))
                            
                            btn1, btn2 = st.columns(2)
                            if btn1.button("💾 Update Item", key=f"update_{dept_filter.replace(' ', '_')}"):
                                if database.update_inventory_item(sel_id, new_name, new_pack, new_cat, new_unit, new_safety, new_stock):
                                    st.success("✅ Item updated successfully!")
                                    st.rerun()
                            if btn2.button("🗑️ Delete Item", key=f"del_{dept_filter.replace(' ', '_')}"):
                                if database.delete_inventory_item(sel_id):
                                    st.warning("⚠️ Item deleted successfully!")
                                    st.rerun()
                        else:
                            c1, c2, c3 = st.columns(3)
                            new_name = c1.text_input("Name:", value=target['item_name'])
                            new_unit = c2.text_input("Unit:", value=target['unit'] if target['unit'] != '-' else '')
                            new_stock = c3.number_input("Stock:", min_value=0, value=float(target['current_stock']))
                            
                            btn1, btn2 = st.columns(2)
                            if btn1.button("💾 Update Item", key=f"update_{dept_filter.replace(' ', '_')}"):
                                if database.update_material_item(sel_id, new_name, new_stock, new_unit):
                                    st.success("✅ Item updated successfully!")
                                    st.rerun()
                            if btn2.button("🗑️ Delete Item", key=f"del_{dept_filter.replace(' ', '_')}"):
                                if database.delete_material_item(sel_id):
                                    st.warning("⚠️ Item deleted successfully!")
                                    st.rerun()
            else:
                st.info(f"No {dept_filter.lower()} registered.")

    # ==========================================
    # 4. PLACE NEW MULTI-ITEM ORDER
    # ==========================================
    elif page == "📦 Place New Order":
        st.subheader("🛒 Create Multi-Item Client Order Invoice")
        cust_list = database.fetch_all_customers()
        if not cust_list:
            st.warning("Please register at least one customer profile first.")
        else:
            cust_names = [c['customer_name'] for c in cust_list]
            selected_customer = st.selectbox("Select Client / Distributor:", cust_names)
            
            inv_list = database.fetch_all_inventory()
            inv_names = [i['item_name'] for i in inv_list]
            
            if inv_names:
                col_i1, col_i2 = st.columns([3, 1])
                selected_item = col_i1.selectbox("Choose Product SKU:", inv_names)
                order_qty = col_i2.number_input("Invoice Target Units:", min_value=1, value=100)
                
                if st.button("➕ Add Item to Order Invoice List"):
                    st.session_state.order_cart.append({'item_name': selected_item, 'quantity': order_qty})
                    st.rerun()
            
            if st.session_state.order_cart:
                st.write("### Current Order Items Cart:")
                st.dataframe(pd.DataFrame(st.session_state.order_cart), use_container_width=True)
                
                c_btn1, c_btn2 = st.columns(2)
                if c_btn1.button("🗑️ Clear Entire Cart"):
                    st.session_state.order_cart = []
                    st.rerun()
                if c_btn2.button("💾 Confirm & Dispatched Complete Order"):
                    for cart_item in st.session_state.order_cart:
                        engine.process_new_order(selected_customer, cart_item['item_name'], cart_item['quantity'])
                    st.session_state.order_cart = []
                    st.success("Orders dispatched to floor layouts successfully!")
                    st.rerun()

    # ==========================================
    # 5. PRODUCTION FLOOR & ORDER LOGS
    # ==========================================
    elif page == "⚙️ Production Floor & Orders Log":
        st.write("## 📊 Products Needing Production")
        
        all_inv = database.fetch_all_inventory()
        low_stock_items = []
        if all_inv:
            for item in all_inv:
                if item['current_stock'] <= item['safety_stock']:
                    low_stock_items.append(item)
        
        if low_stock_items:
            st.info("📋 The following products are below safety stock level and need production:")
            
            df_low = pd.DataFrame(low_stock_items)
            df_low['needed_quantity'] = df_low['safety_stock'] - df_low['current_stock'] + 100
            
            display_cols = ['item_name', 'current_stock', 'safety_stock', 'needed_quantity']
            df_display_low = df_low[display_cols].copy()
            df_display_low.columns = ['Product Name', 'Current Stock', 'Safety Level', 'Required Production']
            
            st.dataframe(df_display_low, use_container_width=True, hide_index=True)
            
            st.write("---")
            st.write("### ⚙️ Production Order Actions")
            
            col1, col2 = st.columns(2)
            with col1:
                selected_low_item = st.selectbox("Select Product for Production Order:", df_low['item_name'].tolist())
            with col2:
                prod_qty = st.number_input("Production Quantity:", min_value=1, value=100, step=50)
            
            if st.button("📤 Generate Production Order for Selected Product"):
                database.insert_order("Auto-System (Low Stock)", selected_low_item, prod_qty, 'Pending Production')
                st.success(f"✅ Production order generated for {selected_low_item}!")
                st.rerun()
            
            if st.button("⚡ Generate Orders for ALL Low Stock Items"):
                for item in low_stock_items:
                    deficit = item['safety_stock'] - item['current_stock'] + 100
                    database.insert_order("Auto-System (Bulk Order)", item['item_name'], deficit, 'Pending Production')
                st.success(f"✅ Production orders generated for {len(low_stock_items)} items!")
                st.rerun()
        else:
            st.success("✅ All products are above safety stock levels. No production needed at this time.")
        
        st.write("---")
        st.write("## 📝 Active Production Floor Requirements")
        
        prod_data = database.fetch_pending_production()
        if prod_data:
            df_pending = pd.DataFrame(prod_data)
            display_print_engine(df_pending, "Active Production Tasks Sheet")
            st.dataframe(df_pending, use_container_width=True, hide_index=True)
            
            st.write("---")
            selected_done_id = st.selectbox("Select Batch Ref ID to Dispatch As Completed:", [str(task['schedule_id']) for task in prod_data])
            if st.button("Mark Selected Order As Completed & Release"):
                conn = database.get_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE orders SET status='Fulfilled' WHERE id=?;", (selected_done_id,))
                conn.commit()
                cursor.close()
                conn.close()
                st.success(f"Batch Ref {selected_done_id} marked fulfilled!")
                st.rerun()
        else:
            st.info("✅ No pending production orders. Floor operations balanced.")
            
        st.write("---")
        st.write("## 📋 Historical Order Logs Registry")
        all_orders = database.fetch_all_orders()
        if all_orders:
            df_orders = pd.DataFrame(all_orders)
            st.dataframe(df_orders, use_container_width=True, hide_index=True)
            
            if st.session_state.user_role in ["Master", "Secondary"]:
                with st.expander("🚨 Admin: Delete Order Record Entry Row"):
                    target_ord_id = st.selectbox("Select Order ID to Cancel/Purge:", df_orders['Order ID'].tolist())
                    if st.button("🗑️ Remove Order Record File From Ledger", use_container_width=True):
                        if database.delete_order_record(target_ord_id):
                            st.warning("Order historical entry purged safely.")
                            st.rerun()

    # ==========================================
    # 6. REGISTER NEW CUSTOMERS
    # ==========================================
    elif page == "👤 Add New Customer":
        st.subheader("👤 Register Profiles (Customers / Suppliers)")
        with st.form("add_customer_form", clear_on_submit=True):
            cc1, cc2 = st.columns(2)
            c_name = cc1.text_input("Account Identifier Name:")
            c_phone = cc2.text_input("Secure Contact String (Phone):")
            c_address = st.text_area("Corporate Location / Address Details:")
            if st.form_submit_button("Register Account Entity") and c_name:
                database.insert_customer(customer_name=c_name, phone=c_phone, address=c_address)
                st.success(f"✔️ Profile '{c_name}' created.")
                st.rerun()

        st.write("---")
        cust_list = database.fetch_all_customers()
        if cust_list:
            df_cust = pd.DataFrame(cust_list)[['id', 'customer_name', 'phone', 'address']]
            display_print_engine(df_cust, "Accounts Ledger Directory")
            st.dataframe(df_cust, use_container_width=True, hide_index=True)
            
            if st.session_state.user_role in ["Master", "Secondary"]:
                with st.expander("🚨 Terminate Account Profile Entry Line"):
                    target_cust_id = st.selectbox("Select Account ID to Delete:", df_cust['id'].tolist())
                    if st.button("🗑️ Delete Account Entry File", use_container_width=True):
                        if database.delete_customer(target_cust_id):
                            st.warning("Customer profile dropped out from logs registry.")
                            st.rerun()

    # ==========================================
    # 7. SYSTEM CREDENTIAL CONFIGS (MASTER ONLY)
    # ==========================================
    elif page == "⚙️ System Settings":
        if st.session_state.user_role != "Master":
            st.error("⛔ Access Denied! Only a designated Master admin profile can access settings.")
        else:
            st.subheader("⚙️ Master User Identity Settings panel")
            with st.form("add_new_user_form", clear_on_submit=True):
                st.write("### ➕ Provision New User Account Profile Matrix")
                new_username = st.text_input("Assign Unique Username:")
                new_password = st.text_input("Set Security Password String:")
                new_role = st.selectbox("Select Access privilege Rank:", ["Master", "Secondary", "Worker"])
                new_dept = st.selectbox("Assign Dedicated Department (Workers Restriction Only):", ["All", "Raw Material", "Empty Carton", "Paper Reels", "Finished Goods"])
                
                if st.form_submit_button("💾 Save User to Server Layout", use_container_width=True):
                    if new_username and new_password:
                        if database.insert_user(new_username, new_password, new_role, new_dept):
                            st.success(f"🚀 User security account '**{new_username}**' successfully registered!")
                            st.rerun()
                        else:
                            st.error("System Integrity Error: Username already taken.")
            
            st.write("---")
            st.write("### 📋 Active Provisioned Accounts Directory Matrix")
            user_directory = database.fetch_all_users()
            
            if user_directory:
                df_users = pd.DataFrame(user_directory)
                st.dataframe(df_users[['id', 'username', 'role', 'assigned_dept']], use_container_width=True, hide_index=True)
                
                with st.expander("🛠️ Modify / Terminate Existing Accounts Permissions Matrix"):
                    target_id = st.selectbox("Select User Database ID to target:", df_users['id'].tolist())
                    target_user = next((u for u in user_directory if u['id'] == target_id), None)
                    
                    if target_user:
                        edit_name = st.text_input("Edit Username Input ID:", value=target_user['username'])
                        edit_pass = st.text_input("Edit Password String:", value=target_user['password'])
                        edit_role = st.selectbox("Modify Permission Rank Condition:", ["Master", "Secondary", "Worker"], index=["Master", "Secondary", "Worker"].index(target_user['role']))
                        
                        dept_list = ["All", "Raw Material", "Empty Carton", "Paper Reels", "Finished Goods"]
                        current_dept_index = dept_list.index(target_user['assigned_dept']) if target_user['assigned_dept'] in dept_list else 0
                        edit_dept = st.selectbox("Modify Functional Department:", dept_list, index=current_dept_index)
                        
                        col_action1, col_action2 = st.columns(2)
                        if col_action1.button("💾 Apply Modifications Changes", use_container_width=True):
                            if database.update_user(target_id, edit_name, edit_pass, edit_role, edit_dept):
                                st.success("Account profile specifications updated.")
                                st.rerun()
                                
                        if col_action2.button("🗑️ Terminate Account Profile Permanently (Delete)", use_container_width=True):
                            if edit_name == "admin":
                                st.error("Operation Denied: Cannot delete primary core admin configuration file.")
                            else:
                                if database.delete_user(target_id):
                                    st.warning("Account deleted from database.")
                                    st.rerun()

    # ==========================================
    # 8. ABOUT DEVELOPER
    # ==========================================
    elif page == "👤 About Developer":
        st.subheader("👤 Software Architect Portfolio")
        
        if os.path.exists("my_pic.png"):
            st.image("my_pic.png", caption="Developer - Nabeel Naeem", width=200)
        else:
            st.info("📷 Developer photo (my_pic.png) not found in the application folder.")
        
        st.markdown("""
            <h3>👨‍💻 Nabeel Naeem</h3>
            <p><b>ICS Computer Science Student & Factory Operations Manager</b></p>
            <hr/>
            <p>This <b>Smart Factory OS</b> is engineered to eliminate manual logging errors, bridge communication gaps between backend order inventory streams and production floors, and enable real-time operational transparency from any remote device.</p>
            <hr/>
            <p><b>📧 Contact:</b> nabeel@example.com</p>
            <p><b>📱 Phone:</b> +92-XXX-XXXXXXX</p>
        """, unsafe_allow_html=True)
