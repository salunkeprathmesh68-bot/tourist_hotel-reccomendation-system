import random
from datetime import datetime, timedelta
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Set deterministic seed
random.seed(42)

# Fixed starter rows from user prompt
initial_data = [
    {
        "Date": "2026-01-01",
        "Region": "West",
        "Product": "Laptop",
        "Category": "Electronics",
        "Order ID": "ORD001",
        "Customer Type": "New",
        "Campaign": "Social Media",
        "Quantity": 2,
        "Main Rate": 70000,
        "Discount Rate": 0.10,
        "Sales": 126000.0,
        "Profit": 18000.0,
        "Marketing Spend": 5000.0
    },
    {
        "Date": "2026-01-02",
        "Region": "South",
        "Product": "Mobile",
        "Category": "Electronics",
        "Order ID": "ORD002",
        "Customer Type": "Returning",
        "Campaign": "Google Ads",
        "Quantity": 3,
        "Main Rate": 45000,
        "Discount Rate": 0.05,
        "Sales": 128250.0,
        "Profit": 21000.0,
        "Marketing Spend": 3500.0
    },
    {
        "Date": "2026-01-03",
        "Region": "North",
        "Product": "Headphones",
        "Category": "Accessories",
        "Order ID": "ORD003",
        "Customer Type": "New",
        "Campaign": "Instagram",
        "Quantity": 5,
        "Main Rate": 15000,
        "Discount Rate": 0.15,
        "Sales": 63750.0,
        "Profit": 12000.0,
        "Marketing Spend": 1800.0
    },
    {
        "Date": "2026-01-04",
        "Region": "East",
        "Product": "Tablet",
        "Category": "Electronics",
        "Order ID": "ORD004",
        "Customer Type": "Returning",
        "Campaign": "Email",
        "Quantity": 2,
        "Main Rate": 40000,
        "Discount Rate": 0.08,
        "Sales": 73600.0,
        "Profit": 13000.0,
        "Marketing Spend": 2500.0
    },
    {
        "Date": "2026-01-05",
        "Region": "West",
        "Product": "Smartwatch",
        "Category": "Wearable",
        "Order ID": "ORD005",
        "Customer Type": "New",
        "Campaign": "Social Media",
        "Quantity": 4,
        "Main Rate": 32000,
        "Discount Rate": 0.12,
        "Sales": 112640.0,
        "Profit": 20000.0,
        "Marketing Spend": 2200.0
    }
]

# Product catalog with default category and base price
products_catalog = [
    {"Product": "Laptop", "Category": "Electronics", "Main Rate": 70000, "Cost Ratio": 0.72},
    {"Product": "Mobile", "Category": "Electronics", "Main Rate": 45000, "Cost Ratio": 0.70},
    {"Product": "Tablet", "Category": "Electronics", "Main Rate": 40000, "Cost Ratio": 0.71},
    {"Product": "Smart TV", "Category": "Electronics", "Main Rate": 55000, "Cost Ratio": 0.74},
    {"Product": "Headphones", "Category": "Accessories", "Main Rate": 15000, "Cost Ratio": 0.65},
    {"Product": "Bluetooth Speaker", "Category": "Accessories", "Main Rate": 8000, "Cost Ratio": 0.62},
    {"Product": "Wireless Earbuds", "Category": "Accessories", "Main Rate": 12000, "Cost Ratio": 0.64},
    {"Product": "Smartwatch", "Category": "Wearable", "Main Rate": 32000, "Cost Ratio": 0.68},
    {"Product": "Fitness Band", "Category": "Wearable", "Main Rate": 6000, "Cost Ratio": 0.60},
    {"Product": "Gaming Console", "Category": "Entertainment", "Main Rate": 48000, "Cost Ratio": 0.75},
]

regions = ["West", "South", "North", "East", "Central"]
customer_types = ["New", "Returning"]
campaigns = ["Social Media", "Google Ads", "Instagram", "Email", "Influencer", "Organic"]
discount_options = [0.00, 0.05, 0.08, 0.10, 0.12, 0.15, 0.20]

start_date = datetime(2026, 1, 6)
end_date = datetime(2026, 3, 31)
date_range_days = (end_date - start_date).days

records = list(initial_data)

order_num = 6
total_target_records = 220

for _ in range(total_target_records - len(initial_data)):
    rand_day = random.randint(0, date_range_days)
    curr_date = start_date + timedelta(days=rand_day)
    order_id = f"ORD{order_num:03d}"
    order_num += 1
    
    prod_meta = random.choice(products_catalog)
    product = prod_meta["Product"]
    category = prod_meta["Category"]
    main_rate = prod_meta["Main Rate"]
    cost_ratio = prod_meta["Cost Ratio"]
    
    region = random.choice(regions)
    cust_type = random.choices(customer_types, weights=[0.45, 0.55])[0]
    campaign = random.choices(campaigns, weights=[0.25, 0.25, 0.20, 0.15, 0.10, 0.05])[0]
    
    # Quantity between 1 and 6
    qty = random.choices([1, 2, 3, 4, 5, 6], weights=[0.35, 0.30, 0.18, 0.10, 0.05, 0.02])[0]
    
    # Discount rate
    discount_rate = random.choice(discount_options)
    
    # Exact Formula: Main Rate × Quantity × (1 − Discount Rate)
    sales = round(main_rate * qty * (1.0 - discount_rate), 2)
    
    # Cost calculation: Unit cost * qty
    cost = main_rate * cost_ratio * qty
    # Net Profit from transaction after basic goods cost and discount
    raw_profit = sales - cost
    # Apply minor realistic operational adjustment, floor at 10% of sales
    profit = round(max(raw_profit, sales * 0.12), 2)
    
    # Marketing Spend associated with the order acquisition
    if campaign == "Organic":
        mkt_spend = round(random.uniform(200, 800), 2)
    elif campaign == "Email":
        mkt_spend = round(random.uniform(800, 2600), 2)
    elif campaign == "Instagram":
        mkt_spend = round(random.uniform(1500, 4200), 2)
    elif campaign == "Social Media":
        mkt_spend = round(random.uniform(1800, 5200), 2)
    elif campaign == "Google Ads":
        mkt_spend = round(random.uniform(2500, 6500), 2)
    else:  # Influencer
        mkt_spend = round(random.uniform(3500, 8500), 2)
        
    records.append({
        "Date": curr_date.strftime("%Y-%m-%d"),
        "Region": region,
        "Product": product,
        "Category": category,
        "Order ID": order_id,
        "Customer Type": cust_type,
        "Campaign": campaign,
        "Quantity": qty,
        "Main Rate": main_rate,
        "Discount Rate": discount_rate,
        "Sales": sales,
        "Profit": profit,
        "Marketing Spend": mkt_spend
    })

# Sort records by Date
records.sort(key=lambda x: x["Date"])

# Create DataFrame
df = pd.DataFrame(records)

# Validation check
for idx, row in df.iterrows():
    expected_sales = round(row["Main Rate"] * row["Quantity"] * (1 - row["Discount Rate"]), 2)
    assert abs(row["Sales"] - expected_sales) < 0.01, f"Mismatch at row {idx}: {row['Sales']} vs {expected_sales}"

print(f"Validation successful: All {len(df)} rows adhere strictly to Sales = Main Rate * Qty * (1 - Discount Rate)")

# Save to CSV
csv_filename = "sales_marketing_dataset.csv"
df.to_csv(csv_filename, index=False)
print(f"Saved {csv_filename} successfully.")

# Save to Excel with professional styling
excel_filename = "sales_marketing_dataset.xlsx"
with pd.ExcelWriter(excel_filename, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Sales & Marketing Data", index=False)
    workbook = writer.book
    worksheet = writer.sheets["Sales & Marketing Data"]
    
    # Styling
    header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    data_font = Font(name="Calibri", size=11)
    center_align = Alignment(horizontal="center", vertical="center")
    right_align = Alignment(horizontal="right", vertical="center")
    left_align = Alignment(horizontal="left", vertical="center")
    
    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )
    
    # Format Headers
    for col_idx in range(1, len(df.columns) + 1):
        cell = worksheet.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
    
    # Format Data Rows
    for row_idx in range(2, len(df) + 2):
        for col_idx in range(1, len(df.columns) + 1):
            cell = worksheet.cell(row=row_idx, column=col_idx)
            cell.font = data_font
            cell.border = thin_border
            col_name = df.columns[col_idx - 1]
            
            if col_name in ["Date", "Region", "Category", "Order ID", "Customer Type", "Campaign"]:
                cell.alignment = center_align if col_name in ["Date", "Region", "Order ID", "Customer Type"] else left_align
            elif col_name == "Product":
                cell.alignment = left_align
            elif col_name == "Quantity":
                cell.alignment = center_align
                cell.number_format = "#,##0"
            elif col_name == "Discount Rate":
                cell.alignment = right_align
                cell.number_format = "0.0%"
            elif col_name in ["Main Rate", "Sales", "Profit", "Marketing Spend"]:
                cell.alignment = right_align
                cell.number_format = '"₹"#,##0.00'

    # Auto-fit column widths
    for col in worksheet.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        worksheet.column_dimensions[col_letter].width = max(max_len + 4, 12)

print(f"Saved styled {excel_filename} successfully.")
