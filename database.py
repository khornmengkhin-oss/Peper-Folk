"""SQLite setup. All prices are stored in whole cents to avoid rounding errors."""
import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.environ.get("RESTAURANT_DB", Path(__file__).with_name("restaurant.db")))
MENU = [
    (1, "Golden Chicken Bowl", "Grilled chicken, fragrant rice, cucumber and sesame.", "Bowls", 650, "bowl.svg"),
    (2, "Khmer Coconut Curry", "Creamy coconut curry, chicken, vegetables and jasmine rice.", "Bowls", 750, "curry.svg"),
    (3, "Garden Fresh Salad", "Crisp greens, tomato, cucumber and citrus dressing.", "Sides", 450, "salad.svg"),
    (4, "Signature Beef Burger", "Juicy beef patty, melted cheese and house sauce.", "Mains", 850, "burger.svg"),
    (5, "Garlic Grilled Chicken", "Herb-marinated chicken with roasted vegetables.", "Mains", 795, "chicken.svg"),
    (6, "Mango Iced Tea", "Fresh mango, brewed tea and a splash of lime.", "Drinks", 325, "tea.svg"),
    (7, "Crispy Spring Rolls", "Golden vegetable rolls with sweet chili dip.", "Sides", 395, "rolls.svg"),
    (8, "Coconut Cooler", "Chilled coconut water with lime and mint.", "Drinks", 350, "coconut.svg"),
    (9, "Beef Lok Lak Bowl", "Tender pepper beef, jasmine rice, egg and fresh cucumber.", "Bowls", 725, "lok-lak.svg"),
    (10, "Traditional Fish Amok", "Steamed fish in fragrant coconut curry with banana leaf.", "Mains", 795, "fish-amok.svg"),
    (11, "Garlic Stir-Fried Noodles", "Wok-tossed noodles, colorful vegetables and savory garlic sauce.", "Mains", 625, "noodles.svg"),
    (12, "Crispy Potato Wedges", "Golden seasoned potato wedges served with house dipping sauce.", "Sides", 375, "wedges.svg"),
    (13, "Khmer Iced Coffee", "Bold Cambodian coffee with creamy condensed milk and ice.", "Drinks", 325, "iced-coffee.svg"),
    (14, "Passion Fruit Cooler", "Tangy passion fruit, fresh lime and sparkling soda.", "Drinks", 375, "passion-fruit.svg"),
    (15, "Strawberry Smoothie", "Sweet strawberries blended into a refreshing chilled smoothie.", "Drinks", 425, "strawberry.svg"),
]


def connect():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize():
    with connect() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS menu (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                price_cents INTEGER NOT NULL,
                image TEXT NOT NULL,
                available INTEGER NOT NULL DEFAULT 1 CHECK (available IN (0,1))
            );
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reference TEXT NOT NULL UNIQUE,
                customer_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                pickup_time TEXT NOT NULL,
                notes TEXT NOT NULL,
                created_at TEXT NOT NULL,
                completed_at TEXT,
                status TEXT NOT NULL,
                total_cents INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL REFERENCES orders(id),
                menu_id INTEGER NOT NULL REFERENCES menu(id),
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                unit_price_cents INTEGER NOT NULL
            );
        """)
        db.executemany("""INSERT OR IGNORE INTO menu
            (id, name, description, category, price_cents, image) VALUES (?, ?, ?, ?, ?, ?)""", MENU)
