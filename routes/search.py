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
            SELECT *
            FROM products
            WHERE product_name LIKE %s
            """
            ,
            ('%' + query + '%',)
        )

        products = cursor.fetchall()

        cursor.close()
        conn.close()

    return render_template(
        "search_results.html",
        products=products,
        query=query
    )