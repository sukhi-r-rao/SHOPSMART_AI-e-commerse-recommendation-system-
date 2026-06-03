from flask import Blueprint, session, redirect, render_template

from database import get_db_connection

recommendations = Blueprint("recommendations", __name__)


@recommendations.route("/recommendations")
def show_recommendations():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ── Products already viewed ──────────────────────────────────────
    cursor.execute(
        "SELECT DISTINCT product_id FROM product_views WHERE user_id=%s",
        (user_id,)
    )
    viewed_ids = [r["product_id"] for r in cursor.fetchall()]

    # ── Build recommended products (not viewed) ──────────────────────
    if viewed_ids:
        placeholders = ",".join(["%s"] * len(viewed_ids))
        cursor.execute(
            f"""
            SELECT p.product_id, p.product_name, p.price, p.image_url,
                   c.category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
            WHERE p.product_id NOT IN ({placeholders})
              AND p.status = 'Active'
            ORDER BY RAND()
            LIMIT 20
            """,
            tuple(viewed_ids)
        )
    else:
        cursor.execute(
            """
            SELECT p.product_id, p.product_name, p.price, p.image_url,
                   c.category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
            WHERE p.status = 'Active'
            ORDER BY RAND()
            LIMIT 20
            """
        )
    all_recs = cursor.fetchall()

    # ── Persist fresh recommendations ───────────────────────────────
    cursor.execute("DELETE FROM recommendations WHERE user_id=%s", (user_id,))
    conn.commit()

    for product in all_recs:
        cursor.execute(
            """
            INSERT INTO recommendations (user_id, product_id, score)
            VALUES (%s, %s, %s)
            """,
            (user_id, product["product_id"], 5.0)
        )
    conn.commit()

    # ── Featured product (first recommendation) ──────────────────────
    featured_product = all_recs[0] if all_recs else None

    # ── Browsing-history products (most recently viewed) ─────────────
    cursor.execute(
        """
        SELECT p.product_id, p.product_name, p.price,
               p.image_url, c.category_name,
               MAX(pv.viewed_at) AS last_viewed
        FROM product_views pv
        JOIN products p ON pv.product_id = p.product_id
        LEFT JOIN categories c ON p.category_id = c.category_id
        WHERE pv.user_id = %s
        GROUP BY p.product_id, p.product_name, p.price,
                 p.image_url, c.category_name
        ORDER BY last_viewed DESC
        LIMIT 4
        """,
        (user_id,)
    )
    browse_products = cursor.fetchall()

    # ── Counts for hero stats ─────────────────────────────────────────
    rec_count   = len(all_recs)
    views_count = len(viewed_ids)

    cursor.close()
    conn.close()

    return render_template(
        "recommendations.html",
        featured_product = featured_product,
        browse_products  = browse_products,
        rec_count        = rec_count,
        views_count      = views_count,
    )