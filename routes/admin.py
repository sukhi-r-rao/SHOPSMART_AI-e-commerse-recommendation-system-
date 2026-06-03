from flask import Blueprint
from flask import render_template

from database import get_db_connection

admin = Blueprint("admin", __name__)


# ====================================
# ADMIN DASHBOARD
# ====================================

@admin.route("/admin")
def admin_dashboard():

    conn = get_db_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT COUNT(*) AS total_users FROM users"
    )
    users = cursor.fetchone()

    cursor.execute(
        "SELECT COUNT(*) AS total_products FROM products"
    )
    products = cursor.fetchone()

    cursor.execute(
        "SELECT COUNT(*) AS total_orders FROM orders"
    )
    orders = cursor.fetchone()

    cursor.execute(
        "SELECT COUNT(*) AS total_payments FROM payments"
    )
    payments = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        users=users,
        products=products,
        orders=orders,
        payments=payments
    )


# ====================================
# USERS
# ====================================

@admin.route("/admin/users")
def admin_users():

    conn = get_db_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            user_id,
            first_name,
            last_name,
            email,
            phone
        FROM users
        """
    )

    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "admin_users.html",
        users=users
    )


# ====================================
# PRODUCTS
# ====================================

@admin.route("/admin/products")
def admin_products():

    conn = get_db_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            product_id,
            product_name,
            price,
            stock
        FROM products
        """
    )

    products = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "admin_products.html",
        products=products
    )


# ====================================
# ORDERS
# ====================================

@admin.route("/admin/orders")
def admin_orders():

    conn = get_db_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            order_id,
            user_id,
            total_amount,
            order_status,
            order_date
        FROM orders
        """
    )

    orders = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "admin_orders.html",
        orders=orders
    )


# ====================================
# PAYMENTS
# ====================================

@admin.route("/admin/payments")
def admin_payments():

    conn = get_db_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            payment_id,
            order_id,
            amount,
            payment_method,
            payment_status
        FROM payments
        """
    )

    payments = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "admin_payments.html",
        payments=payments
    )