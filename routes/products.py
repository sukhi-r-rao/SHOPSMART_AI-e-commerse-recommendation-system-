from flask import Blueprint
from flask import render_template
from flask import session

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
        SELECT *
        FROM products
        WHERE status='Active'
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

    conn = get_db_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM products
        WHERE product_id=%s
        """,
        (product_id,)
    )

    product = cursor.fetchone()

    # Save Product View
    if "user_id" in session:

        user_id = session["user_id"]

        cursor.execute(
            """
            INSERT INTO product_views
            (user_id, product_id)
            VALUES (%s, %s)
            """,
            (user_id, product_id)
        )

        cursor.execute(
            """
            INSERT INTO browsing_history
            (user_id, product_id)
            VALUES (%s, %s)
            """,
            (user_id, product_id)
        )

        conn.commit()

    cursor.close()
    conn.close()

    return render_template(
        "product_detail.html",
        product=product
    )