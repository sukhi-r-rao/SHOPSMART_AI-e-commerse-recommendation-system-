from flask import Blueprint, session, redirect, render_template, flash

from database import get_db_connection

wishlist = Blueprint("wishlist", __name__)


# --------------------------
# Add To Wishlist  (both URL patterns)
# --------------------------
@wishlist.route("/wishlist/add/<int:product_id>")
@wishlist.route("/add-to-wishlist/<int:product_id>")
def add_to_wishlist(product_id):

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM wishlist WHERE user_id=%s AND product_id=%s",
        (user_id, product_id)
    )
    existing = cursor.fetchone()

    if not existing:
        cursor.execute(
            "INSERT INTO wishlist (user_id, product_id) VALUES (%s,%s)",
            (user_id, product_id)
        )
        conn.commit()
        flash("Added to wishlist!", "success")
    else:
        flash("Already in your wishlist.", "success")

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
    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # All wishlist items with product info
    cursor.execute(
        """
        SELECT
            w.wishlist_id,
            p.product_id,
            p.product_name,
            p.price,
            p.image_url
        FROM wishlist w
        JOIN products p ON w.product_id = p.product_id
        WHERE w.user_id = %s
        ORDER BY w.added_at DESC
        """,
        (user_id,)
    )
    wishlist_items = cursor.fetchall()

    # Cart count for navbar
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

    # Estimated savings: 10 % of total wishlist value
    total_wl_value  = sum(i["price"] for i in wishlist_items)
    estimated_savings = round(total_wl_value * 0.10, 2)
    ai_opportunities  = min(len(wishlist_items), 5)

    # Price drops: items whose current price < average (simulation)
    # Use the two cheapest items as "dropped" demos
    price_drops = []
    if len(wishlist_items) >= 2:
        sorted_items = sorted(wishlist_items, key=lambda x: x["price"])
        for item in sorted_items[:2]:
            price_drops.append({
                "product_id":   item["product_id"],
                "product_name": item["product_name"],
                "price":        item["price"],
                "image_url":    item["image_url"],
                "drop_pct":     12,
            })

    cursor.close()
    conn.close()

    return render_template(
        "wishlist.html",
        wishlist_items    = wishlist_items,
        cart_count        = cart_count,
        estimated_savings = estimated_savings,
        ai_opportunities  = ai_opportunities,
        price_drops       = price_drops,
    )


# --------------------------
# Remove Wishlist Item  (both URL patterns)
# --------------------------
@wishlist.route("/wishlist/remove/<int:wishlist_id>")
@wishlist.route("/remove-from-wishlist/<int:wishlist_id>")
def remove_wishlist(wishlist_id):

    conn   = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM wishlist WHERE wishlist_id=%s", (wishlist_id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Item removed from wishlist.", "success")
    return redirect("/wishlist")