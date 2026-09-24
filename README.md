# ⚡ Electricity Bill Generator

A web-based Electricity Bill Generator developed using **Python, Flask, HTML, CSS, JavaScript, and SQLite**.  
The application automates electricity bill calculation using unit-based slabs and provides customer management, bill generation, confirmation, and bill history features.

---

## 📌 Project Overview

The Electricity Bill Generator is designed to simplify the process of calculating and managing electricity bills.

Instead of manually calculating electricity charges, the application automatically calculates the bill based on the number of units consumed and the applicable tariff slabs.

The system also maintains customer records and generated bill history, making the billing process faster, organized, and less prone to manual calculation errors.

---

## 🎯 Objectives

- Automate electricity bill calculation.
- Calculate charges using predefined unit-based slabs.
- Maintain customer information.
- Prevent duplicate consumer records.
- Generate bills through a web interface.
- Store and view previous bills.
- Provide a simple login system.
- Generate monthly bill reports.

---

## ✨ Features

### 👤 Customer Management
- Add new customers.
- Store consumer details.
- Validate duplicate consumer numbers.
- View registered customers.

### 🧮 Automatic Bill Calculation
- Calculate electricity charges based on units consumed.
- Apply slab-wise tariff rates.
- Calculate the total payable amount automatically.
- Reduce manual calculation errors.

### 🧾 Bill Generation
- Enter consumer and meter details.
- Calculate the bill automatically.
- Preview and confirm the bill before generation.
- Generate a structured electricity bill.

### 📚 Bill History
- Store generated bills.
- View previously generated bills.
- Search and review billing records.

### 🔐 Login System
- Simple login interface.
- Restricts access to the billing application.

### 📊 Monthly Reports
- Maintain monthly billing records.
- Generate monthly report files for billing data.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Backend programming |
| Flask | Web application framework |
| SQLite | Database management |
| HTML | Web page structure |
| CSS | User interface styling |
| JavaScript | Client-side interactions |
| Jinja2 | Dynamic HTML templates |

---

## 🏗️ Project Structure

```text
Electricity-Bill-Generator/
│
├── app.py
├── database.py
├── requirements.txt
├── .gitignore
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── index.html
│   ├── customers.html
│   ├── generate_bill.html
│   ├── confirm_bill.html
│   ├── bill.html
│   └── history.html
│
├── static/
│   ├── style.css
│   └── script.js
│
└── data/
    └── monthly_reports/