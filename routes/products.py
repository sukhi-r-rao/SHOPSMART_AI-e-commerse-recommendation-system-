from flask import Blueprint, render_template, session

from database import get_db_connection

products = Blueprint('products', __name__)


# -----------------------------
# Product Listing Page
# -----------------------------
@products.route("/products")
def product_list():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            p.product_id,
            p.product_name,
            p.price,
            p.stock,
            p.image_url,
            p.description,
            p.status,
            c.category_name,
            b.brand_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        LEFT JOIN brands b ON p.brand_id = b.brand_id
        WHERE p.status='Active'
        ORDER BY p.product_id
    """)

    products_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "products.html",
        products=products_data
    )


# -----------------------------
# Product Detail Page
# -----------------------------
@products.route("/product/<int:product_id>")
def product_detail(product_id):

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Main product
    cursor.execute(
        """
        SELECT p.*, c.category_name, b.brand_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        LEFT JOIN brands b     ON p.brand_id     = b.brand_id
        WHERE p.product_id = %s
        """,
        (product_id,)
    )
    product = cursor.fetchone()

    # Similar products (same category, different product, limit 4)
    similar_products = []
    if product and product.get("category_id"):
        cursor.execute(
            """
            SELECT p.product_id, p.product_name, p.price, p.image_url,
                   b.brand_name
            FROM products p
            LEFT JOIN brands b ON p.brand_id = b.brand_id
            WHERE p.category_id = %s
              AND p.product_id  != %s
              AND p.status = 'Active'
            ORDER BY RAND()
            LIMIT 4
            """,
            (product["category_id"], product_id)
        )
        similar_products = cursor.fetchall()

    # Cart count for navbar badge
    cart_count = 0
    if "user_id" in session:
        user_id = session["user_id"]

        # Log product view
        try:
            cursor.execute(
                "INSERT INTO product_views (user_id, product_id) VALUES (%s, %s)",
                (user_id, product_id)
            )
            cursor.execute(
                "INSERT INTO browsing_history (user_id, product_id) VALUES (%s, %s)",
                (user_id, product_id)
            )
            conn.commit()
        except Exception:
            conn.rollback()

        cursor.execute(
            """
            SELECT COALESCE(SUM(ci.quantity), 0) AS cnt
            FROM cart c
            JOIN cart_items ci ON c.cart_id = ci.cart_id
            WHERE c.user_id = %s
            """,
            (user_id,)
        )
        cart_count = cursor.fetchone()["cnt"] or 0

    cursor.close()
    conn.close()

    return render_template(
        "product_detail.html",
        product         = product,
        similar_products= similar_products,
        cart_count      = cart_count,
    )