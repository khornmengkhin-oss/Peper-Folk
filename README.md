# Mekong & Fork — Restaurant Ordering & Management System

A local Python course project using **Python, SQLite, HTML, CSS, and JavaScript**. No Flask, Django, Node installation or external packages needed.

## Run on macOS

1. Extract the ZIP and open the `fresh-restaurant` folder in VS Code.
2. Open Terminal > New Terminal.
3. Run:

```bash
python3 server.py
```

4. Visit **http://localhost:8000/** for customers.
5. Visit **http://localhost:8000/staff.html** in another tab for staff. Enter demo PIN **2468**.
6. Keep the terminal running. Press Ctrl+C to stop the server.

On Windows, use `py server.py` if `python3` is not recognized. Python 3.10+ is recommended. The SQLite database is created automatically on the first run.

## 5 features
1. Food ordering: select quantities, enter pickup details, submit. Python looks up prices from the database, verifies availability and calculates the correct total.
2. Kitchen management: on staff page advance each order to Preparing, Ready for pickup, and Completed.
3. Order tracking: copy the order reference and check its status on the customer page. The page refreshes every six seconds.
4. Availability: staff mark a dish sold out; Python rejects any checkout containing unavailable dishes.
5. Daily sales: completed orders, recorded totals and top dishes, grouped by the date the order is completed (Cambodia time).

## Project structure
- `server.py`: built-in HTTP server and API routing (the bridge between Python and the browser).
- `restaurant.py`: functions, conditions, loops, lists, calculations and order validation.
- `database.py`: initializes SQLite and the sample menu of 15 food and drink items.
- `restaurant.db`: generated at first run; persistent local data.
- `web/index.html`: customer page.
- `web/staff.html`: staff dashboard.
- `web/styles.css`: responsive visual design.
- `web/shared.js`, `customer.js`, `staff.js`: frontend requests and displays.
- `web/images/`: original local SVG food illustrations.

## Classroom demonstration
Open both pages. Place an order with two different dishes. Show the total and tracking reference. Open staff, update preparation status and observe customer tracking. Mark a dish sold out and demonstrate checkout rejection. Complete the order, then open Sales report. Restart the server to show database persistence.

## Important limitations
This is a localhost teaching prototype. Do not expose this built-in server publicly. The demo PIN is not a production authentication system; this project does not process online payments. The only dependencies are Python's standard library and a modern browser. If your professor strictly requires a console program, confirm that a web interface is accepted before submitting.

## Updating an earlier copy
If you already have a working copy of Mekong & Fork, stop the server, back up your project, and copy only the updated `database.py` and the seven newly added SVG files into their matching locations in your current folder. Do not delete `restaurant.db`. Restart with `python3 server.py`; the new menu rows (IDs 9–15) will be inserted automatically, while existing orders and availability are preserved.
