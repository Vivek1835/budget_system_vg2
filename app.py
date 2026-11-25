# app.py - the website.
# Each "@app.route" is one page. The function under it runs when someone opens that page.

import os
import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_rows, get_one, run_command

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-in-the-env-file")


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def format_money(number):
    # Turns 12000 into "12 000 kr"
    number = round(float(number))
    text = "{:,}".format(number)
    text = text.replace(",", " ")
    return text + " kr"


def add_money_text(rows):
    # Gives every row a text version of its amount, for example "89 kr"
    for row in rows:
        row["amount_text"] = format_money(row["amount"])
    return rows


def get_categories():
    return get_rows("SELECT id, name FROM categories ORDER BY name")


def get_transactions(user_id, how_many):
    # The newest transactions of this user
    rows = get_rows(
        """SELECT transactions.id, transactions.date, transactions.type,
                  transactions.amount, transactions.description,
                  categories.name AS category
           FROM transactions
           JOIN categories ON categories.id = transactions.category_id
           WHERE transactions.user_id = %s
           ORDER BY transactions.date DESC, transactions.id DESC
           LIMIT %s""",
        (user_id, how_many),
    )
    return add_money_text(rows)


def get_month_totals(user_id):
    # Adds up the income and the expenses for this month
    rows = get_rows(
        """SELECT type, SUM(amount) AS total
           FROM transactions
           WHERE user_id = %s
             AND YEAR(date) = YEAR(CURDATE())
             AND MONTH(date) = MONTH(CURDATE())
           GROUP BY type""",
        (user_id,),
    )
    income = 0
    expenses = 0
    for row in rows:
        if row["type"] == "income":
            income = float(row["total"])
        else:
            expenses = float(row["total"])
    return income, expenses


def get_category_totals(user_id):
    # Expenses per category this month.
    # "percent" is the width of the bar. The biggest category gets 100.
    rows = get_rows(
        """SELECT categories.name AS name, SUM(transactions.amount) AS total
           FROM transactions
           JOIN categories ON categories.id = transactions.category_id
           WHERE transactions.user_id = %s
             AND transactions.type = 'expense'
             AND YEAR(transactions.date) = YEAR(CURDATE())
             AND MONTH(transactions.date) = MONTH(CURDATE())
           GROUP BY categories.name
           ORDER BY total DESC""",
        (user_id,),
    )

    biggest = 0
    for row in rows:
        row["total"] = float(row["total"])
        if row["total"] > biggest:
            biggest = row["total"]

    for row in rows:
        row["percent"] = round(row["total"] / biggest * 100)
        row["total_text"] = format_money(row["total"])

    return rows


def get_budget_limit(user_id):
    # Returns the monthly budget of the user, or None if there is no budget yet
    row = get_one("SELECT monthly_limit FROM budgets WHERE user_id = %s", (user_id,))
    if row is None:
        return None
    return float(row["monthly_limit"])


def calculate_percent(expenses, budget_limit):
    # How many percent of the budget is used
    if budget_limit is None:
        return 0
    return round(expenses / budget_limit * 100)


def check_transaction_form(form):
    # Checks the form on the Add and Edit pages.
    # Returns "" if everything is fine. If not, returns a text that says what is wrong.

    try:
        amount = float(form["amount"])
    except ValueError:
        return "Amount must be a number."

    if amount <= 0:
        return "Amount must be more than 0."

    if form["type"] != "income" and form["type"] != "expense":
        return "Pick income or expense."

    category = get_one("SELECT id FROM categories WHERE id = %s", (form["category_id"],))
    if category is None:
        return "Pick a category."

    try:
        datetime.datetime.strptime(form["date"], "%Y-%m-%d")
    except ValueError:
        return "That date is not valid."

    return ""


# =====================================================
# REGISTER, LOG IN, LOG OUT
# =====================================================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        confirm = request.form["confirm"]

        if len(username) < 3 or len(username) > 30:
            flash("Username must be 3 to 30 characters.")
            return redirect("/register")

        # Only letters, numbers and _ are allowed in a username
        if not username.replace("_", "").isalnum():
            flash("Username can only have letters, numbers and _")
            return redirect("/register")

        if len(password) < 8:
            flash("Password must be at least 8 characters.")
            return redirect("/register")

        if password != confirm:
            flash("The two passwords are not the same.")
            return redirect("/register")

        old_user = get_one("SELECT id FROM users WHERE username = %s", (username,))
        if old_user is not None:
            flash("That username is already taken.")
            return redirect("/register")

        # We never save the real password. We save a scrambled version (a hash).
        password_hash = generate_password_hash(password)

        run_command(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, password_hash),
        )
        flash("Account created. You can log in now.")
        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        user = get_one(
            "SELECT id, password_hash FROM users WHERE username = %s",
            (username,),
        )

        if user is not None:
            if check_password_hash(user["password_hash"], password):
                # The password is correct. Remember the user in the session.
                session.clear()
                session["user_id"] = user["id"]
                session["username"] = username
                return redirect("/")

        flash("Wrong username or password.")
        return redirect("/login")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# =====================================================
# THE PAGES (you must be logged in to see them)
# =====================================================

@app.route("/")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    user_id = session["user_id"]

    income, expenses = get_month_totals(user_id)
    budget_limit = get_budget_limit(user_id)
    percent_used = calculate_percent(expenses, budget_limit)

    # The text in the middle of the ring
    if budget_limit is None:
        ring_big = "No budget"
        ring_small = "set yet"
        budget_text = "No budget yet"
    elif expenses > budget_limit:
        ring_big = format_money(expenses - budget_limit)
        ring_small = "over budget"
        budget_text = format_money(budget_limit)
    else:
        ring_big = format_money(budget_limit - expenses)
        ring_small = "left to spend"
        budget_text = format_money(budget_limit)

    # The ring can never be more than 100 percent full
    ring_percent = percent_used
    if ring_percent > 100:
        ring_percent = 100

    # The ring turns orange when the user is over budget
    ring_color = "var(--main)"
    if percent_used >= 100:
        ring_color = "var(--warning-text)"

    # The warning box at the top of the page
    warning_text = ""
    if budget_limit is not None:
        if percent_used >= 100:
            warning_text = "You are over your budget this month."
        elif percent_used >= 80:
            warning_text = "You have used " + str(percent_used) + "% of your budget."

    return render_template(
        "dashboard.html",
        month_name=datetime.date.today().strftime("%B"),
        income_text=format_money(income),
        expenses_text=format_money(expenses),
        balance_text=format_money(income - expenses),
        has_budget=budget_limit is not None,
        budget_text=budget_text,
        percent_used=percent_used,
        ring_big=ring_big,
        ring_small=ring_small,
        ring_percent=ring_percent,
        ring_color=ring_color,
        warning_text=warning_text,
        categories=get_category_totals(user_id),
        recent=get_transactions(user_id, 5),
    )


@app.route("/transactions")
def transactions():
    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "transactions.html",
        transactions=get_transactions(session["user_id"], 200),
    )


@app.route("/add", methods=["GET", "POST"])
def add():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        error = check_transaction_form(request.form)
        if error != "":
            flash(error)
            return redirect("/add")

        description = request.form["description"].strip()[:200]

        run_command(
            """INSERT INTO transactions (user_id, category_id, type, amount, description, date)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (
                session["user_id"],
                request.form["category_id"],
                request.form["type"],
                request.form["amount"],
                description,
                request.form["date"],
            ),
        )
        flash("Transaction saved.")
        return redirect("/")

    return render_template(
        "add.html",
        categories=get_categories(),
        today=datetime.date.today().isoformat(),
    )


@app.route("/edit/<int:transaction_id>", methods=["GET", "POST"])
def edit(transaction_id):
    if "user_id" not in session:
        return redirect("/login")
    user_id = session["user_id"]

    # "AND user_id = ..." means you can only open your own transactions
    transaction = get_one(
        """SELECT id, category_id, type, amount, description, date
           FROM transactions
           WHERE id = %s AND user_id = %s""",
        (transaction_id, user_id),
    )
    if transaction is None:
        flash("That transaction was not found.")
        return redirect("/transactions")

    if request.method == "POST":
        error = check_transaction_form(request.form)
        if error != "":
            flash(error)
            return redirect("/edit/" + str(transaction_id))

        description = request.form["description"].strip()[:200]

        run_command(
            """UPDATE transactions
               SET category_id = %s, type = %s, amount = %s, description = %s, date = %s
               WHERE id = %s AND user_id = %s""",
            (
                request.form["category_id"],
                request.form["type"],
                request.form["amount"],
                description,
                request.form["date"],
                transaction_id,
                user_id,
            ),
        )
        flash("Transaction updated.")
        return redirect("/transactions")

    return render_template(
        "edit.html",
        transaction=transaction,
        categories=get_categories(),
    )


@app.route("/delete/<int:transaction_id>", methods=["POST"])
def delete(transaction_id):
    if "user_id" not in session:
        return redirect("/login")

    # "AND user_id = ..." means you can only delete your own transactions
    run_command(
        "DELETE FROM transactions WHERE id = %s AND user_id = %s",
        (transaction_id, session["user_id"]),
    )
    flash("Transaction deleted.")
    return redirect("/transactions")


@app.route("/budget", methods=["GET", "POST"])
def budget():
    if "user_id" not in session:
        return redirect("/login")
    user_id = session["user_id"]

    if request.method == "POST":
        try:
            limit = float(request.form["limit"])
        except ValueError:
            limit = 0

        if limit <= 0:
            flash("The budget must be more than 0.")
            return redirect("/budget")

        # If the user already has a budget, update it. If not, create it.
        run_command(
            """INSERT INTO budgets (user_id, monthly_limit) VALUES (%s, %s)
               ON DUPLICATE KEY UPDATE monthly_limit = %s""",
            (user_id, limit, limit),
        )
        flash("Budget saved.")
        return redirect("/")

    income, expenses = get_month_totals(user_id)
    budget_limit = get_budget_limit(user_id)

    # The number that is already in the box when the page opens
    limit_value = ""
    if budget_limit is not None:
        limit_value = str(int(budget_limit))

    return render_template(
        "budget.html",
        has_budget=budget_limit is not None,
        limit_value=limit_value,
        expenses_text=format_money(expenses),
        percent_used=calculate_percent(expenses, budget_limit),
    )


# =====================================================
# START THE WEBSITE
# =====================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
