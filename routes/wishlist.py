from flask import Blueprint
from flask import session
from flask import redirect
from flask import render_template

from database import get_db_connection

wishlist = Blueprint("wishlist", __name__)


# --------------------------
# Add To Wishlist
# --------------------------
@wishlist.route("/wishlist/add/<int:product_id>")
def add_to_wishlist(product_id):

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM wishlist
        WHERE user_id=%s
        AND product_id=%s
        """,
        (user_id, product_id)
    )

    existing = cursor.fetchone()

    if not existing:

        cursor.execute(
            """
            INSERT INTO wishlist
            (user_id, product_id)
            VALUES (%s,%s)
            """,
            (user_id, product_id)
        )

        conn.commit()

    cursor.close()
    conn.close()

    return redirect("/wishlist")


# --------------------------
# View Wishlist
# --------------------------
@wishlist.route("/wishlist")
def view_wishlist():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = get_db_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            w.wishlist_id,
            p.product_id,
            p.product_name,
            p.price,
            p.image_url
        FROM wishlist w
        JOIN products p
        ON w.product_id = p.product_id
        WHERE w.user_id=%s
        """,
        (user_id,)
    )

    wishlist_items = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "wishlist.html",
        wishlist_items=wishlist_items
    )


# --------------------------
# Remove Wishlist Item
# --------------------------
@wishlist.route("/wishlist/remove/<int:wishlist_id>")
def remove_wishlist(wishlist_id):

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM wishlist
        WHERE wishlist_id=%s
        """,
        (wishlist_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/wishlist")