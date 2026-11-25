# Preview only: shows the pages with fake data (no database).
# Put this file next to the templates and static folders and run: python preview_app.py
from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)
app.secret_key = "preview"

categories_list = [
    {"id": 1, "name": "Mat"},
    {"id": 2, "name": "Transport"},
    {"id": 3, "name": "Klær"},
]

transactions_list = [
    {"id": 1, "description": "Lunch", "category": "Mat", "date": "2026-11-22", "type": "expense", "amount": 89},
    {"id": 2, "description": "Bus pass", "category": "Transport", "date": "2026-11-20", "type": "expense", "amount": 380},
    {"id": 3, "description": "Salary", "category": "Lønn", "date": "2026-11-15", "type": "income", "amount": 12000},
    {"id": 4, "description": "Jacket", "category": "Klær", "date": "2026-11-12", "type": "expense", "amount": 900},
]

budget_limit = 2000


@app.route("/")
def dashboard():
    income = 0
    expenses = 0
    totals = {}

    for t in transactions_list:
        if t["type"] == "income":
            income = income + t["amount"]
        else:
            expenses = expenses + t["amount"]
            totals[t["category"]] = totals.get(t["category"], 0) + t["amount"]

    categories = []
    for name in totals:
        percent = round(totals[name] / expenses * 100)
        categories.append({"name": name, "total": totals[name], "percent": percent})

    percent_used = round(expenses / budget_limit * 100)

    return render_template("dashboard.html", income=income, expenses=expenses,
                           balance=income - expenses, budget_limit=budget_limit,
                           percent_used=percent_used, categories=categories,
                           recent=transactions_list)


@app.route("/transactions")
def transactions():
    return render_template("transactions.html", transactions=transactions_list)


@app.route("/add", methods=["GET", "POST"])
def add():
    return render_template("add.html", cats=categories_list, today="2026-11-24")


@app.route("/budget", methods=["GET", "POST"])
def budget():
    return render_template("budget.html", budget_limit=budget_limit)


@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    return redirect(url_for("transactions"))


if __name__ == "__main__":
    app.run(debug=True)
