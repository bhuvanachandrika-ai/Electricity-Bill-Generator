from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_file
)

from werkzeug.security import check_password_hash

import sqlite3
import csv
import os
from datetime import datetime

from database import get_connection, initialize_database


app = Flask(__name__)

# Secret key for sessions
app.secret_key = "electricity-bill-generator-secret-key"


# ---------------------------------------------------
# INITIALIZE DATABASE
# ---------------------------------------------------

initialize_database()


# ---------------------------------------------------
# LOGIN REQUIRED DECORATOR
# ---------------------------------------------------

def login_required():

    return "user" in session


# ---------------------------------------------------
# BILL CALCULATION
# ---------------------------------------------------

def calculate_bill(units):

    units = float(units)

    amount = 0

    # First 100 units
    if units <= 100:

        amount = units * 1.50

    # 101 - 200
    elif units <= 200:

        amount = (100 * 1.50) + ((units - 100) * 2.50)

    # 201 - 400
    elif units <= 400:

        amount = (
            (100 * 1.50)
            + (100 * 2.50)
            + ((units - 200) * 4.00)
        )

    # Above 400
    else:

        amount = (
            (100 * 1.50)
            + (100 * 2.50)
            + (200 * 4.00)
            + ((units - 400) * 6.00)
        )

    return round(amount, 2)


# ---------------------------------------------------
# LOGIN
# ---------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def login():

    if "user" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        connection = get_connection()

        user = connection.execute(
            """
            SELECT * FROM users
            WHERE username = ?
            """,
            (username,)
        ).fetchone()

        connection.close()

        if user and check_password_hash(user["password"], password):

            session["user"] = user["username"]

            flash("Login successful!", "success")

            return redirect(url_for("dashboard"))

        else:

            flash(
                "Invalid username or password.",
                "danger"
            )

    return render_template("login.html")


# ---------------------------------------------------
# LOGOUT
# ---------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(url_for("login"))


# ---------------------------------------------------
# DASHBOARD
# ---------------------------------------------------

@app.route("/dashboard")
def dashboard():

    if not login_required():
        return redirect(url_for("login"))

    connection = get_connection()

    customer_count = connection.execute(
        "SELECT COUNT(*) AS count FROM customers"
    ).fetchone()["count"]

    bill_count = connection.execute(
        "SELECT COUNT(*) AS count FROM bills"
    ).fetchone()["count"]

    total_amount = connection.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM bills"
    ).fetchone()["total"]

    recent_bills = connection.execute(
        """
        SELECT *
        FROM bills
        ORDER BY id DESC
        LIMIT 5
        """
    ).fetchall()

    connection.close()

    return render_template(
        "index.html",
        customer_count=customer_count,
        bill_count=bill_count,
        total_amount=total_amount,
        recent_bills=recent_bills
    )


# ---------------------------------------------------
# CUSTOMER MANAGEMENT
# ---------------------------------------------------

@app.route("/customers", methods=["GET", "POST"])
def customers():

    if not login_required():
        return redirect(url_for("login"))

    connection = get_connection()

    if request.method == "POST":

        consumer_no = request.form["consumer_no"].strip()
        name = request.form["name"].strip()
        phone = request.form["phone"].strip()
        address = request.form["address"].strip()

        # Check duplicate consumer
        existing = connection.execute(
            """
            SELECT * FROM customers
            WHERE consumer_no = ?
            """,
            (consumer_no,)
        ).fetchone()

        if existing:

            flash(
                "Consumer number already exists!",
                "danger"
            )

        else:

            connection.execute(
                """
                INSERT INTO customers
                (
                    consumer_no,
                    name,
                    phone,
                    address
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    consumer_no,
                    name,
                    phone,
                    address
                )
            )

            connection.commit()

            flash(
                "Customer added successfully!",
                "success"
            )

    customer_list = connection.execute(
        """
        SELECT *
        FROM customers
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "customers.html",
        customers=customer_list
    )


# ---------------------------------------------------
# GENERATE BILL
# ---------------------------------------------------

@app.route("/generate-bill", methods=["GET", "POST"])
def generate_bill():

    if not login_required():
        return redirect(url_for("login"))

    connection = get_connection()

    customers_list = connection.execute(
        """
        SELECT *
        FROM customers
        ORDER BY name
        """
    ).fetchall()

    connection.close()

    if request.method == "POST":

        consumer_no = request.form["consumer_no"]
        bill_month = request.form["bill_month"]

        previous_reading = float(
            request.form["previous_reading"]
        )

        current_reading = float(
            request.form["current_reading"]
        )

        # Validate reading
        if current_reading < previous_reading:

            flash(
                "Current reading cannot be less than previous reading.",
                "danger"
            )

            return redirect(
                url_for("generate_bill")
            )

        units = current_reading - previous_reading

        amount = calculate_bill(units)

        # Check duplicate bill
        connection = get_connection()

        existing_bill = connection.execute(
            """
            SELECT *
            FROM bills
            WHERE consumer_no = ?
            AND bill_month = ?
            """,
            (
                consumer_no,
                bill_month
            )
        ).fetchone()

        connection.close()

        if existing_bill:

            flash(
                "Bill already exists for this consumer and month.",
                "danger"
            )

            return redirect(
                url_for("generate_bill")
            )

        # Send information to confirmation page
        return render_template(
            "confirm_bill.html",
            consumer_no=consumer_no,
            bill_month=bill_month,
            previous_reading=previous_reading,
            current_reading=current_reading,
            units=units,
            amount=amount
        )

    return render_template(
        "generate_bill.html",
        customers=customers_list
    )


# ---------------------------------------------------
# CONFIRM BILL
# ---------------------------------------------------

@app.route("/confirm-bill", methods=["POST"])
def confirm_bill():

    if not login_required():
        return redirect(url_for("login"))

    consumer_no = request.form["consumer_no"]
    bill_month = request.form["bill_month"]

    previous_reading = float(
        request.form["previous_reading"]
    )

    current_reading = float(
        request.form["current_reading"]
    )

    units = current_reading - previous_reading

    amount = calculate_bill(units)

    generated_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    connection = get_connection()

    try:

        connection.execute(
            """
            INSERT INTO bills
            (
                consumer_no,
                bill_month,
                previous_reading,
                current_reading,
                units,
                amount,
                generated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                consumer_no,
                bill_month,
                previous_reading,
                current_reading,
                units,
                amount,
                generated_at
            )
        )

        connection.commit()

        bill_id = connection.execute(
            "SELECT last_insert_rowid()"
        ).fetchone()[0]

        connection.close()

        return redirect(
            url_for(
                "view_bill",
                bill_id=bill_id
            )
        )

    except sqlite3.IntegrityError:

        connection.close()

        flash(
            "Bill already exists for this consumer and month.",
            "danger"
        )

        return redirect(
            url_for("generate_bill")
        )


# ---------------------------------------------------
# VIEW BILL
# ---------------------------------------------------

@app.route("/bill/<int:bill_id>")
def view_bill(bill_id):

    if not login_required():
        return redirect(url_for("login"))

    connection = get_connection()

    bill = connection.execute(
        """
        SELECT
            bills.*,
            customers.name,
            customers.phone,
            customers.address
        FROM bills
        JOIN customers
        ON bills.consumer_no = customers.consumer_no
        WHERE bills.id = ?
        """,
        (bill_id,)
    ).fetchone()

    connection.close()

    if bill is None:

        flash(
            "Bill not found.",
            "danger"
        )

        return redirect(
            url_for("bill_history")
        )

    return render_template(
        "bill.html",
        bill=bill
    )


# ---------------------------------------------------
# BILL HISTORY
# ---------------------------------------------------

@app.route("/history")
def bill_history():

    if not login_required():
        return redirect(url_for("login"))

    connection = get_connection()

    bills = connection.execute(
        """
        SELECT
            bills.*,
            customers.name
        FROM bills
        JOIN customers
        ON bills.consumer_no = customers.consumer_no
        ORDER BY bills.id DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "history.html",
        bills=bills
    )


# ---------------------------------------------------
# MONTHLY CSV REPORT
# ---------------------------------------------------

@app.route("/export/<month>")
def export_month(month):

    if not login_required():
        return redirect(url_for("login"))

    connection = get_connection()

    bills = connection.execute(
        """
        SELECT
            bills.*,
            customers.name
        FROM bills
        JOIN customers
        ON bills.consumer_no = customers.consumer_no
        WHERE bills.bill_month = ?
        ORDER BY bills.id
        """,
        (month,)
    ).fetchall()

    connection.close()

    if not bills:

        flash(
            "No bills found for this month.",
            "danger"
        )

        return redirect(
            url_for("bill_history")
        )

    base_dir = os.path.dirname(os.path.abspath(__file__))
    report_folder = os.path.join(base_dir, "data", "monthly_reports")

    os.makedirs(
        report_folder,
        exist_ok=True
    )

    file_path = os.path.join(
        report_folder,
        f"electricity_bills_{month}.csv"
    )

    with open(
        file_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Bill ID",
            "Consumer Number",
            "Customer Name",
            "Bill Month",
            "Previous Reading",
            "Current Reading",
            "Units",
            "Amount",
            "Generated At"
        ])

        for bill in bills:

            writer.writerow([
                bill["id"],
                bill["consumer_no"],
                bill["name"],
                bill["bill_month"],
                bill["previous_reading"],
                bill["current_reading"],
                bill["units"],
                bill["amount"],
                bill["generated_at"]
            ])

    return send_file(
        file_path,
        as_attachment=True
    )


# ---------------------------------------------------
# RUN APPLICATION
# ---------------------------------------------------

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )