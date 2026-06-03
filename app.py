from flask import Flask, session, render_template, redirect
from flask import get_flashed_messages, flash

from config import Config

from routes.auth import auth
from routes.products import products
from routes.search import search
from routes.cart import cart
from routes.orders import orders
from routes.wishlist import wishlist
from routes.recommendations import recommendations
from routes.admin import admin

from database import get_db_connection

app = Flask(__name__)
app.config["SECRET_KEY"] = Config.SECRET_KEY

# Register Blueprints
app.register_blueprint(auth)
app.register_blueprint(products)
app.register_blueprint(search)
app.register_blueprint(cart)
app.register_blueprint(orders)
app.register_blueprint(wishlist)
app.register_blueprint(recommendations)
app.register_blueprint(admin)


# =========================
# HOME / LANDING PAGE
# =========================
@app.route("/")
def home():
    return render_template("index.html")


# =========================
# PROFILE / DASHBOARD
# =========================
@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    user_name = session.get("user_name", "User")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Total orders
    cursor.execute(
        "SELECT COUNT(*) AS count FROM orders WHERE user_id=%s",
        (user_id,)
    )
    order_count = cursor.fetchone()["count"]

    # Wishlist count
    cursor.execute(
        "SELECT COUNT(*) AS count FROM wishlist WHERE user_id=%s",
        (user_id,)
    )
    wishlist_count = cursor.fetchone()["count"]

    # Cart items count
    cursor.execute(
        """
        SELECT COALESCE(SUM(ci.quantity), 0) AS count
        FROM cart c
        JOIN cart_items ci ON c.cart_id = ci.cart_id
        WHERE c.user_id=%s
        """,
        (user_id,)
    )
    cart_count = cursor.fetchone()["count"] or 0

    # Recently viewed products — use MAX(viewed_at) to avoid DISTINCT + ORDER BY conflict
    cursor.execute(
        """
        SELECT p.product_id, p.product_name, p.price, p.image_url,
               MAX(pv.viewed_at) AS last_viewed
        FROM product_views pv
        JOIN products p ON pv.product_id = p.product_id
        WHERE pv.user_id = %s
        GROUP BY p.product_id, p.product_name, p.price, p.image_url
        ORDER BY last_viewed DESC
        LIMIT 5
        """,
        (user_id,)
    )
    recently_viewed = cursor.fetchall()

    # Recent searches — use GROUP BY + MAX to avoid DISTINCT + ORDER BY MySQL conflict
    cursor.execute(
        """
        SELECT search_query, MAX(searched_at) AS last_searched
        FROM search_history
        WHERE user_id=%s
        GROUP BY search_query
        ORDER BY last_searched DESC
        LIMIT 6
        """,
        (user_id,)
    )
    recent_searches = cursor.fetchall()

    # Recent orders
    cursor.execute(
        """
        SELECT order_id, total_amount, order_status, order_date
        FROM orders
        WHERE user_id=%s
        ORDER BY order_date DESC
        LIMIT 3
        """,
        (user_id,)
    )
    recent_orders = cursor.fetchall()

    # AI suggestions count (from recommendations table)
    cursor.execute(
        "SELECT COUNT(*) AS count FROM recommendations WHERE user_id=%s",
        (user_id,)
    )
    ai_suggestions = cursor.fetchone()["count"] or 12

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        user_name=user_name,
        order_count=order_count,
        wishlist_count=wishlist_count,
        cart_count=cart_count,
        recently_viewed=recently_viewed,
        recent_searches=recent_searches,
        recent_orders=recent_orders,
        ai_suggestions=ai_suggestions
    )


# =========================
# USER ORDER HISTORY
# =========================
@app.route("/orders")
def user_orders():
    if "user_id" not in session:
        return redirect("/login")

    user_id   = session["user_id"]
    user_name = session.get("user_name", "User")

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # All orders for this user
    cursor.execute(
        """
        SELECT o.order_id, o.total_amount, o.order_status, o.order_date,
               p.payment_method, p.payment_status
        FROM orders o
        LEFT JOIN payments p ON o.order_id = p.order_id
        WHERE o.user_id = %s
        ORDER BY o.order_date DESC
        """,
        (user_id,)
    )
    orders_list = cursor.fetchall()

    # Cast Decimal to float
    for o in orders_list:
        o["total_amount"] = float(o["total_amount"] or 0)

    # Get items for each order
    for o in orders_list:
        cursor.execute(
            """
            SELECT oi.quantity, oi.unit_price,
                   p.product_name, p.image_url
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = %s
            """,
            (o["order_id"],)
        )
        items = cursor.fetchall()
        for item in items:
            item["unit_price"] = float(item["unit_price"] or 0)
        o["order_lines"] = items

    cursor.close()
    conn.close()

    return render_template(
        "orders.html",
        orders_list = orders_list,
        user_name   = user_name,
    )


if __name__ == "__main__":
    app.run(debug=True)