from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId
import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "defaultsecret")

# MongoDB connection
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
db = client["agri_connect"]  # ✅ unified DB name
users_col = db["users"]
products_col = db["products"]
cart_col = db["cart"]
wishlist_col = db["wishlist"]
news_col = db["news"]
knowledge_col = db["knowledge"]
crops_col = db["crops"]
schemes_col = db["schemes"]
orders_col = db["orders"]


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/profile")
def profile():
    if not session.get("user"):
        flash("Please log in to view your profile.", "warning")
        return redirect(url_for("login"))
    return render_template("profile.html", name=session.get("name"), email=session.get("user"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        if users_col.find_one({"email": email}):
            flash("User already exists. Please login.", "error")
            return redirect(url_for("login"))

        hashed_pw = generate_password_hash(password)
        users_col.insert_one({
            "name": name,
            "email": email,
            "password": hashed_pw,
            "role": "user"  # 🔥 Default user role
        })
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# --- USER LOGIN ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]
        user = users_col.find_one({"email": email})
        if user and check_password_hash(user["password"], password):
            # Keep old key for your existing cart/wishlist logic
            session["user"] = user["email"]
            # Add richer session data
            session["email"] = user["email"]
            session["name"]  = user.get("name", "User")
            session["role"]  = user.get("role", "user")
            flash(f"Welcome back, {session['name']}! 👋", "success")
            return redirect(url_for("home"))
        flash("Invalid credentials. Try again.", "error")
        return redirect(url_for("login"))
    return render_template("login.html")


# --- ADMIN LOGIN ---
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]
        admin = users_col.find_one({"email": email, "role": "admin"})
        if admin and check_password_hash(admin["password"], password):
            session["user"]  = admin["email"]       # for existing logic
            session["email"] = admin["email"]
            session["name"]  = admin.get("name", "Admin")
            session["role"] = "admin"
            flash(f"Welcome, {session['name']} (Admin) ✅", "success")
            return redirect(url_for("admin_dashboard"))
        flash("Invalid admin credentials.", "error")
        return redirect(url_for("admin_login"))
    return render_template("admin_login.html")

@app.route("/admin")
def admin_dashboard():
    if "user" not in session or session.get("role") != "admin":
        flash("Access denied!", "error")
        return redirect(url_for("home"))

    products = list(products_col.find())
    users = list(users_col.find())
    return render_template("admin_dashboard.html", products=products, users=users)


# --- LOGOUT ---
@app.route("/logout")
def logout():
    session.clear()  # ✅ Clears ALL session data
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("login"))

@app.route("/products")
def products():
    items = list(products_col.find())
    return render_template("products.html", products=items)

@app.route("/add-to-cart/<product_id>")
def add_to_cart(product_id):
    if "user" not in session:
        return redirect(url_for("login"))

    product = products_col.find_one({"_id": ObjectId(product_id)})
    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("products"))

    existing_item = cart_col.find_one({"user": session["user"], "product_id": product_id})
    if existing_item:
        cart_col.update_one(
            {"_id": existing_item["_id"]},
            {"$inc": {"quantity": 1}}
        )
    else:
        cart_col.insert_one({
            "user": session["user"],  # email
            "product_id": product_id,
            "name": product["name"],
            "price": product["price"],
            "image": product["image"],
            "quantity": 1
        })

    flash("✅ Added to cart!", "success")
    return redirect(url_for("view_cart"))


@app.route("/remove-from-cart/<product_id>")
def remove_from_cart(product_id):
    if "user" in session:
        cart_col.delete_one({"user": session["user"], "product_id": product_id})
    return redirect(url_for("view_cart"))

@app.route("/add-to-wishlist/<product_id>")
def add_to_wishlist(product_id):
    if "user" not in session:
        return redirect(url_for("login"))

    if not wishlist_col.find_one({"user": session["user"], "product_id": product_id}):  # ✅ avoid duplicates
        wishlist_col.insert_one({"user": session["user"], "product_id": product_id})

    return redirect(url_for("view_wishlist"))

@app.route("/remove-from-wishlist/<product_id>")
def remove_from_wishlist(product_id):
    if "user" in session:
        wishlist_col.delete_one({"user": session["user"], "product_id": product_id})
    return redirect(url_for("view_wishlist"))

@app.route("/cart")
def view_cart():
    if "user" not in session:
        return redirect(url_for("login"))

    cart_items = list(cart_col.find({"user": session["user"]}))
    products = [products_col.find_one({"_id": ObjectId(item["product_id"])}) for item in cart_items]
    return render_template("cart.html", products=products)

@app.route("/wishlist")
def view_wishlist():
    if "user" not in session:
        return redirect(url_for("login"))

    wishlist_items = list(wishlist_col.find({"user": session["user"]}))
    products = [products_col.find_one({"_id": ObjectId(item["product_id"])}) for item in wishlist_items]
    return render_template("wishlist.html", products=products)


@app.route("/seeds")
def seeds():
    items = list(products_col.find({"category": "seeds"}))
    return render_template("seeds.html", products=items)

@app.route("/tools")
def tools():
    items = list(products_col.find({"category": "tools"}))
    return render_template("tools.html", products=items)

@app.route("/pesticides")
def pesticides():
    items = list(products_col.find({"category": "pesticides"}))
    return render_template("pesticides.html", products=items)

@app.route("/fertilizers")
def fertilizers():
    items = list(products_col.find({"category": "fertilizers"}))
    return render_template("fertilizers.html", products=items)

@app.route("/cropsdetails")
def cropsdetails():
    items = list(crops_col.find())
    return render_template("cropsdetails.html", crops=items)

@app.route("/govschemes")
def govschemes():
    items = list(schemes_col.find())
    return render_template("govschemes.html", schemes=items)

@app.route("/news")
def news():
    items = list(news_col.find())
    return render_template("news.html", news=items)

@app.route("/knowledgehub")
def knowledgehub():
    items = list(knowledge_col.find())
    return render_template("knowledgehub.html", knowledge=items)

@app.route("/checkout")
def checkout():
    if not session.get("user"):
        flash("Please login to proceed with checkout.", "error")
        return redirect(url_for("login"))

    user = session["user"]
    cart_items = list(cart_col.find({"user": user}))

    if not cart_items:
        flash("Your cart is empty!", "warning")
        return redirect(url_for("products"))

    subtotal = sum(item["price"] * item.get("quantity", 1) for item in cart_items)
    tax = round(subtotal * 0.05, 2)
    grandtotal = subtotal + tax

    return render_template(
        "checkout.html",
        cart=cart_items,
        subtotal=subtotal,
        tax=tax,
        grandtotal=grandtotal
    )


@app.route("/place_order", methods=["POST"])
def place_order():
    if not session.get("user"):
        flash("Please login to place an order.", "error")
        return redirect(url_for("login"))

    user = session["user"]
    payment_method = request.form.get("payment")
    cart_items = list(cart_col.find({"user": user}))

    if not cart_items:
        flash("Cart is empty, cannot place order.", "error")
        return redirect(url_for("products"))

    subtotal = sum(item["price"] * item.get("quantity", 1) for item in cart_items)
    tax = round(subtotal * 0.05, 2)
    grandtotal = subtotal + tax

    order = {
        "user": user,
        "items": cart_items,
        "subtotal": subtotal,
        "tax": tax,
        "grandtotal": grandtotal,
        "payment_method": payment_method,
        "status": "Pending",
        "created_at": datetime.datetime.now()
    }

    orders_col.insert_one(order)
    cart_col.delete_many({"user": user})

    flash("✅ Order placed successfully!", "success")
    return redirect(url_for("home"))

@app.route("/update-cart/<cart_id>/<action>")
def update_cart(cart_id, action):
    item = cart_col.find_one({"_id": ObjectId(cart_id)})
    if not item:
        flash("Item not found in cart.", "error")
        return redirect(url_for("checkout"))

    if action == "inc":
        cart_col.update_one({"_id": item["_id"]}, {"$inc": {"quantity": 1}})
    elif action == "dec" and item.get("quantity", 1) > 1:
        cart_col.update_one({"_id": item["_id"]}, {"$inc": {"quantity": -1}})
    else:
        cart_col.delete_one({"_id": item["_id"]})

    return redirect(url_for("checkout"))

@app.route("/empty-cart")
def empty_cart():
    if "user" not in session:
        flash("Please login first.", "error")
        return redirect(url_for("login"))

    cart_col.delete_many({"user": session["user"]})
    flash("🗑 Your cart has been emptied.", "success")
    return redirect(url_for("checkout"))



if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
