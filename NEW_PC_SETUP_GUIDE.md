# 💻 New PC Setup Guide: PlantCart

Follow these step-by-step instructions to set up the **PlantCart** project on a new computer.

---

## Prerequisites
Before you begin, ensure you have the following installed on your system:
1. **Python 3.11+**: [Download Link](https://www.python.org/downloads/)
2. **Git**: [Download Link](https://git-scm.com/downloads)
3. **MySQL Server (XAMPP/WAMP/MySQL Installer)**: Ensure MySQL is running on port `3306`.

---

## 1. Clone the Repository
Open your terminal (CMD or PowerShell) and run:
```bash
git clone https://github.com/Mehulkoshti/plantcart_marketplace.git
cd plantcart_marketplace
```

---

## 2. Setup Virtual Environment
It is highly recommended to use a virtual environment to keep dependencies isolated.
```bash
# Create the environment
python -m venv venv

# Activate the environment (Windows)
venv\Scripts\activate

# Activate the environment (Mac/Linux)
# source venv/bin/activate
```

---

## 3. Database Setup (MySQL)
The project is configured to use **MySQL**.
1. Open your MySQL client (like phpMyAdmin or MySQL Workbench).
2. Create a new database named: `plant_marketplace_db`.
   ```sql
   CREATE DATABASE plant_marketplace_db;
   ```
3. **Note**: The project currently uses `root` user with **no password** (default for XAMPP). If you have a different MySQL password, update it in `config/settings.py` on line 86.

---

## 4. Install Dependencies
Install all required Python packages:
```bash
pip install -r requirements.txt
```
*Note: If you face errors with `mysqlclient`, ensure you have the "C++ Build Tools" installed or use `mysql-connector-python`.*

---

## 5. Initialize the Database
Run the Django migrations to create the necessary tables:
```bash
python manage.py migrate
```

---

## 6. Create Admin Account
Create a superuser account to access the admin panel and approve vendors:
```bash
python manage.py createsuperuser
```
Follow the prompts to enter your Email, First Name, Last Name, and Password.

---

## 7. Run the Project
Start the development server:
```bash
python manage.py runserver
```

Open your browser and go to: `http://127.0.0.1:8000/`

---

## 8. Initial Configuration (Important)
Once the site is running:
1. Go to `http://127.0.0.1:8000/admin/` and log in.
2. Create some **Categories** and **Subcategories** first.
3. Vendors cannot list products until you approve them in the `Users` section of the admin panel (`is_approved = True`).

---

## Troubleshooting
- **Media Files**: If plant images are not showing, ensure the `media/` folder exists in the root directory.
- **Stripe**: The payment system is in **Test Mode**. Use Stripe's test card numbers for checkout.
