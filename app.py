from flask import Flask
from flask import session

from config import Config

from routes.auth import auth
from routes.products import products
from routes.search import search
from routes.cart import cart
from routes.orders import orders
from routes.wishlist import wishlist
from routes.recommendations import recommendations
from routes.admin import admin

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


@app.route("/")
def home():

    return """
    <h1>ShopSmart AI</h1>

    <ul>

        <li><a href="/register">Register</a></li>
        <li><a href="/login">Login</a></li>
        <li><a href="/profile">Profile</a></li>

        <br>

        <li><a href="/products">Products</a></li>
        <li><a href="/cart">My Cart</a></li>
        <li><a href="/wishlist">Wishlist</a></li>

        <br>

        <li><a href="/recommendations">Recommendations</a></li>
        <li><a href="/checkout">Checkout</a></li>

        <br>

        <li><a href="/admin">Admin Dashboard</a></li>

    </ul>
    """


@app.route("/profile")
def profile():

    if "user_id" not in session:
        return "Please Login First"

    return f"""
    <h1>Welcome {session['user_name']}</h1>

    <p>User ID: {session['user_id']}</p>

    <a href="/products">Products</a>

    <br><br>

    <a href="/logout">Logout</a>
    """


if __name__ == "__main__":
    app.run(debug=True)