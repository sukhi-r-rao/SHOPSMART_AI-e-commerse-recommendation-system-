from flask import Blueprint, session, redirect, render_template, flash

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

    # Get or create cart
    cursor.execute("SELECT * FROM cart WHERE user_id=%s", (user_id,))
    existing_cart = cursor.fetchone()

    if existing_cart:
        cart_id = existing_cart["cart_id"]
    else:
        cursor.execute("INSERT INTO cart(user_id) VALUES(%s)", (user_id,))
        conn.commit()
        cart_id = cursor.lastrowid

    # Check if product already in cart
    cursor.execute(
        "SELECT * FROM cart_items WHERE cart_id=%s AND product_id=%s",
        (cart_id, product_id)
    )
    item = cursor.fetchone()

    if item:
        cursor.execute(
            "UPDATE cart_items SET quantity = quantity + 1 WHERE cart_item_id=%s",
            (item["cart_item_id"],)
        )
    else:
        cursor.execute(
            "INSERT INTO cart_items (cart_id, product_id, quantity) VALUES(%s,%s,1)",
            (cart_id, product_id)
        )

    conn.commit()
    cursor.close()
    conn.close()

    flash("Product added to cart!", "success")
    return redirect("/cart")


# -------------------------
# View Cart
# -------------------------
@cart.route("/cart")
def view_cart():

    if "user_id" not in session:
        return redirect("/login")

    user_id   = session["user_id"]
    user_name = session.get("user_name", "User")

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Full cart items with image and cart_item_id
    cursor.execute(
        """
        SELECT
            ci.cart_item_id,
            ci.quantity,
            p.product_id,
            p.product_name,
            p.price,
            p.image_url
        FROM cart_items ci
        JOIN cart c  ON ci.cart_id   = c.cart_id
        JOIN products p ON ci.product_id = p.product_id
        WHERE c.user_id = %s
        """,
        (user_id,)
    )
    cart_items = cursor.fetchall()

    # Cast Decimal → float for every item so Jinja arithmetic works
    for item in cart_items:
        item["price"] = float(item["price"])

    # Subtotal
    subtotal   = sum(float(i["price"]) * int(i["quantity"]) for i in cart_items)
    ai_savings = round(subtotal * 0.10, 2)   # 10 % AI discount demo

    # "Complete the look" – 3 random products not in cart
    in_cart_ids = [i["product_id"] for i in cart_items] or [0]
    placeholders = ",".join(["%s"] * len(in_cart_ids))
    cursor.execute(
        f"""
        SELECT product_id, product_name, price, image_url
        FROM products
        WHERE product_id NOT IN ({placeholders}) AND status='Active'
        ORDER BY RAND()
        LIMIT 3
        """,
        tuple(in_cart_ids)
    )
    look_products = cursor.fetchall()
    for lp in look_products:
        lp["price"] = float(lp["price"])

    cursor.close()
    conn.close()

    return render_template(
        "cart.html",
        cart_items    = cart_items,
        subtotal      = subtotal,
        ai_savings    = ai_savings,
        look_products = look_products,
        user_name     = user_name,
    )


# -------------------------
# Remove Cart Item
# -------------------------
@cart.route("/remove-from-cart/<int:cart_item_id>")
def remove_from_cart(cart_item_id):

    if "user_id" not in session:
        return redirect("/login")

    conn   = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart_items WHERE cart_item_id=%s", (cart_item_id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Item removed from cart.", "success")
    return redirect("/cart")
