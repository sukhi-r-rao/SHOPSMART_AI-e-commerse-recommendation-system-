from flask import Blueprint
from flask import session
from flask import redirect
from flask import render_template

from database import get_db_connection

cart = Blueprint("cart", __name__)


# -------------------------
# Add Product To Cart
# -------------------------
@cart.route("/add-to-cart/<int:product_id>")
def add_to_cart(product_id):

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = get_db_connection()

    cursor = conn.cursor(dictionary=True)

    # Check if cart exists
    cursor.execute(
        """
        SELECT *
        FROM cart
        WHERE user_id=%s
        """,
        (user_id,)
    )

    existing_cart = cursor.fetchone()

    if existing_cart:

        cart_id = existing_cart["cart_id"]

    else:

        cursor.execute(
            """
            INSERT INTO cart(user_id)
            VALUES(%s)
            """,
            (user_id,)
        )

        conn.commit()

        cart_id = cursor.lastrowid

    # Check product already in cart
    cursor.execute(
        """
        SELECT *
        FROM cart_items
        WHERE cart_id=%s
        AND product_id=%s
        """,
        (cart_id, product_id)
    )

    item = cursor.fetchone()

    if item:

        cursor.execute(
            """
            UPDATE cart_items
            SET quantity = quantity + 1
            WHERE cart_item_id=%s
            """,
            (item["cart_item_id"],)
        )

    else:

        cursor.execute(
            """
            INSERT INTO cart_items
            (cart_id, product_id, quantity)
            VALUES(%s,%s,1)
            """,
            (cart_id, product_id)
        )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/cart")


# -------------------------
# View Cart
# -------------------------
@cart.route("/cart")
def view_cart():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = get_db_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            p.product_name,
            p.price,
            c.quantity
        FROM cart_items c
        JOIN products p
            ON c.product_id=p.product_id
        JOIN cart ct
            ON c.cart_id=ct.cart_id
        WHERE ct.user_id=%s
        """,
        (user_id,)
    )

    cart_items = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "cart.html",
        cart_items=cart_items
    )
