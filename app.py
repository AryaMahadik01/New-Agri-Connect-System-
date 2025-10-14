from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
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
from flask import Flask, render_template, request
from bson.regex import Regex
import requests
from flask import jsonify, request
import json
import re

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

# @app.route("/")
# def home():
#     return render_template("index.html")

@app.route("/profile")
def profile():
    if not session.get("user"):
        flash("Please log in to view your profile.", "warning")
        return redirect(url_for("login"))

    user = users_col.find_one({"email": session["email"]})
    return render_template("profile.html", user=user)

UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/update_profile", methods=["POST"])
def update_profile():
    if not session.get("user"):
        flash("Please login to update your profile.", "error")
        return redirect(url_for("login"))

    user_email = session["email"]
    name = request.form.get("name")
    phone = request.form.get("phone")
    address = request.form.get("address")

    update_data = {"name": name, "phone": phone, "address": address}

    # ✅ Handle profile image upload
    if "profile_pic" in request.files:
        file = request.files["profile_pic"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            update_data["profile_pic"] = f"uploads/{filename}"

    users_col.update_one({"email": user_email}, {"$set": update_data})
    session["name"] = name  # update session instantly

    flash("Profile updated successfully!", "success")
    return redirect(url_for("profile"))

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

@app.route("/products")
def products():
    query = request.args.get("q", "").strip()
    items = list(products_col.find(
        {"name": {"$regex": query, "$options": "i"}} if query else {}
    ))
    return render_template("products.html", products=items, query=query)

@app.route("/search_suggestions")
def search_suggestions():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    suggestions = list(products_col.find(
        {"name": {"$regex": q, "$options": "i"}},
        {"name": 1, "_id": 0}
    ).limit(8))
    return jsonify(suggestions)

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
    query = request.args.get("q", "").strip()
    items = list(products_col.find(
        {"category": "seeds", "name": {"$regex": query, "$options": "i"}} if query else {"category": "seeds"}
    ))
    return render_template("seeds.html", products=items, query=query)

@app.route("/tools")
def tools():
    query = request.args.get("q", "").strip()
    items = list(products_col.find(
        {"category": "tools", "name": {"$regex": query, "$options": "i"}} if query else {"category": "tools"}
    ))
    return render_template("tools.html", products=items, query=query)

@app.route("/pesticides")
def pesticides():
    query = request.args.get("q", "").strip()
    items = list(products_col.find(
        {"category": "pesticides", "name": {"$regex": query, "$options": "i"}} if query else {"category": "pesticides"}
    ))
    return render_template("pesticides.html", products=items, query=query)

@app.route("/fertilizers")
def fertilizers():
    query = request.args.get("q", "").strip()
    items = list(products_col.find(
        {"category": "fertilizers", "name": {"$regex": query, "$options": "i"}} if query else {"category": "fertilizers"}
    ))
    return render_template("fertilizers.html", products=items, query=query)

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
        # After you have created the `order` dict ...
        result = db.orders.insert_one(order)
        order_id = result.inserted_id

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

@app.route("/")
def home():
    offers = list(db.offers.find())  # 🧩 Load offers dynamically from MongoDB
    return render_template("index.html", offers=offers)

@app.route("/admin/offers")
def admin_offers():
    if "user" not in session or session.get("role") != "admin":
        flash("Access denied!", "error")
        return redirect(url_for("home"))

    offers = list(db.offers.find())
    return render_template("admin_offers.html", offers=offers)


@app.route("/admin/add_offer", methods=["POST"])
def add_offer():
    if "user" not in session or session.get("role") != "admin":
        flash("Access denied!", "error")
        return redirect(url_for("home"))

    name = request.form["name"]
    description = request.form["description"]
    old_price = int(request.form["old_price"])
    new_price = int(request.form["new_price"])
    image = request.form["image"]

    db.offers.insert_one({
        "name": name,
        "description": description,
        "old_price": old_price,
        "new_price": new_price,
        "image": image,
        "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    flash("✅ Offer added successfully!", "success")
    return redirect(url_for("admin_offers"))


@app.route("/admin/delete_offer/<offer_id>")
def delete_offer(offer_id):
    if "user" not in session or session.get("role") != "admin":
        flash("Access denied!", "error")
        return redirect(url_for("home"))

    db.offers.delete_one({"_id": ObjectId(offer_id)})
    flash("🗑️ Offer deleted successfully!", "success")
    return redirect(url_for("admin_offers"))

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        subject = request.form["subject"]
        message = request.form["message"]

        # ✅ Send email
        msg = Message(
            subject=f"📩 New Contact from {name} - {subject}",
            sender=app.config["MAIL_USERNAME"],
            recipients=[app.config["MAIL_USERNAME"]],
        )
        msg.body = f"From: {name} <{email}>\n\n{message}"
        mail.send(msg)

        flash("✅ Your message has been sent successfully!", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html")

@app.route("/tutorials")
def tutorials():
    tutorials_data = [
        {
            "title": "Organic Farming Basics",
            "video_id": "lRyXlvIJFWI",  # Replace with real YouTube video ID
            "category": "Organic Farming"
        },
        {
            "title": "Soil Testing Guide",
            "video_id": "L6EtmGMJflI",
            "category": "Soil Health"
        },
        {
            "title": "Efficient Drip Irrigation Setup",
            "video_id": "HEyFQo9RUWQ",
            "category": "Irrigation"
        },
        {
            "title": "Fully Automated Greenhouse Farm",
            "video_id": "OOb7q7YcxiI",
            "category": "Farming"
        },
        {
            "title": "Vegetable Gardening at Home",
            "video_id": "5-59g0K2x6Y",
            "category": "Farming"
        },
        {
            "title": "How to Prepare Soil for Farming",
            "video_id": "yN76_3-bj6s",
            "category": "Soil Health"
        },
    ]
    return render_template("tutorials.html", tutorials=tutorials_data)

# chatbot route 
@app.route("/chatbot", methods=["POST"])
def chatbot():
    user_message = request.json.get("message", "").lower().strip()
    
    try:
        # Get data from database for intelligent responses
        products = list(products_col.find({}, {"name": 1, "category": 1, "price": 1}))
        crops = list(crops_col.find({}, {"name": 1, "season": 1, "location": 1, "description": 1}))
        schemes = list(schemes_col.find({}, {"name": 1, "description": 1}))
        
        # Enhanced rule-based responses with data awareness
        response = generate_chatbot_response(user_message, products, crops, schemes)
        
    except Exception as e:
        print(f"Chatbot error: {e}")
        response = "I'm having trouble accessing our database right now. Please try again later."
    
    return jsonify({"response": response})

def generate_chatbot_response(user_message, products, crops, schemes):
    print(f"User asked: {user_message}")  # Debug log
    
    # Product-related queries
    if any(word in user_message for word in ["product", "buy", "shop", "price", "cost", "seed", "fertilizer", "tool", "pesticide"]):
        return handle_product_query(user_message, products)
    
    # Crop-related queries
    elif any(word in user_message for word in ["crop", "grow", "cultivate", "season", "harvest", "wheat", "rice", "maize"]):
        return handle_crop_query(user_message, crops)
    
    # Scheme-related queries
    elif any(word in user_message for word in ["scheme", "subsidy", "government", "yojana", "loan", "credit"]):
        return handle_scheme_query(user_message, schemes)
    
    # Order-related queries
    elif any(word in user_message for word in ["order", "track", "delivery", "shipping", "return", "refund"]):
        return handle_order_query(user_message)
    
    # General farming advice
    elif any(word in user_message for word in ["fertilizer", "pesticide", "soil", "irrigation", "farming", "advice", "help"]):
        return handle_farming_advice(user_message)
    
    # Greetings and general
    else:
        return handle_general_query(user_message)

def handle_product_query(user_message, products):
    print(f"Products found: {len(products)}")  # Debug log
    
    # Extract categories from products
    seed_products = [p for p in products if p.get("category") == "seeds"]
    fertilizer_products = [p for p in products if p.get("category") == "fertilizers"]
    tool_products = [p for p in products if p.get("category") == "tools"]
    pesticide_products = [p for p in products if p.get("category") == "pesticides"]
    
    # Specific product category queries
    if "seed" in user_message:
        if seed_products:
            sample_seeds = seed_products[:3]
            seed_names = [s["name"] for s in sample_seeds]
            seed_list = ", ".join(seed_names)
            return f"🌱 We have {len(seed_products)} seed varieties! Including: {seed_list}. Check our Seeds section for more options!"
        else:
            return "🌱 We have various seeds available! Visit our Products page to browse all seed varieties."
    
    elif "fertilizer" in user_message:
        if fertilizer_products:
            sample_fert = fertilizer_products[:2]
            fert_names = [f["name"] for f in sample_fert]
            fert_list = ", ".join(fert_names)
            return f"🧪 We offer {len(fertilizer_products)} fertilizers! Such as: {fert_list}. Browse our Fertilizers category!"
        else:
            return "🧪 Check our Fertilizers section for various nutrient solutions for your crops!"
    
    elif "tool" in user_message:
        if tool_products:
            sample_tools = tool_products[:3]
            tool_names = [t["name"] for t in sample_tools]
            tool_list = ", ".join(tool_names)
            return f"🛠️ We have {len(tool_products)} farming tools! Like: {tool_list}. Visit Tools section!"
        else:
            return "🛠️ We offer various farming tools and equipment. Check our Tools category!"
    
    elif "pesticide" in user_message:
        if pesticide_products:
            sample_pest = pesticide_products[:2]
            pest_names = [p["name"] for p in sample_pest]
            pest_list = ", ".join(pest_names)
            return f"🐛 We provide {len(pesticide_products)} pesticides! Including: {pest_list}. Check Pesticides category!"
        else:
            return "🐛 We have various pest control solutions. Browse our Pesticides section!"
    
    # Price-related queries
    elif any(word in user_message for word in ["cheap", "affordable", "budget", "low price"]):
        affordable_products = [p for p in products if p.get("price", 1000) < 500][:3]
        if affordable_products:
            affordable_list = ", ".join([f"{p['name']} (₹{p['price']})" for p in affordable_products])
            return f"💰 Budget-friendly options: {affordable_list}. Use our search to filter by price!"
        else:
            return "💰 We have products across different price ranges. Use the search bar to find options within your budget!"
    
    # General product query
    else:
        total_products = len(products)
        return f"🛍️ We have {total_products} products across seeds, fertilizers, tools, and pesticides! Use our search bar or browse by category to find what you need."

def handle_crop_query(user_message, crops):
    print(f"Crops found: {len(crops)}")  # Debug log
    
    # Season-based recommendations
    if "rabi" in user_message:
        rabi_crops = [c for c in crops if c.get("season", "").lower() == "rabi"]
        if rabi_crops:
            crop_list = ", ".join([c["name"] for c in rabi_crops[:5]])
            return f"❄️ Rabi season crops (winter): {crop_list}. These grow in cool, dry conditions from October to March."
        else:
            return "❄️ Rabi crops are winter crops like wheat, barley, and mustard. They grow in cool, dry conditions."
    
    elif "kharif" in user_message:
        kharif_crops = [c for c in crops if c.get("season", "").lower() == "kharif"]
        if kharif_crops:
            crop_list = ", ".join([c["name"] for c in kharif_crops[:5]])
            return f"🌧️ Kharif season crops (monsoon): {crop_list}. These need warm, humid conditions from June to September."
        else:
            return "🌧️ Kharif crops are monsoon crops like rice, maize, and cotton. They need warm, humid conditions."
    
    # Specific crop queries
    for crop in crops:
        crop_name_lower = crop["name"].lower()
        if crop_name_lower in user_message:
            location = crop.get('location', 'various regions')
            season = crop.get('season', 'specific season')
            description = crop.get('description', 'Check our crop details page for more information!')
            return f"🌾 **{crop['name']}**\n📍 Grown in: {location}\n📅 Season: {season}\n📝 {description}"
    
    # General crop advice
    if crops:
        sample_crops = ", ".join([c["name"] for c in crops[:4]])
        return f"🌱 We have information on {len(crops)} crops! Including: {sample_crops}. Visit 'Crop Details' page for complete growing guides!"
    else:
        return "🌱 Check our 'Crop Details' section for information on various crops and their growing conditions!"

def handle_scheme_query(user_message, schemes):
    print(f"Schemes found: {len(schemes)}")  # Debug log
    
    # Specific scheme mentions
    for scheme in schemes:
        scheme_name_lower = scheme["name"].lower()
        # Check if any significant word from scheme name is in user message
        scheme_words = scheme_name_lower.split()
        if any(word in user_message for word in scheme_words if len(word) > 4):
            return f"🏛️ **{scheme['name']}**\n📋 {scheme['description']}\n🔗 Visit our Government Schemes page for application details and eligibility!"
    
    # Loan/Credit queries
    if any(word in user_message for word in ["loan", "credit", "kisan card"]):
        credit_schemes = [s for s in schemes if any(word in s["name"].lower() for word in ["credit", "kisan", "samman"])]
        if credit_schemes:
            scheme_list = ", ".join([s["name"] for s in credit_schemes])
            return f"💳 Financial support schemes: {scheme_list}. These provide credit and income support to farmers. Check Government Schemes page for details!"
    
    # Insurance queries
    if "insurance" in user_message or "fasal bima" in user_message:
        insurance_schemes = [s for s in schemes if "bima" in s["name"].lower() or "insurance" in s["name"].lower()]
        if insurance_schemes:
            scheme_info = "\n".join([f"• {s['name']}: {s['description']}" for s in insurance_schemes])
            return f"🛡️ Crop insurance schemes:\n{scheme_info}"
    
    # General scheme information
    if schemes:
        sample_schemes = ", ".join([s["name"] for s in schemes[:3]])
        return f"📜 We list {len(schemes)} government schemes! Including: {sample_schemes}. Check 'Government Schemes' page for complete list with eligibility criteria!"
    else:
        return "📜 Visit our Government Schemes page for information on various farmer support programs and subsidies!"

def handle_order_query(user_message):
    if "track" in user_message:
        return "📦 To track your order, go to 'My Orders' section in your profile. You'll see current status and shipping updates there!"
    elif "delivery" in user_message or "shipping" in user_message:
        return "🚚 Delivery usually takes 3-7 days depending on your location. Shipping status updates are available in 'My Orders'. Contact support for urgent queries!"
    elif "return" in user_message or "refund" in user_message:
        return "🔄 For returns/refunds, please contact our support team with your order details at support@agriconnect.in or call +91 98765 43210"
    elif "status" in user_message:
        return "📋 You can check your order status in 'My Orders' section. Need help with a specific order? Contact our support team!"
    else:
        return "📦 For order-related queries, visit 'My Orders' section or contact our support team. We're here to help!"

def handle_farming_advice(user_message):
    if "fertilizer" in user_message:
        return "🧪 Choose fertilizers based on your soil type and crop needs. We offer organic and chemical options. Consider soil testing for best results! Check our Fertilizers section."
    elif "pesticide" in user_message:
        return "🐛 Select pesticides based on the specific pest and crop. Always follow usage instructions. We have various options in Pesticides category. Consult an agricultural expert for severe infestations."
    elif "soil" in user_message:
        return "🌱 Soil health is crucial! Consider getting a Soil Health Card from government schemes. We offer soil testing kits and appropriate fertilizers in our store."
    elif "irrigation" in user_message or "water" in user_message:
        return "💧 Efficient irrigation saves water and improves yield. We offer drip irrigation systems and water pumps in Tools section. Consider rainwater harvesting for sustainable farming!"
    elif "organic" in user_message:
        return "🌿 Organic farming improves soil health and produces chemical-free crops. We offer organic manure and natural pest control solutions. Check our Knowledge Hub for organic farming guides!"
    else:
        return "🌾 For detailed farming advice, visit our Knowledge Hub with articles on organic farming, irrigation, pest control, and sustainable practices!"

def handle_general_query(user_message):
    # Greetings
    if any(word in user_message for word in ["hi", "hello", "hey", "hola", "namaste"]):
        return "Hello! 👋 I'm AgriBot, your farming assistant. I can help with:\n• Product recommendations\n• Crop growing advice\n• Government schemes\n• Order tracking\n• Farming tips\nHow can I assist you today?"
    
    elif any(word in user_message for word in ["bye", "exit", "quit", "goodbye"]):
        return "Goodbye! 👋 Happy farming! Visit again if you need help with your agricultural needs."
    
    elif any(word in user_message for word in ["thank", "thanks"]):
        return "You're welcome! 😊 Is there anything else I can help you with today?"
    
    elif any(word in user_message for word in ["what can you do", "help", "features"]):
        return "I can help you with:\n🛍️ Product information and recommendations\n🌾 Crop growing advice and seasons\n🏛️ Government scheme details\n📦 Order tracking and support\n🌱 Farming tips and best practices\nWhat would you like to know?"
    
    # Default response
    return "I'm here to help with farming products, crop advice, government schemes, and orders! You can ask me about:\n• Available seeds/fertilizers/tools\n• Crop growing seasons\n• Government subsidies\n• Order status\n• Farming best practices"
# Add this route to test if data is loading correctly
@app.route("/chatbot-debug")
def chatbot_debug():
    products = list(products_col.find({}, {"name": 1, "category": 1, "price": 1}))
    crops = list(crops_col.find({}, {"name": 1, "season": 1, "location": 1}))
    schemes = list(schemes_col.find({}, {"name": 1, "description": 1}))
    
    return jsonify({
        "products_count": len(products),
        "crops_count": len(crops), 
        "schemes_count": len(schemes),
        "sample_products": products[:2],
        "sample_crops": crops[:2],
        "sample_schemes": schemes[:2]
    })

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
