from flask import Blueprint
from flask import session
from flask import redirect

from database import get_db_connection

orders = Blueprint("orders", __name__)


@orders.route("/checkout")
def checkout():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get Cart
    cursor.execute(
        """
        SELECT cart_id
        FROM cart
        WHERE user_id=%s
        """,
        (user_id,)
    )

    cart = cursor.fetchone()

    if not cart:
        return "Cart is Empty"

    cart_id = cart["cart_id"]

    # Get Cart Items
    cursor.execute(
        """
        SELECT
            ci.product_id,
            ci.quantity,
            p.price
        FROM cart_items ci
        JOIN products p
            ON ci.product_id = p.product_id
        WHERE ci.cart_id=%s
        """,
        (cart_id,)
    )

    cart_items = cursor.fetchall()

    if not cart_items:
        return "Cart is Empty"

    total_amount = 0

    for item in cart_items:
        total_amount += (
            item["quantity"] *
            float(item["price"])
        )

    # Create Order
    cursor.execute(
        """
        INSERT INTO orders
        (user_id,total_amount)
        VALUES(%s,%s)
        """,
        (user_id,total_amount)
    )

    conn.commit()

    order_id = cursor.lastrowid

    # Create Order Items
    for item in cart_items:

        cursor.execute(
            """
            INSERT INTO order_items
            (
                order_id,
                product_id,
                quantity,
                unit_price
            )
            VALUES(%s,%s,%s,%s)
            """,
            (
                order_id,
                item["product_id"],
                item["quantity"],
                item["price"]
            )
        )

    # Create Payment
    cursor.execute(
        """
        INSERT INTO payments
        (
            order_id,
            amount,
            payment_method,
            payment_status
        )
        VALUES
        (%s,%s,'Cash On Delivery','Pending')
        """,
        (
            order_id,
            total_amount
        )
    )

    # Clear Cart
    cursor.execute(
        """
        DELETE FROM cart_items
        WHERE cart_id=%s
        """,
        (cart_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return f"Order Created Successfully. Order ID: {order_id}"