from flask import Blueprint
from flask import render_template
from flask import request
from flask import session

from database import get_db_connection

search = Blueprint("search", __name__)


@search.route("/search")
def search_products():

    query = request.args.get("q")

    products = []

    if query:

        conn = get_db_connection()

        cursor = conn.cursor(dictionary=True)

        if "user_id" in session:

            cursor.execute(
                """
                INSERT INTO search_history
                (user_id, search_query)
                VALUES (%s,%s)
                """,
                (
                    session["user_id"],
                    query
                )
            )

            conn.commit()

        cursor.execute(
            """
            SELECT p.product_id, p.product_name, p.price, p.stock,
                   p.image_url, p.description, p.status,
                   c.category_name, b.brand_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
            LEFT JOIN brands     b ON p.brand_id     = b.brand_id
            WHERE p.product_name LIKE %s
               OR p.description  LIKE %s
               OR c.category_name LIKE %s
            ORDER BY p.product_name
            """,
            ('%' + query + '%', '%' + query + '%', '%' + query + '%')
        )

        products = cursor.fetchall()

        cursor.close()
        conn.close()

    return render_template(
        "search_results.html",
        products=products,
        query=query
    )