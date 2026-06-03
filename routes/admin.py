import csv
import io
from flask import Blueprint, render_template, redirect, session, jsonify, Response

from database import get_db_connection

admin = Blueprint("admin", __name__)


# ====================================
# EXPORT USERS AS CSV
# ====================================
@admin.route("/admin/export-users")
def export_users_csv():
    if "user_id" not in session:
        return redirect("/login")

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT user_id, first_name, last_name, email, phone, role_id FROM users ORDER BY user_id")
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "First Name", "Last Name", "Email", "Phone", "Role"])
    for u in users:
        writer.writerow([
            u["user_id"], u["first_name"], u["last_name"],
            u["email"], u.get("phone",""), "Admin" if u["role_id"]==1 else "Customer"
        ])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=users_export.csv"}
    )


# ====================================
# USER DETAIL API (for View button)
# ====================================
@admin.route("/admin/user/<int:uid>")
def admin_user_detail(uid):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT user_id, first_name, last_name, email, phone, role_id FROM users WHERE user_id=%s",
        (uid,)
    )
    user = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) AS cnt FROM orders WHERE user_id=%s", (uid,))
    orders = cursor.fetchone()["cnt"]
    cursor.execute("SELECT COUNT(*) AS cnt FROM wishlist WHERE user_id=%s", (uid,))
    wishlist = cursor.fetchone()["cnt"]
    cursor.close()
    conn.close()

    if not user:
        return jsonify({"error": "Not found"}), 404

    return jsonify({
        "user_id":    user["user_id"],
        "name":       f"{user['first_name']} {user['last_name']}",
        "email":      user["email"],
        "phone":      user.get("phone") or "—",
        "role":       "Admin" if user["role_id"] == 1 else "Customer",
        "initials":   (user["first_name"][0] + (user["last_name"][0] if user["last_name"] else "")).upper(),
        "orders":     orders,
        "wishlist":   wishlist,
    })


# ====================================
# ADMIN DASHBOARD – Nexus Analytics
# ====================================
@admin.route("/admin")
def admin_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ── KPI 1: Total Revenue (all completed payments) ──
    cursor.execute("SELECT COALESCE(SUM(amount), 0) AS total FROM payments WHERE payment_status='Completed'")
    total_revenue = float(cursor.fetchone()["total"] or 0)

    # Also get total of ALL payments for reference
    cursor.execute("SELECT COALESCE(SUM(amount), 0) AS total FROM payments")
    all_payments_total = float(cursor.fetchone()["total"] or 0)

    # ── KPI 2: Orders breakdown ──
    cursor.execute("SELECT COUNT(*) AS cnt FROM orders")
    total_orders = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) AS cnt FROM orders WHERE order_status='Pending'")
    pending_orders = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) AS cnt FROM orders WHERE order_status='Completed'")
    completed_orders = cursor.fetchone()["cnt"]

    # ── KPI 3: Users ──
    cursor.execute("SELECT COUNT(*) AS cnt FROM users")
    total_users = cursor.fetchone()["cnt"] or 1

    cursor.execute("SELECT COUNT(*) AS cnt FROM users WHERE role_id=2")
    total_customers = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) AS cnt FROM users WHERE role_id=1")
    total_admins = cursor.fetchone()["cnt"]

    # ── KPI 4: Products ──
    cursor.execute("SELECT COUNT(*) AS cnt FROM products")
    total_products = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) AS cnt FROM products WHERE stock = 0")
    out_of_stock = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) AS cnt FROM products WHERE stock > 0 AND stock <= 10")
    low_stock_count = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) AS cnt FROM payments WHERE payment_status='Pending'")
    pending_payments = cursor.fetchone()["cnt"]

    # ── Conversion Rate ──
    conversion_rate = round((total_orders / total_users) * 100, 1) if total_users else 0

    # ── Top Performing Product ──
    cursor.execute("""
        SELECT p.product_id, p.product_name, p.price, p.stock, p.image_url,
               COUNT(oi.order_item_id) AS order_count,
               SUM(oi.quantity * oi.unit_price) AS revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        GROUP BY p.product_id, p.product_name, p.price, p.stock, p.image_url
        ORDER BY order_count DESC
        LIMIT 1
    """)
    top_product = cursor.fetchone()

    if not top_product:
        cursor.execute(
            "SELECT product_id, product_name, price, stock, image_url, 0 AS order_count FROM products LIMIT 1"
        )
        top_product = cursor.fetchone()

    # ── Top 5 Products by Order Count ──
    cursor.execute("""
        SELECT p.product_name, COUNT(oi.order_item_id) AS order_count
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        GROUP BY p.product_id, p.product_name
        ORDER BY order_count DESC
        LIMIT 5
    """)
    top_products = cursor.fetchall()

    # ── Category Distribution (real) ──
    cursor.execute("""
        SELECT c.category_name, COUNT(p.product_id) AS cnt
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        GROUP BY c.category_id, c.category_name
        ORDER BY cnt DESC
        LIMIT 4
    """)
    categories_raw = cursor.fetchall()
    total_cat_products = sum(r["cnt"] for r in categories_raw) or 1
    category_dist = [
        {
            "name": r["category_name"],
            "cnt":  r["cnt"],
            "pct":  round(r["cnt"] / total_cat_products * 100)
        }
        for r in categories_raw
    ]

    # ── Recent Orders (last 5) ──
    cursor.execute("""
        SELECT o.order_id, o.total_amount, o.order_status, o.order_date,
               u.first_name, u.last_name
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        ORDER BY o.order_date DESC
        LIMIT 5
    """)
    recent_orders = cursor.fetchall()

    # ── Recent Users (last 5 registered) ──
    cursor.execute("""
        SELECT user_id, first_name, last_name, email, role_id
        FROM users
        ORDER BY user_id DESC
        LIMIT 5
    """)
    recent_users = cursor.fetchall()

    # ── Monthly Revenue for bar chart (last 6 months) ──
    cursor.execute("""
        SELECT DATE_FORMAT(o.order_date, '%b') AS month_label,
               DATE_FORMAT(o.order_date, '%Y-%m') AS month_key,
               COALESCE(SUM(p.amount), 0) AS revenue
        FROM orders o
        LEFT JOIN payments p ON o.order_id = p.order_id AND p.payment_status = 'Completed'
        GROUP BY month_key, month_label
        ORDER BY month_key DESC
        LIMIT 6
    """)
    monthly_raw = list(reversed(cursor.fetchall()))
    max_rev = max((r["revenue"] for r in monthly_raw), default=1) or 1
    monthly_chart = [
        {
            "label":  r["month_label"],
            "height": max(int(float(r["revenue"]) / max_rev * 100), 5)
        }
        for r in monthly_raw
    ]
    # Pad to 6 bars if fewer months
    while len(monthly_chart) < 6:
        monthly_chart.insert(0, {"label": "—", "height": 5})

    cursor.close()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        total_revenue    = total_revenue,
        all_payments_total = all_payments_total,
        total_orders     = total_orders,
        pending_orders   = pending_orders,
        completed_orders = completed_orders,
        total_customers  = total_customers,
        total_admins     = total_admins,
        total_users      = total_users,
        total_products   = total_products,
        out_of_stock     = out_of_stock,
        low_stock_count  = low_stock_count,
        pending_payments = pending_payments,
        conversion_rate  = conversion_rate,
        top_product      = top_product,
        top_products     = top_products,
        category_dist    = category_dist,
        recent_orders    = recent_orders,
        recent_users     = recent_users,
        monthly_chart    = monthly_chart,
    )


# ====================================
# USERS
# ====================================
@admin.route("/admin/users")
def admin_users():

    if "user_id" not in session:
        return redirect("/login")

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT user_id, first_name, last_name, email, phone, role_id
        FROM users
        ORDER BY user_id DESC
        """
    )
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin_users.html", users=users)


# ====================================
# PRODUCTS
# ====================================
@admin.route("/admin/products")
def admin_products():

    if "user_id" not in session:
        return redirect("/login")

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT p.product_id, p.product_name, p.price, p.stock, p.image_url,
               p.description, p.status,
               c.category_name, b.brand_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        LEFT JOIN brands     b ON p.brand_id     = b.brand_id
        ORDER BY p.product_id DESC
        """
    )
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin_products.html", products=products)


# ====================================
# ORDERS
# ====================================
@admin.route("/admin/orders")
def admin_orders():

    if "user_id" not in session:
        return redirect("/login")

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT order_id, user_id, total_amount, order_status, order_date
        FROM orders
        ORDER BY order_date DESC
        """
    )
    orders = cursor.fetchall()

    # For "New Order" modal dropdowns
    cursor.execute("SELECT user_id, first_name, last_name, email FROM users ORDER BY first_name")
    users_list = cursor.fetchall()

    cursor.execute("SELECT product_id, product_name, price, stock FROM products WHERE stock > 0 ORDER BY product_name")
    products_list = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template(
        "admin_orders.html",
        orders        = orders,
        users_list    = users_list,
        products_list = products_list,
    )


# ====================================
# CREATE NEW ORDER (Admin)
# ====================================
@admin.route("/admin/orders/new", methods=["POST"])
def admin_create_order():
    from flask import request

    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data           = request.get_json()
    cust_user_id   = data.get("user_id")
    product_id     = data.get("product_id")
    quantity       = int(data.get("quantity", 1))
    payment_method = data.get("payment_method", "Cash On Delivery")

    if not cust_user_id or not product_id:
        return jsonify({"error": "User and product are required"}), 400

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get product price
    cursor.execute("SELECT price, stock, product_name FROM products WHERE product_id=%s", (product_id,))
    product = cursor.fetchone()
    if not product:
        cursor.close(); conn.close()
        return jsonify({"error": "Product not found"}), 404
    if product["stock"] < quantity:
        cursor.close(); conn.close()
        return jsonify({"error": f"Only {product['stock']} units in stock"}), 400

    total_amount = float(product["price"]) * quantity

    # Insert order
    cursor.execute(
        "INSERT INTO orders (user_id, total_amount, order_status) VALUES (%s, %s, 'Pending')",
        (cust_user_id, total_amount)
    )
    conn.commit()
    order_id = cursor.lastrowid

    # Insert order item
    cursor.execute(
        "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (%s, %s, %s, %s)",
        (order_id, product_id, quantity, product["price"])
    )

    # Insert payment record
    cursor.execute(
        "INSERT INTO payments (order_id, amount, payment_method, payment_status) VALUES (%s, %s, %s, 'Pending')",
        (order_id, total_amount, payment_method)
    )

    # Reduce stock
    cursor.execute(
        "UPDATE products SET stock = stock - %s WHERE product_id = %s",
        (quantity, product_id)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        "success":    True,
        "order_id":   order_id,
        "product":    product["product_name"],
        "total":      total_amount,
        "message":    f"Order #{order_id} created successfully!"
    })


# ====================================
# PAYMENTS
# ====================================
@admin.route("/admin/payments")
def admin_payments():

    if "user_id" not in session:
        return redirect("/login")

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT payment_id, order_id, amount, payment_method, payment_status
        FROM payments
        ORDER BY payment_id DESC
        """
    )
    payments = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin_payments.html", payments=payments)


# ====================================
# AI INSIGHTS
# ====================================
@admin.route("/admin/ai-insights")
def admin_ai_insights():

    if "user_id" not in session:
        return redirect("/login")

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Most recommended products
    cursor.execute(
        """
        SELECT p.product_id, p.product_name, p.price, p.image_url,
               COUNT(r.recommendation_id) AS rec_count
        FROM recommendations r
        JOIN products p ON r.product_id = p.product_id
        GROUP BY p.product_id, p.product_name, p.price, p.image_url
        ORDER BY rec_count DESC
        LIMIT 10
        """
    )
    top_recommended = cursor.fetchall()

    # Total recommendation count
    cursor.execute("SELECT COUNT(*) AS cnt FROM recommendations")
    total_recs = cursor.fetchone()["cnt"]

    # Top searched terms
    cursor.execute(
        """
        SELECT search_query, COUNT(*) AS cnt
        FROM search_history
        GROUP BY search_query
        ORDER BY cnt DESC
        LIMIT 10
        """
    )
    top_searches = cursor.fetchall()

    # Most viewed products
    cursor.execute(
        """
        SELECT p.product_id, p.product_name, p.price, p.image_url,
               COUNT(pv.view_id) AS view_count
        FROM product_views pv
        JOIN products p ON pv.product_id = p.product_id
        GROUP BY p.product_id, p.product_name, p.price, p.image_url
        ORDER BY view_count DESC
        LIMIT 8
        """
    )
    most_viewed = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "admin_ai_insights.html",
        top_recommended = top_recommended,
        total_recs      = total_recs,
        top_searches    = top_searches,
        most_viewed     = most_viewed,
    )


# ====================================
# INVENTORY HEALTH
# ====================================
@admin.route("/admin/inventory")
def admin_inventory():

    if "user_id" not in session:
        return redirect("/login")

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # All products with category, sorted by stock ascending (low stock first)
    cursor.execute(
        """
        SELECT p.product_id, p.product_name, p.price, p.stock, p.image_url,
               p.status, c.category_name, b.brand_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        LEFT JOIN brands     b ON p.brand_id     = b.brand_id
        ORDER BY p.stock ASC
        """
    )
    all_products = cursor.fetchall()

    # Count by stock level
    cursor.execute("SELECT COUNT(*) AS cnt FROM products WHERE stock = 0")
    out_of_stock = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) AS cnt FROM products WHERE stock > 0 AND stock <= 10")
    low_stock = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) AS cnt FROM products WHERE stock > 10 AND stock <= 50")
    medium_stock = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) AS cnt FROM products WHERE stock > 50")
    healthy_stock = cursor.fetchone()["cnt"]

    cursor.close()
    conn.close()

    return render_template(
        "admin_inventory.html",
        all_products  = all_products,
        out_of_stock  = out_of_stock,
        low_stock     = low_stock,
        medium_stock  = medium_stock,
        healthy_stock = healthy_stock,
    )