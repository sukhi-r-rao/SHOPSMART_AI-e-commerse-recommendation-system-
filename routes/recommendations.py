from flask import Blueprint
from flask import session
from flask import redirect
from flask import render_template

from database import get_db_connection

recommendations = Blueprint("recommendations", __name__)


@recommendations.route("/recommendations")
def show_recommendations():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Clear old recommendations
    cursor.execute(
        """
        DELETE FROM recommendations
        WHERE user_id=%s
        """,
        (user_id,)
    )

    conn.commit()

    # Products viewed by user
    cursor.execute(
        """
        SELECT product_id
        FROM product_views
        WHERE user_id=%s
        """,
        (user_id,)
    )

    viewed_products = cursor.fetchall()

    viewed_ids = [item["product_id"] for item in viewed_products]

    if viewed_ids:

        placeholders = ",".join(["%s"] * len(viewed_ids))

        query = f"""
        SELECT product_id
        FROM products
        WHERE product_id NOT IN ({placeholders})
        """

        cursor.execute(query, tuple(viewed_ids))

    else:

        cursor.execute(
            """
            SELECT product_id
            FROM products
            """
        )

    products = cursor.fetchall()

    # Insert recommendations
    for product in products:

        cursor.execute(
            """
            INSERT INTO recommendations
            (
                user_id,
                product_id,
                score
            )
            VALUES
            (%s,%s,%s)
            """,
            (
                user_id,
                product["product_id"],
                5.0
            )
        )

    conn.commit()

    # Fetch recommendations
    cursor.execute(
        """
        SELECT
            r.recommendation_id,
            r.score,
            p.product_id,
            p.product_name,
            p.price,
            p.image_url
        FROM recommendations r
        JOIN products p
        ON r.product_id = p.product_id
        WHERE r.user_id=%s
        ORDER BY r.score DESC
        """,
        (user_id,)
    )

    recommendations_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "recommendations.html",
        recommendations=recommendations_data
    )