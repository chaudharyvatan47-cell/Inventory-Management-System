from flask import Flask, render_template, request, redirect, url_for, flash
from pathlib import Path
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = "inventory-management-system"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "products.json"


def ensure_data_file():
    DATA_DIR.mkdir(exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")


def read_products():
    ensure_data_file()
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_products(products):
    ensure_data_file()
    DATA_FILE.write_text(
        json.dumps(products, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def find_product(products, product_id):
    return next((p for p in products if p["id"] == product_id), None)


def next_product_id(products):
    numbers = []
    for product in products:
        try:
            numbers.append(int(product["id"]))
        except (ValueError, TypeError):
            pass
    return str(max(numbers, default=0) + 1)


def parse_price(value):
    price = float(value)
    if price < 0:
        raise ValueError
    return round(price, 2)


def parse_quantity(value):
    quantity = int(value)
    if quantity < 0:
        raise ValueError
    return quantity


@app.route("/")
def dashboard():
    products = read_products()
    total_products = len(products)
    total_stock = sum(product["quantity"] for product in products)
    low_stock = [p for p in products if p["quantity"] < 5]

    return render_template(
        "index.html",
        total_products=total_products,
        total_stock=total_stock,
        low_stock_count=len(low_stock),
        low_stock_products=low_stock
    )


@app.route("/products")
def products_page():
    products = read_products()
    search = request.args.get("search", "").strip()

    if search:
        products = [
            p for p in products
            if search.lower() in p["name"].lower()
        ]

    return render_template(
        "products.html",
        products=products,
        search=search
    )


@app.route("/products/add", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        price_value = request.form.get("price", "").strip()
        quantity_value = request.form.get("quantity", "").strip()

        errors = []
        if not name:
            errors.append("Product name is required.")
        if not category:
            errors.append("Category is required.")

        try:
            price = parse_price(price_value)
        except (ValueError, TypeError):
            errors.append("Price must be a valid non-negative number.")
            price = 0

        try:
            quantity = parse_quantity(quantity_value)
        except (ValueError, TypeError):
            errors.append("Quantity must be a valid non-negative whole number.")
            quantity = 0

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("add_product.html")

        products = read_products()
        products.append({
            "id": next_product_id(products),
            "name": name,
            "category": category,
            "price": price,
            "quantity": quantity,
            "created_date": datetime.now().strftime("%Y-%m-%d")
        })
        save_products(products)
        flash("Product added successfully.", "success")
        return redirect(url_for("products_page"))

    return render_template("add_product.html")


@app.route("/products/edit/<product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    products = read_products()
    product = find_product(products, product_id)

    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("products_page"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        price_value = request.form.get("price", "").strip()
        quantity_value = request.form.get("quantity", "").strip()

        errors = []
        if not name:
            errors.append("Product name is required.")
        if not category:
            errors.append("Category is required.")

        try:
            price = parse_price(price_value)
        except (ValueError, TypeError):
            errors.append("Price must be a valid non-negative number.")
            price = product["price"]

        try:
            quantity = parse_quantity(quantity_value)
        except (ValueError, TypeError):
            errors.append("Quantity must be a valid non-negative whole number.")
            quantity = product["quantity"]

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("edit_product.html", product=product)

        product.update({
            "name": name,
            "category": category,
            "price": price,
            "quantity": quantity
        })
        save_products(products)
        flash("Product updated successfully.", "success")
        return redirect(url_for("products_page"))

    return render_template("edit_product.html", product=product)


@app.post("/products/delete/<product_id>")
def delete_product(product_id):
    products = read_products()
    product = find_product(products, product_id)

    if not product:
        flash("Product not found.", "error")
    else:
        products.remove(product)
        save_products(products)
        flash("Product deleted successfully.", "success")

    return redirect(url_for("products_page"))


@app.post("/products/stock/<product_id>/add")
def add_stock(product_id):
    return change_stock(product_id, "add")


@app.post("/products/stock/<product_id>/remove")
def remove_stock(product_id):
    return change_stock(product_id, "remove")


def change_stock(product_id, action):
    products = read_products()
    product = find_product(products, product_id)

    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("products_page"))

    try:
        amount = int(request.form.get("amount", "0"))
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash("Stock amount must be a positive whole number.", "error")
        return redirect(url_for("products_page"))

    if action == "remove":
        if amount > product["quantity"]:
            flash("Stock removal cannot be greater than available quantity.", "error")
            return redirect(url_for("products_page"))
        product["quantity"] -= amount
        flash("Stock removed successfully.", "success")
    else:
        product["quantity"] += amount
        flash("Stock added successfully.", "success")

    save_products(products)
    return redirect(url_for("products_page"))


if __name__ == "__main__":
    ensure_data_file()
    app.run(debug=True)
