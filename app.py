from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId
from datetime import datetime
import razorpay
from itsdangerous import URLSafeTimedSerializer
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_mail import Mail, Message


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "defaultsecret")


app.config.update(
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_USE_TLS=os.getenv("MAIL_USE_TLS", "True") == "True",
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD")
)

mail = Mail(app)

# Token serializer
s = URLSafeTimedSerializer(app.secret_key)


RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


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

    # Fetch all orders
    orders = list(orders_col.find().sort("created_at", -1))  # ✅ Call find()

    # Convert ObjectId to string for Jinja
    for order in orders:
        order["_id"] = str(order["_id"])
        for item in order.get("items", []):
            item["name"] = item.get("name", "Unknown")
            item["price"] = item.get("price", 0)
            item["quantity"] = item.get("quantity", 1)

    return render_template("admin_dashboard.html", orders=orders)



# --- LOGOUT ---
@app.route("/logout")
def logout():
    session.clear()  # ✅ Clears ALL session data
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("login"))

# @app.route("/products")
# def products():
#     items = list(products_col.find())
#     return render_template("products.html", products=items)
@app.route("/products")
def products():
    query = request.args.get("q", "").strip().lower()

    if query:
        # Search products by name or description (case-insensitive)
        items = list(products_col.find({
            "$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}}
            ]
        }))
    else:
        # Show all products by default
        items = list(products_col.find({}))

    return render_template("products.html", products=items, query=query)

@app.route("/search_suggestions")
def search_suggestions():
    query = request.args.get("q", "").strip()
    results = []
    if query:
        results = list(products_col.find(
            {"name": {"$regex": query, "$options": "i"}},
            {"name": 1, "_id": 0}
        ).limit(10))
    return jsonify(results)

@app.route("/add_to_cart/<product_id>")
def add_to_cart(product_id):
    if not session.get("user"):
        flash("Please login to add items to cart.", "error")
        return redirect(url_for("login"))

    user_email = session.get("email")
    print("SESSION EMAIL IN CART:", user_email)  # ✅ debug

    product = db.products.find_one({"_id": ObjectId(product_id)})
    if not product:
        flash("Product not found!", "error")
        return redirect(url_for("products"))

    existing = db.cart.find_one({"product_id": product_id, "user_email": user_email})
    if existing:
        db.cart.update_one({"_id": existing["_id"]}, {"$inc": {"quantity": 1}})
        print("UPDATED CART ITEM:", existing)  # ✅ debug
    else:
        cart_doc = {
            "product_id": product_id,
            "name": product["name"],
            "price": product["price"],
            "image": product.get("image", "images/placeholder.png"),
            "quantity": 1,
            "user_email": user_email   # ✅ important
        }
        db.cart.insert_one(cart_doc)
        print("INSERTED CART ITEM:", cart_doc)  # ✅ debug

    flash("Product added to cart.", "success")
    return redirect(url_for("view_cart"))




@app.route("/remove-from-cart/<product_id>")
def remove_from_cart(product_id):
    if "user" in session:
        cart_col.delete_one({"product_id": product_id, "user_email": session["email"]})
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

@app.route("/view_cart")
def view_cart():
    if "user" not in session:
        return redirect(url_for("login"))

    user_email = session.get("email")
    cart_items = list(cart_col.find({"user_email": user_email}))

    products = []
    for item in cart_items:
        product = products_col.find_one({"_id": ObjectId(item["product_id"])})
        if product:
            product["quantity"] = item["quantity"]
            product["cart_id"] = str(item["_id"])
            products.append(product)

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
        flash("Please login first.", "error")
        return redirect(url_for("login"))

    user_email = session.get("email")
    cart_items = list(db.cart.find({"user_email": user_email}))

    if not cart_items:
        flash("Your cart is empty!", "error")
        return redirect(url_for("view_cart"))

    # Totals
    subtotal = sum(item["price"] * item["quantity"] for item in cart_items)
    tax = round(0.05 * subtotal, 2)
    grandtotal = subtotal + tax

    return render_template("checkout.html",
                           cart=cart_items,
                           subtotal=subtotal,
                           tax=tax,
                           grandtotal=grandtotal)


@app.route("/place_order", methods=["POST"])
def place_order():
    if not session.get("user"):
        flash("Please login to place order.", "error")
        return redirect(url_for("login"))

    payment_method = request.form.get("payment")
    user_email = session.get("email")

    cart_items = list(db.cart.find({"user_email": user_email}))
    if not cart_items:
        flash("Your cart is empty!", "error")
        return redirect(url_for("view_cart"))

    # 🧮 Calculate totals
    subtotal = sum(item["price"] * item["quantity"] for item in cart_items)
    tax = round(0.05 * subtotal, 2)
    grand_total = subtotal + tax

    # 🚚 Shipping Info
    shipping_info = {
        "full_name": request.form.get("full_name"),
        "phone": request.form.get("phone"),
        "address": request.form.get("address"),
        "city": request.form.get("city"),
        "state": request.form.get("state"),
        "pincode": request.form.get("pincode")
    }

    if payment_method in ["upi", "card"]:
        # ✅ Razorpay order creation
        razorpay_order = razorpay_client.order.create({
            "amount": int(grand_total * 100),
            "currency": "INR",
            "payment_capture": 1
        })

        order = {
            "user_email": user_email,
            "user": session.get("name"),
            "items": cart_items,
            "grandtotal": grand_total,
            "payment_method": payment_method,
            "status": "Pending Payment",
            "razorpay_order_id": razorpay_order["id"],
            "shipping_info": shipping_info,
            "shipping_status": "Pending",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        db.orders.insert_one(order)

        return render_template(
            "razorpay_checkout.html",
            razorpay_order=razorpay_order,
            grandtotal=grand_total,
            user_email=user_email,
            order=order,
            key_id=RAZORPAY_KEY_ID
        )

    else:
        # ✅ COD flow
        order = {
            "user_email": user_email,
            "user": session.get("name"),
            "items": cart_items,
            "grandtotal": grand_total,
            "payment_method": "cod",
            "status": "Pending",
            "shipping_info": shipping_info,
            "shipping_status": "Pending",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        db.orders.insert_one(order)
        db.cart.delete_many({"user_email": user_email})
        flash("Order placed successfully with Cash on Delivery!", "success")
        return redirect(url_for("my_orders"))
    
@app.route("/payment-success", methods=["POST"])
def payment_success():
    data = request.json
    razorpay_order_id = data.get("razorpay_order_id")

    db.orders.update_one(
        {"razorpay_order_id": razorpay_order_id},
        {"$set": {"status": "Completed"}}
    )

    # Clear cart
    db.cart.delete_many({"user_email": session.get("email")})

    flash("Payment successful and order confirmed!", "success")
    return jsonify({"status": "success"})

@app.route("/admin/update_shipping/<order_id>/<status>")
def update_shipping(order_id, status):
    if "user" not in session or session.get("role") != "admin":
        flash("Access denied!", "error")
        return redirect(url_for("home"))

    if status not in ["Pending", "Shipped", "Delivered"]:
        flash("Invalid status", "error")
        return redirect(url_for("admin_dashboard"))

    orders_col.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"shipping_status": status}}
    )

    flash(f"Order marked as {status}", "success")
    return redirect(url_for("admin_dashboard"))


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

    cart_col.delete_many({"user_email": session["email"]})
    flash("🗑 Your cart has been emptied.", "success")
    return redirect(url_for("checkout"))



@app.route("/admin/order/<order_id>")
def view_order_details(order_id):
    if "user" not in session or session.get("role") != "admin":
        flash("Access denied!", "error")
        return redirect(url_for("home"))

    order = orders_col.find_one({"_id": ObjectId(order_id)})
    if not order:
        flash("Order not found!", "error")
        return redirect(url_for("admin_dashboard"))

    return render_template("order_details.html", order=order)

@app.route("/admin/approve_order/<order_id>")
def approve_order(order_id):
    if "user" not in session or session.get("role") != "admin":
        flash("Access denied!", "error")
        return redirect(url_for("home"))

    result = orders_col.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": "Completed"}}
    )

    if result.modified_count:
        flash("✅ Order approved successfully!", "success")
    else:
        flash("⚠ Order not found or already approved.", "warning")

    return redirect(url_for("admin_dashboard"))

@app.route("/my_orders")
def my_orders():
    if not session.get("user"):
        flash("Please login to view your orders.", "error")
        return redirect(url_for("login"))

    orders = list(db.orders.find({"user_email": session.get("email")}))
    return render_template("user_orders.html", orders=orders)


@app.route("/my-orders/<order_id>")
def user_order_details(order_id):
    if not session.get("user"):
        flash("Please login to view order details.", "error")
        return redirect(url_for("login"))

    order = db.orders.find_one({"_id": ObjectId(order_id), "user_email": session.get("email")})
    if not order:
        flash("Order not found.", "error")
        return redirect(url_for("my_orders"))

    return render_template("user_order_details.html", order=order)


@app.route("/debug_cart")
def debug_cart():
    user_email = session.get("email")
    items = list(db.cart.find({"user_email": user_email}))
    print("DEBUG CART:", items)   # log in terminal
    return {"cart_items": str(items)}


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"].strip()
        user = users_col.find_one({"email": email})

        if not user:
            flash("No account found with that email.", "error")
            return redirect(url_for("forgot_password"))

        # Generate token valid for 30 minutes
        token = s.dumps(email, salt="password-reset")
        reset_link = url_for("reset_password", token=token, _external=True)

        # Send email
        if send_reset_email(email, reset_link):
            flash("✅ Password reset link sent to your email!", "success")
        else:
            flash("❌ Could not send email. Please try again.", "error")

        return redirect(url_for("login"))

    return render_template("forgot_password.html")


# -----------------------------
# RESET PASSWORD
# -----------------------------
@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        email = s.loads(token, salt="password-reset", max_age=1800)  # 30 min
    except:
        flash("The reset link is invalid or expired.", "error")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for("reset_password", token=token))

        hashed_pw = generate_password_hash(password)
        users_col.update_one({"email": email}, {"$set": {"password": hashed_pw}})

        flash("Password reset successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("reset_password.html", token=token)

def send_reset_email(to_email, reset_link):
    """Send password reset email using Flask-Mail"""
    try:
        msg = Message(
            subject="AgriConnect Password Reset",
            sender=os.getenv("MAIL_USERNAME"),
            recipients=[to_email],
        )
        msg.html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; background-color:#f9fff9; padding:20px;">
            <div style="max-width:600px; margin:auto; background:#fff; border-radius:8px; padding:20px; border:1px solid #dfe6e9;">
              <h2 style="color:#27ae60;">🌱 AgriConnect Password Reset</h2>
              <p>Hello,</p>
              <p>We received a request to reset your password.</p>
              <p>
                <a href="{reset_link}" style="background:#27ae60; color:white; padding:10px 15px; text-decoration:none; border-radius:5px;">Reset Password</a>
              </p>
              <p>This link will expire in 30 minutes.</p>
              <hr>
              <p>If you didn’t request this, please ignore this email.</p>
              <p style="color:#95a5a6;">– AgriConnect Team</p>
            </div>
          </body>
        </html>
        """
        mail.send(msg)
        print(f"✅ Email sent to {to_email}")
        return True
    except Exception as e:
        print("❌ Failed to send email:", e)
        return False

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
