from flask import Flask, render_template, request, jsonify, send_file
import csv
import io
import os
from datetime import datetime

app = Flask(__name__)

# Hardcoded stock prices dictionary
STOCK_PRICES = {
    "AAPL": 180,
    "TSLA": 250,
    "GOOGL": 140,
    "AMZN": 185,
    "MSFT": 420,
    "META": 480,
    "NFLX": 620,
    "NVDA": 130,
    "AMD": 165,
    "INTC": 30,
    "ORCL": 125,
    "CRM": 265,
    "PYPL": 68,
    "UBER": 72,
    "SPOT": 290,
}

# In-memory portfolio storage
portfolio = []


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/stocks", methods=["GET"])
def get_stocks():
    """Return all available stocks and their prices."""
    return jsonify(STOCK_PRICES)


@app.route("/api/portfolio", methods=["GET"])
def get_portfolio():
    """Return the current portfolio."""
    total = sum(item["total"] for item in portfolio)
    return jsonify({"portfolio": portfolio, "total_investment": total})


@app.route("/api/portfolio/add", methods=["POST"])
def add_stock():
    """Add a stock to the portfolio."""
    data = request.get_json()
    stock_name = data.get("stock", "").upper().strip()
    quantity = data.get("quantity", 0)

    if not stock_name:
        return jsonify({"error": "Stock name is required."}), 400

    if stock_name not in STOCK_PRICES:
        return jsonify({"error": f"Stock '{stock_name}' not found. Available: {', '.join(STOCK_PRICES.keys())}"}), 404

    try:
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "Quantity must be a positive integer."}), 400

    price = STOCK_PRICES[stock_name]
    total = price * quantity

    # Check if stock already exists in portfolio, update quantity
    for item in portfolio:
        if item["stock"] == stock_name:
            item["quantity"] += quantity
            item["total"] = item["quantity"] * price
            break
    else:
        portfolio.append({
            "stock": stock_name,
            "price": price,
            "quantity": quantity,
            "total": total,
        })

    grand_total = sum(item["total"] for item in portfolio)
    return jsonify({
        "message": f"Added {quantity} shares of {stock_name}",
        "portfolio": portfolio,
        "total_investment": grand_total,
    })


@app.route("/api/portfolio/remove", methods=["POST"])
def remove_stock():
    """Remove a stock from the portfolio."""
    data = request.get_json()
    stock_name = data.get("stock", "").upper().strip()

    global portfolio
    portfolio = [item for item in portfolio if item["stock"] != stock_name]

    grand_total = sum(item["total"] for item in portfolio)
    return jsonify({
        "message": f"Removed {stock_name} from portfolio",
        "portfolio": portfolio,
        "total_investment": grand_total,
    })


@app.route("/api/portfolio/clear", methods=["POST"])
def clear_portfolio():
    """Clear the entire portfolio."""
    global portfolio
    portfolio = []
    return jsonify({"message": "Portfolio cleared", "portfolio": [], "total_investment": 0})


@app.route("/api/portfolio/export/txt", methods=["GET"])
def export_txt():
    """Export portfolio as a .txt file."""
    if not portfolio:
        return jsonify({"error": "Portfolio is empty."}), 400

    lines = []
    lines.append("=" * 55)
    lines.append("        STOCK PORTFOLIO REPORT")
    lines.append(f"        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 55)
    lines.append("")
    lines.append(f"{'Stock':<10} {'Price ($)':<12} {'Qty':<8} {'Total ($)':<12}")
    lines.append("-" * 55)

    for item in portfolio:
        lines.append(f"{item['stock']:<10} {item['price']:<12} {item['quantity']:<8} {item['total']:<12}")

    grand_total = sum(item["total"] for item in portfolio)
    lines.append("-" * 55)
    lines.append(f"{'TOTAL INVESTMENT:':<30} ${grand_total:,.2f}")
    lines.append("=" * 55)

    content = "\n".join(lines)
    buffer = io.BytesIO(content.encode("utf-8"))
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype="text/plain",
        as_attachment=True,
        download_name="portfolio_report.txt",
    )


@app.route("/api/portfolio/export/csv", methods=["GET"])
def export_csv():
    """Export portfolio as a .csv file."""
    if not portfolio:
        return jsonify({"error": "Portfolio is empty."}), 400

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Stock", "Price ($)", "Quantity", "Total ($)"])

    for item in portfolio:
        writer.writerow([item["stock"], item["price"], item["quantity"], item["total"]])

    grand_total = sum(item["total"] for item in portfolio)
    writer.writerow([])
    writer.writerow(["Total Investment", "", "", grand_total])

    buffer = io.BytesIO(output.getvalue().encode("utf-8"))
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype="text/csv",
        as_attachment=True,
        download_name="portfolio_report.csv",
    )


if __name__ == "__main__":
    app.run(debug=True)
