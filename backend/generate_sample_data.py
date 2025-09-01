"""
Sample data generator for Retail Analytics Platform
"""
import random
from datetime import datetime, timedelta
from faker import Faker
import json

fake = Faker()

def generate_sample_products(count=50):
    """Generate sample product data"""
    categories = ["Electronics", "Clothing", "Home & Garden", "Sports", "Books", "Health", "Automotive"]
    brands = ["Samsung", "Apple", "Nike", "Adidas", "Sony", "LG", "Dell", "HP"]
    
    products = []
    for i in range(count):
        category = random.choice(categories)
        price = round(random.uniform(10, 1000), 2)
        cost = round(price * random.uniform(0.4, 0.8), 2)
        
        product = {
            "name": fake.catch_phrase(),
            "category": category,
            "subcategory": f"{category} Accessories",
            "brand": random.choice(brands),
            "price": price,
            "cost": cost,
            "description": fake.text(max_nb_chars=200),
            "sku": f"SKU{i+1:04d}",
            "stock_quantity": random.randint(0, 100),
            "reorder_level": random.randint(5, 20),
            "is_active": True
        }
        products.append(product)
    
    return products

def generate_sample_customers(count=100):
    """Generate sample customer data"""
    segments = ["VIP", "Regular", "New", "Inactive"]
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia"]
    
    customers = []
    for i in range(count):
        customer = {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
            "phone": fake.phone_number(),
            "address": fake.address(),
            "city": random.choice(cities),
            "state": fake.state_abbr(),
            "zip_code": fake.zipcode(),
            "country": "USA",
            "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=80).isoformat(),
            "customer_segment": random.choice(segments),
            "is_active": True
        }
        customers.append(customer)
    
    return customers

def generate_sample_sales(products, customers, count=500):
    """Generate sample sales data"""
    sales_channels = ["in-store", "online", "mobile"]
    payment_methods = ["credit_card", "debit_card", "cash", "paypal"]
    stores = ["Store A", "Store B", "Store C", "Main Store"]
    
    sales = []
    for i in range(count):
        product = random.choice(products)
        customer = random.choice(customers)
        quantity = random.randint(1, 5)
        unit_price = product["price"]
        total_amount = quantity * unit_price
        discount = round(total_amount * random.uniform(0, 0.2), 2)
        tax = round((total_amount - discount) * 0.08, 2)
        final_amount = total_amount - discount + tax
        
        # Generate date within last 90 days
        sale_date = datetime.now() - timedelta(days=random.randint(0, 90))
        
        sale = {
            "product_id": products.index(product) + 1,  # Assuming 1-based IDs
            "customer_id": customers.index(customer) + 1,
            "quantity": quantity,
            "unit_price": unit_price,
            "total_amount": total_amount,
            "discount_amount": discount,
            "tax_amount": tax,
            "final_amount": final_amount,
            "sale_date": sale_date.isoformat(),
            "payment_method": random.choice(payment_methods),
            "store_location": random.choice(stores),
            "sales_channel": random.choice(sales_channels),
            "transaction_id": f"TXN{i+1:06d}"
        }
        sales.append(sale)
    
    return sales

def save_sample_data():
    """Generate and save sample data to JSON files"""
    print("🔄 Generating sample data...")
    
    products = generate_sample_products(50)
    customers = generate_sample_customers(100)
    sales = generate_sample_sales(products, customers, 500)
    
    # Save to JSON files
    with open("sample_products.json", "w") as f:
        json.dump(products, f, indent=2)
    
    with open("sample_customers.json", "w") as f:
        json.dump(customers, f, indent=2)
    
    with open("sample_sales.json", "w") as f:
        json.dump(sales, f, indent=2)
    
    print("✅ Sample data generated successfully!")
    print(f"📦 Generated {len(products)} products")
    print(f"👥 Generated {len(customers)} customers")
    print(f"💰 Generated {len(sales)} sales transactions")

if __name__ == "__main__":
    save_sample_data()
