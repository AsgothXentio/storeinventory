from sqlalchemy import (create_engine, Column, Date,
                        Integer, String, Float,)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import csv
import datetime
import time
import re

engine= create_engine("sqlite:///inventory.db", echo=False)
Session= sessionmaker(bind=engine)
session= Session()
Base = declarative_base()


class Product(Base):
    __tablename__= "Product"
    product_id = Column(Integer, primary_key= True)
    product_name = Column("Product Name", String)
    product_quantity = Column("Product Quantity", Integer)
    product_price = Column("Product Price", Integer)
    date_updated = Column ("Last Updated", Date)

    def __repr__(self):
        return f"Product Name: {self.product_name}, Product quantity: {self.product_quantity}, Product Price: {self.product_price},"\
               f" Last updated: {self.date_updated}"



def clean_date(date_str):
    date_split= date_str.split("/")
    month = int(date_split[0])
    day = int(date_split[1])
    year = int(date_split[2])
    return datetime.date(year,month,day)



def clean_num(number_str):
    cleaned_str = re.sub(r'[^\d.]', "", number_str)
    try:
        number_float = float(cleaned_str)
        number_int = int(number_float * 100)
        return number_int
    except ValueError:
        print(f"Error converting '{cleaned_str}' to an integer.")
        return None


def add_csv():
    with open("c:/Users/menno/OneDrive/Desktop/Python/Storeinventory/env/inventory.csv") as csvfile:
        data = csv.reader(csvfile)
        next(data)
        for row in data:
            product_in_db = session.query(Product).filter(Product.product_name ==row[0]).one_or_none()
            if product_in_db == None:
                prod_name= row[0]
                prod_price = clean_num(row[1])
                prod_quan = row[2]
                prod_dat = clean_date(row[3])
                new_prod= Product(product_name= prod_name, product_quantity=prod_quan,
                                product_price = prod_price, date_updated=prod_dat)
                session.add(new_prod)
        session.commit()

def check_data():
    products = session.query(Product).all()
    for product in products:
        print(product.product_id)
        print(product)


Base.metadata.create_all(engine)

add_csv()
check_data()



