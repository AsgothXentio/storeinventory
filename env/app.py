from sqlalchemy import (create_engine, Column, Date,
                        Integer, String, select, inspect, MetaData, Table)
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



def clean_date(date_str=None):
    if date_str:
        date_split = date_str.split("/")
        month = int(date_split[0])
        day = int(date_split[1])
        year = int(date_split[2])
        return datetime.date(year, month, day)
    else:
        return datetime.datetime.now().strftime("%m/%d/%Y %H:%M")



def clean_num(number_str):
    if isinstance(number_str, float):
        return int(number_str*100)
    cleaned_str = re.sub(r'[^\d.]', "", str(number_str))
    try:
        number_float = float(cleaned_str)
        number_int = int(number_float * 100)
        return number_int
    except ValueError:
        print(f"Can you my fellow human give me the correct date instead of '{cleaned_str}'.")
        return None


def add_csv():
    with open("inventory.csv") as csvfile:
        data = csv.reader(csvfile)
        next(data)
        for row in data:
            product_in_db = session.query(Product).filter(Product.product_name ==row[0]).one_or_none()
            if product_in_db == None:
                prod_name= row[0]
                prod_price = clean_num(row[1])
                prod_quan = int(row[2])
                prod_dat = clean_date(row[3])
                new_prod= Product(product_name= prod_name, product_quantity=prod_quan,
                                product_price = prod_price, date_updated=prod_dat)
                session.add(new_prod)
            else:
                prod_price = clean_num(row[1])
                prod_quan = row[2]
                prod_dat = clean_date(row[3])

        session.commit()


def check_data():
    products = session.query(Product).all()
    for product in products:
        print(f" ID {product.product_id} {product.product_name} {product.product_quantity}")


def search_id():
    product_choice = input ("Please input part of the product name to find the product ID: ")
    id_product_db = session.query(Product).filter(Product.product_name.like(f"{product_choice}%")).all()

    if id_product_db:
        for product in id_product_db:
            print(f"ID {product.product_id} {product.product_name}")
            time.sleep(0.5)
    else:
        print("No product with the given start letters found, please try again")
        time.sleep(0.5)

def add_product():
    print("Please input the following data")
    manual_name = input("Product Name: ")
    while True:
        try:
            manual_price = float(input("Price in USD (example 2.99): "))
            break
        except ValueError:
            print("please inpute a correct number")
    manual_quan = input("Quantity received: ")
    manual_in_db = session.query(Product).filter(Product.product_name == manual_name).one_or_none()
    if manual_in_db == None:
        man_name = manual_name
        man_price = clean_num(manual_price)
        man_quan = int(manual_quan)
        man_date = clean_date()
        man_prod = Product(product_name= man_name, product_quantity= man_quan, product_price= man_price, date_updated= man_date)
        print(f"We will add the following to the database: {man_name}, {man_price}, {man_quan}, Creation date: {man_date} ")
        man_cor = input("Is this correct Y/N?: ").lower()
        if man_cor == "y":
            session.add(man_prod)
        else:
            new_y= input("Do you want to add a new product Y/N: ").lower()
            if new_y == "y":
                print("Ok we will start again")
                add_product()
            else:
                print("Ok, back to the main menu it is")
                main_menu()


def add_quantity():
     while True:
        product_idcheck = input("Please input the product id for which you want to add or subtract quantity. Type 'm' to return to the main menu: ").lower()
        if product_idcheck == "m":
            main_menu()
        quantity_in_db = session.query(Product).filter(Product.product_id == product_idcheck).one_or_none()
        if quantity_in_db == None:
            new_quantityid = input("ID number not known, please enter a different id number or go back to the main menu (id/main): ").lower()
            if new_quantityid == "main":
                main_menu()
        else:
            while True:
                try:
                    add_quan = int(input("How much do you want to change the amount (if negative use the minus sign (for example -7)): "))
                    break
                except ValueError:
                    print("Please try again an add a valid number.")

            new_quantity = int(quantity_in_db.product_quantity) + add_quan
            if new_quantity <0:
                print("We cannot have less then 0 product, please check and try again")
            else:    
                print(f"New quantity for {quantity_in_db.product_name}: {new_quantity}")
                quantity_in_db.product_quantity = new_quantity
                session.commit()
                break
         



def back_up(engine, csv_filename=None):
    if csv_filename is None:
        csv_filename = input("Enter the backup name for the csv file (without the .csv extension): ")

    conn = engine.connect()
    inspector = inspect(engine)
    metadata = MetaData()

    for table_name in inspector.get_table_names():
        table = Table(table_name, metadata, autoload_with=engine)
        query = select(table)
        result = conn.execute(query)

        with open(f"{csv_filename}_{table_name}.csv", 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(result.keys())
            csv_writer.writerows(result.fetchall())

    conn.close()
    print("Back up succesfully created")
    


def main_menu():
    active_menu = True
    while active_menu == True:
        print("\rWelcome fellow human to our stores inventory database")
        print("\rAs we humans always love choice,")
        print("\rwe present you with the following options:")
        time.sleep(1)
        print("\r(\033[1mP\033[0m)roduct in stock    (P)")
        print("\r(\033[1mV\033[0m)iew product ID     (V)")
        print("\r(\033[1mA\033[0m)dd a new product   (A)")
        print("\r(\033[1mB\033[0m)ackup the database (B)")
        print("\r(\033[1mC\033[0m)hange in quantity  (C)")
        print("\r(\033[1mQ\033[0m)uit this program   (Q)")


        main_choice = input("Select your option here: ").lower()
        if main_choice == "q":
            print("Ok, we hope you enjoyed our Database. We wish you a humanly time human.")
            active_menu = False
        elif main_choice == "p":
            check_data()
        elif main_choice == "v":
            search_id()
        elif main_choice == "a":
            add_product()
        elif main_choice == "b":
            back_up(engine)
        elif main_choice == "c":
            add_quantity()


 


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    add_csv()
    main_menu()



