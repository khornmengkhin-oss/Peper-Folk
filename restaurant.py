"""Restaurant business logic: normal Python functions, conditions, loops and SQLite."""
from datetime import datetime, timezone, timedelta
import secrets

from database import connect

# Cambodia is UTC+7 throughout the year.
LOCAL_TIMEZONE = timezone(timedelta(hours=7))
STATUSES = ["Received", "Preparing", "Ready for pickup", "Completed"]
PICKUP_TIMES = ["As soon as possible", "In 30 minutes", "In 45 minutes", "In 60 minutes"]


def now():
    return datetime.now(LOCAL_TIMEZONE).isoformat(timespec="seconds")


def get_menu():
    with connect() as db:
        return [dict(row) for row in db.execute("SELECT * FROM menu ORDER BY id")]


def get_order(db, reference, staff=False):
    order = db.execute("SELECT * FROM orders WHERE reference = ?", (reference,)).fetchone()
    if order is None:
        return None
    result = dict(order)
    result["items"] = [dict(row) for row in db.execute(
        "SELECT name, quantity, unit_price_cents FROM order_items WHERE order_id = ? ORDER BY id",
        (order["id"],))]
    if not staff:
        for key in ["id", "phone", "notes"]:
            result.pop(key, None)
    return result


def clean_text(data, key, limit, required=True):
    value = data.get(key, "")
    if not isinstance(value, str):
        raise ValueError("Invalid " + key)
    value = value.strip()
    if (required and not value) or len(value) > limit:
        raise ValueError("Please check " + key.replace("_", " ") + ".")
    return value


def place_order(data):
    name = clean_text(data, "customer_name", 70)
    phone = clean_text(data, "phone", 25)
    if not 7 <= sum(c.isdigit() for c in phone) <= 15 or any(c not in "0123456789+ -()" for c in phone):
        raise ValueError("Enter a valid phone number.")
    pickup = clean_text(data, "pickup_time", 50)
    if pickup not in PICKUP_TIMES:
        raise ValueError("Select a pickup time.")
    notes = clean_text(data, "notes", 300, False)
    items = data.get("items")
    if not isinstance(items, list) or not items or len(items) > 30:
        raise ValueError("Add at least one dish to your basket.")

    with connect() as db:
        total = 0
        selected = []
        seen_ids = set()
        for item in items:
            if not isinstance(item, dict):
                raise ValueError("Invalid item.")
            dish_id = item.get("id")
            quantity = item.get("quantity")
            if type(dish_id) is not int or type(quantity) is not int or not 1 <= quantity <= 20:
                raise ValueError("Choose a quantity between 1 and 20.")
            if dish_id in seen_ids:
                raise ValueError("Duplicate dish in basket.")
            seen_ids.add(dish_id)
            dish = db.execute("SELECT * FROM menu WHERE id = ?", (dish_id,)).fetchone()
            if dish is None or not dish["available"]:
                raise ValueError("One of your dishes is now unavailable. Refresh your menu.")
            # Never trust a total or a price supplied by the browser.
            total += dish["price_cents"] * quantity
            selected.append((dish_id, dish["name"], quantity, dish["price_cents"]))

        reference = "MF-" + secrets.token_hex(8).upper()
        cursor = db.execute("""INSERT INTO orders (reference, customer_name, phone, pickup_time,
            notes, created_at, status, total_cents) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (reference, name, phone, pickup, notes, now(), STATUSES[0], total))
        order_id = cursor.lastrowid
        for dish_id, dish_name, quantity, price in selected:
            db.execute("""INSERT INTO order_items (order_id, menu_id, name, quantity, unit_price_cents)
                VALUES (?, ?, ?, ?, ?)""", (order_id, dish_id, dish_name, quantity, price))
        return get_order(db, reference)


def track_order(reference):
    with connect() as db:
        return get_order(db, reference.strip().upper())


def staff_orders():
    with connect() as db:
        refs = db.execute("SELECT reference FROM orders ORDER BY id DESC").fetchall()
        return [get_order(db, row["reference"], True) for row in refs]


def change_status(reference, next_status):
    with connect() as db:
        order = get_order(db, reference)
        if order is None:
            raise ValueError("Order not found.")
        position = STATUSES.index(order["status"])
        if position == len(STATUSES) - 1 or next_status != STATUSES[position + 1]:
            raise ValueError("This order has an invalid status transition.")
        completed = now() if next_status == "Completed" else None
        db.execute("UPDATE orders SET status = ?, completed_at = ? WHERE reference = ?",
                   (next_status, completed, reference))
        return get_order(db, reference, True)


def change_availability(dish_id, available):
    if type(dish_id) is not int or type(available) is not bool:
        raise ValueError("Invalid availability.")
    with connect() as db:
        cursor = db.execute("UPDATE menu SET available = ? WHERE id = ?", (int(available), dish_id))
        if cursor.rowcount == 0:
            raise ValueError("Menu item not found.")


def sales_report(date):
    try:
        if datetime.strptime(date, "%Y-%m-%d").date().isoformat() != date:
            raise ValueError()
    except (TypeError, ValueError):
        raise ValueError("Choose a valid report date.")
    with connect() as db:
        rows = db.execute("""SELECT id, total_cents FROM orders
            WHERE status = 'Completed' AND substr(completed_at, 1, 10) = ?""", (date,)).fetchall()
        total = 0
        quantities = {}
        for row in rows:
            total += row["total_cents"]
            for item in db.execute("SELECT name, quantity FROM order_items WHERE order_id = ?", (row["id"],)):
                name = item["name"]
                quantities[name] = quantities.get(name, 0) + item["quantity"]
        popular = sorted(quantities.items(), key=lambda item: (-item[1], item[0]))
        return {"date": date, "orders": len(rows), "sales_cents": total,
                "items_sold": sum(quantities.values()), "top_dishes": popular[:5]}
