# main.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from models import Base, Product, Category


# Load environment variables

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = os.getenv("DATABASE_URL") or f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


# Create SQLAlchemy engine & sessionmaker

engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)


# Fetch all products

def fetch_all_products():
    with Session() as session:
        products = session.query(Product).all()
        print("\n--- Products ---")
        for p in products:
            print(f"{p.product_name} | Price: {p.price} | Description: {p.description}")
        return products


# Show all categories

def show_categories():
    with Session() as session:
        categories = session.query(Category).all()
        print("\nAvailable Categories:")
        for idx, c in enumerate(categories, 1):
            print(f"{idx}. {c.name}")
        return categories


# Bulk price update 

def bulk_price_update(category_name: str):
    percentage_increase = 10
    try:
        with Session() as session:
            with session.begin():  # transaction block
                category = session.query(Category).filter_by(name=category_name).first()
                if not category:
                    raise ValueError(f"Category '{category_name}' does not exist")

                stmt = (
                    update(Product)
                    .where(Product.category_id == category.id)
                    .values(price=Product.price * 1.10)  # increase by 10%
                )
                session.execute(stmt)
                print(f"\n Prices for category '{category_name}' increased by 10%")
    except (SQLAlchemyError, ValueError) as e:
        print(f"\nTransaction failed: {e}")


# Main script

if __name__ == "__main__":
    print("All products before update:")
    fetch_all_products()

    categories = show_categories()

    # User selects a category
    while True:
        try:
            choice = int(input("\nEnter the number of the category to update: "))
            if 1 <= choice <= len(categories):
                selected_category = categories[choice - 1].name
                break
            else:
                print("Invalid number, try again.")
        except ValueError:
            print("Please enter a valid integer.")

    # Perform the bulk price update
    bulk_price_update(selected_category)

    print("\nAll products after update:")
    fetch_all_products()
