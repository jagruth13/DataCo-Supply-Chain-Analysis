import sqlite3
from sqlite3 import Error
import timeit

def create_connection(db_file, delete_db=False):
    import os
    if delete_db and os.path.exists(db_file):
        os.remove(db_file)

    conn = None
    try:
        conn = sqlite3.connect(db_file)
        conn.execute("PRAGMA foreign_keys = 1")
    except Error as e:
        print(e)

    return conn

def create_table(conn, create_table_sql, drop_table_name=None):
    
    if drop_table_name: # You can optionally pass drop_table_name to drop the table. 
        try:
            c = conn.cursor()
            c.execute("""DROP TABLE IF EXISTS %s""" % (drop_table_name))
        except Error as e:
            print(e)
    
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)
        
def execute_sql_statement(sql_statement, conn):
    cur = conn.cursor()
    cur.execute(sql_statement)

    rows = cur.fetchall()

    return rows

def create_market(db_file,data_file):
    conn = create_connection(db_file)
    table = 'CREATE TABLE MarketDetails (MarketID INTEGER NOT NULL PRIMARY KEY, Market TEXT NOT NULL);'
    create_table(conn, table, 'MarketDetails')
    market_list = []
    header = None
    pos = 0
    with open(data_file, 'r') as file:
        for line in file:
            line = line.strip().strip('\n')
            if header == None:
                header = line.split(',')
                for i in range(0, len(header)):
                    if header[i] == 'Market':
                        pos = i
                        break
                continue
            line = line.split(',')
            if len(market_list) == 0:
                market_list.append((line[pos],))
            else:
                if (line[pos],) not in market_list:
                    market_list.append((line[pos],))
    market_list.append(('Customer',))
    market_list.sort()
    market_dat = "INSERT INTO MarketDetails (Market) VALUES (?);"
    cur = conn.cursor()
    cur.executemany(market_dat, market_list)
    conn.commit()
    conn.close()
    
def create_region(db_file,data_file):
    conn = create_connection(db_file)
    table = 'CREATE TABLE RegionDetails (RegionID INTEGER NOT NULL PRIMARY KEY, Region TEXT NOT NULL, MarketID INTEGER NOT NULL, FOREIGN KEY(MarketID) REFERENCES MarketDetails(MarketID));'
    create_table(conn, table, 'RegionDetails')
    region_list = []
    header = None
    pos = [None, None]
    with open(data_file, 'r') as file:
        for line in file:
            line = line.strip().strip('\n')
            if header == None:
                header = line.split(',')
                for i in range(0, len(header)):
                    if header[i] == 'Order Region':
                        pos[0] = i
                    elif header[i] == 'Market':
                        pos[1] = i
                    elif None not in pos:
                        break
                continue
            line = line.split(',')
            get_id = "SELECT MarketID FROM MarketDetails WHERE Market = '"+line[pos[1]]+"';"
            id = execute_sql_statement(get_id, conn)
            if len(region_list) == 0:
                region_list.append((line[pos[0]],id[0][0]))
            else:
                if (line[pos[0]],id[0][0]) not in region_list:
                    region_list.append((line[pos[0]],id[0][0]))
    get_id = "SELECT MarketID FROM MarketDetails WHERE Market = 'Customer';"
    id = execute_sql_statement(get_id, conn)
    region_list.append(('Customer',id[0][0]))
    region_list.sort()
    region_dat = "INSERT INTO RegionDetails (Region, MarketID) VALUES (?,?);"
    cur = conn.cursor()
    cur.executemany(region_dat, region_list)
    conn.commit()
    conn.close()
    
def create_country(db_file,data_file):
    conn = create_connection(db_file)
    table = 'CREATE TABLE CountryDetails (CountryID INTEGER NOT NULL PRIMARY KEY, Country TEXT NOT NULL, RegionID INTEGER, FOREIGN KEY(RegionID) REFERENCES RegionDetails(RegionID));'
    create_table(conn, table, 'CountryDetails')
    dict_region = {}
    sql = "SELECT Region, RegionID FROM RegionDetails;"
    rows = execute_sql_statement(sql, conn)
    for i in rows:
        dict_region[i[0]] = i[1]
    country_list = []
    header = None
    pos = [None,None,None]
    with open(data_file, 'r') as file:
        for line in file:
            line = line.strip().strip('\n')
            if header == None:
                header = line.split(',')
                for i in range(0, len(header)):
                    if header[i] == 'Order Region':
                        pos[2] = i
                    elif header[i] == 'Order Country':
                        pos[0] = i
                    elif header[i] == 'Customer Country':
                        pos[1] = i
                    elif None not in pos:
                        break
                continue
            line = line.split(',')
            id = dict_region[line[pos[2]]] 
            if len(country_list) == 0:
                country_list.append((line[pos[0]],id))
                country_list.append((line[pos[1]],dict_region['Customer']))
            else:
                if (line[pos[0]],id) not in country_list:
                    country_list.append((line[pos[0]],id))
                if (line[pos[1]],dict_region['Customer']) not in country_list:
                    country_list.append((line[pos[1]],dict_region['Customer']))
    country_list.sort()
    country_dat = "INSERT INTO CountryDetails (Country, RegionID) VALUES (?,?);"
    cur = conn.cursor()
    cur.executemany(country_dat, country_list)
    conn.commit()
    conn.close()

def create_state(db_file,data_file):
    conn = create_connection(db_file)
    table = 'CREATE TABLE StateDetails (StateID INTEGER NOT NULL PRIMARY KEY, State TEXT NOT NULL, CountryID INTEGER NOT NULL, FOREIGN KEY(CountryID) REFERENCES CountryDetails(CountryID));'
    create_table(conn, table, 'StateDetails')
    dict_country = {}
    sql = "SELECT Country, CountryID FROM CountryDetails;"
    rows = execute_sql_statement(sql, conn)
    for i in rows:
        dict_country[i[0]] = i[1]
    state_list = []
    header = None
    pos = [None,None,None,None]
    with open(data_file, 'r') as file:
        for line in file:
            line = line.strip().strip('\n')
            if header == None:
                header = line.split(',')
                for i in range(0, len(header)):
                    if header[i] == 'Order Country':
                        pos[1] = i
                    elif header[i] == 'Order State':
                        pos[0] = i
                    elif header[i] == 'Customer Country':
                        pos[3] = i
                    elif header[i] == 'Customer State':
                        pos[2] = i
                    elif None not in pos:
                        break
                continue
            line = line.split(',')
            id_order = dict_country[line[pos[1]]]
            id_cust = dict_country[line[pos[3]]]    
            if len(state_list) == 0:
                state_list.append((line[pos[0]],id_order))
                state_list.append((line[pos[2]],id_cust))
            else:
                if (line[pos[0]],id_order) not in state_list:
                    state_list.append((line[pos[0]],id_order))
                if (line[pos[2]],id_cust) not in state_list:
                    state_list.append((line[pos[2]],id_cust))
    state_list.sort()
    state_dat = "INSERT INTO StateDetails (State, CountryID) VALUES (?,?);"
    cur = conn.cursor()
    cur.executemany(state_dat, state_list)
    conn.commit()
    conn.close()

def create_city(db_file,data_file):
    conn = create_connection(db_file)
    table = 'CREATE TABLE CityDetails (CityID INTEGER NOT NULL PRIMARY KEY, City TEXT NOT NULL, StateID INTEGER NOT NULL, FOREIGN KEY(StateID) REFERENCES StateDetails(StateID));'
    create_table(conn, table, 'CityDetails')
    data = "SELECT SD.StateID, SD.State, CD.Country FROM StateDetails AS SD, CountryDetails AS CD WHERE CD.CountryID = SD.CountryID;"
    rows = execute_sql_statement(data,conn)
    dict_cs = {}
    for i in rows:
        dict_cs[i[1]+","+i[2]] = i[0]
    city_list = []
    header = None
    pos = [None,None,None,None,None,None]
    with open(data_file, 'r') as file:
        for line in file:
            line = line.strip().strip('\n')
            if header == None:
                header = line.split(',')
                for i in range(0, len(header)):
                    if header[i] == 'Order State':
                        pos[1] = i
                    elif header[i] == 'Order City':
                        pos[0] = i
                    elif header[i] == 'Customer State':
                        pos[3] = i
                    elif header[i] == 'Customer City':
                        pos[2] = i
                    elif header[i] == 'Order Country':
                        pos[4] = i
                    elif header[i] == 'Customer Country':
                        pos[5] = i
                    elif None not in pos:
                        break
                continue
            line = line.split(',')
            id_order = dict_cs[line[pos[1]]+","+line[pos[4]]]
            id_cust = dict_cs[line[pos[3]]+","+line[pos[5]]]    
            if len(city_list) == 0:
                city_list.append((line[pos[0]],id_order))
                city_list.append((line[pos[2]],id_cust))
            else:
                if (line[pos[0]],id_order) not in city_list:
                    city_list.append((line[pos[0]],id_order))
                if (line[pos[2]],id_cust) not in city_list:
                    city_list.append((line[pos[2]],id_cust))
    city_list.sort()
    city_dat = "INSERT INTO CityDetails (City, StateID) VALUES (?,?);"
    cur = conn.cursor()
    cur.executemany(city_dat, city_list)
    conn.commit()
    conn.close()

def create_dept(db_file,data_file):
    conn = create_connection(db_file)
    table = 'CREATE TABLE DepartmentDetails (DepartmentID INTEGER NOT NULL PRIMARY KEY, Department TEXT NOT NULL);'
    create_table(conn, table, 'DepartmentDetails')
    dept_list = []
    header = None
    pos = None
    with open(data_file, 'r') as file:
        for line in file:
            line = line.strip().strip('\n')
            if header == None:
                header = line.split(',')
                for i in range(0, len(header)):
                    if header[i] == 'Department Name':
                        pos = i
                        break
                continue
            line = line.split(',')
            if len(dept_list) == 0:
                dept_list.append((line[pos],))
            else:
                if (line[pos],) not in dept_list:
                    dept_list.append((line[pos],))
    dept_list.sort()
    dept_dat = "INSERT INTO DepartmentDetails (Department) VALUES (?);"
    cur = conn.cursor()
    cur.executemany(dept_dat, dept_list)
    conn.commit()
    conn.close()

def create_cat(db_file,data_file):
    conn = create_connection(db_file)
    table = 'CREATE TABLE CategoryDetails (CategoryID INTEGER NOT NULL PRIMARY KEY, Category TEXT NOT NULL, DepartmentID INTEGER NOT NULL, FOREIGN KEY(DepartmentID) REFERENCES DepartmentDetails(DepartmentID));'
    create_table(conn, table, 'CategoryDetails')
    cat_list = []
    header = None
    pos = [None,None]
    with open(data_file, 'r') as file:
        for line in file:
            line = line.strip().strip('\n')
            if header == None:
                header = line.split(',')
                for i in range(0, len(header)):
                    if header[i] == 'Department Name':
                        pos[1] = i
                    elif header[i] == 'Category Name':
                        pos[0] = i
                    elif None not in pos:
                        break
                continue
            line = line.split(',')
            get_id = "SELECT DepartmentID FROM DepartmentDetails WHERE Department = '"+line[pos[1]]+"';"
            id = execute_sql_statement(get_id, conn)
            if len(cat_list) == 0:
                cat_list.append((line[pos[0]],id[0][0]))
            else:
                if (line[pos[0]],id[0][0]) not in cat_list:
                    cat_list.append((line[pos[0]],id[0][0]))
    cat_list.sort()
    cat_dat = "INSERT INTO CategoryDetails (Category, DepartmentID) VALUES (?,?);"
    cur = conn.cursor()
    cur.executemany(cat_dat, cat_list)
    conn.commit()
    conn.close()

def create_prod(db_file,data_file):
    conn = create_connection(db_file)
    table = 'CREATE TABLE ProductDetails (ProductID INTEGER NOT NULL PRIMARY KEY, Product TEXT NOT NULL, ProductUnitPrice REAL NOT NULL, CategoryID INTEGER NOT NULL, FOREIGN KEY(CategoryID) REFERENCES CategoryDetails(CategoryID));'
    create_table(conn, table, 'ProductDetails')
    prod_list = []
    header = None
    pos = [None,None,None]
    with open(data_file, 'r') as file:
        for line in file:
            line = line.strip().strip('\n')
            if header == None:
                header = line.split(',')
                for i in range(0, len(header)):
                    if header[i] == 'Product Name':
                        pos[0] = i
                    elif header[i] == 'Category Name':
                        pos[2] = i
                    elif header[i] == 'Product Price':
                        pos[1] = i
                    elif None not in pos:
                        break
                continue
            line = line.split(',')
            get_id = "SELECT CategoryID FROM CategoryDetails WHERE Category = \""+line[pos[2]]+"\";"
            id = execute_sql_statement(get_id, conn)
            if len(prod_list) == 0:
                prod_list.append((line[pos[0]],line[pos[1]],id[0][0]))
            else:
                if (line[pos[0]],line[pos[1]],id[0][0]) not in prod_list:
                    prod_list.append((line[pos[0]],line[pos[1]],id[0][0]))
    prod_list.sort()
    prod_dat = "INSERT INTO ProductDetails (Product, ProductUnitPrice, CategoryID) VALUES (?,?,?);"
    cur = conn.cursor()
    cur.executemany(prod_dat, prod_list)
    conn.commit()
    conn.close()

def create_csc_dict(db_file):
    data = "SELECT CiD.CityID, CiD.CIty, SD.State, CD.Country FROM CityDetails AS CiD, StateDetails AS SD, CountryDetails AS CD WHERE CiD.StateID = SD.StateID AND CD.CountryID = SD.CountryID;"
    conn = create_connection(db_file)
    rows = execute_sql_statement(data, conn)
    csc_dict = {}
    for i in rows:
        csc_dict[i[1]+","+i[2]+","+i[3]] = i[0]
    conn.close()
    return csc_dict   

def create_vend(db_file,data_file,csc_dict):
    conn = create_connection(db_file)
    table = 'CREATE TABLE VendorDetails (VendorID INTEGER NOT NULL PRIMARY KEY, Zipcode TEXT NOT NULL, CityID INTEGER NOT NULL, FOREIGN KEY(CityID) REFERENCES CityDetails(CityID));'
    create_table(conn, table, 'VendorDetails')
    prod_list = []
    header = None
    pos = [None,None,None,None]
    with open(data_file, 'r') as file:
        for line in file:
            line = line.strip().strip('\n')
            if header == None:
                header = line.split(',')
                for i in range(0, len(header)):
                    if header[i] == 'Order Zipcode':
                        pos[0] = i
                    elif header[i] == 'Order City':
                        pos[1] = i
                    elif header[i] == 'Order State':
                        pos[2] = i
                    elif header[i] == 'Order Country':
                        pos[3] = i
                    elif None not in pos:
                        break
                continue
            line = line.split(',')
            id = csc_dict[line[pos[1]]+","+line[pos[2]]+","+line[pos[3]]]
            if len(prod_list) == 0:
                prod_list.append((line[pos[0]],id))
            else:
                if (line[pos[0]],id) not in prod_list:
                    prod_list.append((line[pos[0]],id))
    prod_list.sort()
    prod_dat = "INSERT INTO VendorDetails (Zipcode, CityID) VALUES (?,?);"
    cur = conn.cursor()
    cur.executemany(prod_dat, prod_list)
    conn.commit()
    conn.close()

def create_cust(db_file,data_file,csc_dict):
    conn = create_connection(db_file)
    table = 'CREATE TABLE CustomerDetails (CustomerID INTEGER NOT NULL PRIMARY KEY, Fname TEXT NOT NULL, Lname TEXT, Segment TEXT NOT NULL, Address TEXT NOT NULL, CityID INTEGER NOT NULL, Zipcode TEXT NOT NULL, FOREIGN KEY(CityID) REFERENCES CityDetails(CityID));'
    create_table(conn, table, 'CustomerDetails')
    cust_list = []
    header = None
    pos = [None,None,None,None,None,None,None,None,None]
    with open(data_file, 'r') as file:
        for line in file:
            line = line.strip().strip('\n')
            if header == None:
                header = line.split(',')
                for i in range(0, len(header)):
                    if header[i] == 'Customer Fname':
                        pos[0] = i
                    elif header[i] == 'Customer Lname':
                        pos[1] = i
                    elif header[i] == 'Customer Segment':
                        pos[2] = i
                    elif header[i] == 'Customer Street':
                        pos[3] = i
                    elif header[i] == 'Customer City':
                        pos[4] = i
                    elif header[i] == 'Customer State':
                        pos[5] = i
                    elif header[i] == 'Customer Zipcode':
                        pos[6] = i
                    elif header[i] == 'Customer Country':
                        pos[7] = i
                    elif header[i] == 'Customer Id':
                        pos[8] = i
                    elif None not in pos:
                        break
                continue
            line = line.split(',')
            id = csc_dict[line[pos[4]]+","+line[pos[5]]+","+line[pos[7]]]
            if len(cust_list) == 0:
                cust_list.append((line[pos[8]],line[pos[0]],line[pos[1]],line[pos[2]],line[pos[3]],id,line[pos[6]]))
            flag = 1
            for i in cust_list:
                if line[pos[8]] == i[0]:
                    flag = 0
                    break
            if flag:
                cust_list.append((line[pos[8]],line[pos[0]],line[pos[1]],line[pos[2]],line[pos[3]],id,line[pos[6]]))
    cust_list.sort()
    cust_data = "INSERT INTO CustomerDetails (CustomerID, Fname, Lname, Segment, Address, CityID, Zipcode) VALUES (?,?,?,?,?,?,?);"
    cur = conn.cursor()
    cur.executemany(cust_data,cust_list)
    conn.commit()
    conn.close

def create_ship(db_file,data_file):
    from datetime import datetime
    conn = create_connection(db_file)
    table = 'CREATE TABLE ShippingDetails (OrderID INTEGER NOT NULL PRIMARY KEY, CustomerID INTEGER NOT NULL, OrderStatus TEXT NOT NULL, PaymentType TEXT NOT NULL, OrderDate DATE NOT NULL, ActualNoDays INTEGER NOT NULL, EstimateNoDays INTEGER NOT NULL, DeliveryStatus TEXT NOT NULL, LateRisk INTEGER NOT NULL, ShippingDate DATE NOT NULL, ShippingMode TEXT NOT NULL, FOREIGN KEY(CustomerID) REFERENCES CustomerDetails(CustomerID));'
    create_table(conn, table, 'ShippingDetails')
    ship_list = []
    header = None
    pos = [None,None,None,None,None,None,None,None,None,None,None]
    with open(data_file, 'r') as file:
        for line in file:
            line = line.strip().strip('\n')
            if header == None:
                header = line.split(',')
                for i in range(0, len(header)):
                    if header[i] == 'Order Id':
                        pos[0] = i
                    elif header[i] == 'Order Status':
                        pos[1] = i
                    elif header[i] == 'Type':
                        pos[2] = i
                    elif header[i] == 'order date (DateOrders)':
                        pos[3] = i
                    elif header[i] == 'Days for shipping (real)':
                        pos[4] = i
                    elif header[i] == 'Days for shipment (scheduled)':
                        pos[5] = i
                    elif header[i] == 'Delivery Status':
                        pos[6] = i
                    elif header[i] == 'Late_delivery_risk':
                        pos[7] = i
                    elif header[i] == 'shipping date (DateOrders)':
                        pos[8] = i
                    elif header[i] == 'Shipping Mode':
                        pos[9] = i
                    elif header[i] == 'Customer Id':
                        pos[10] = i
                    elif None not in pos:
                        break
                continue
            line = line.split(',')
            date = line[pos[3]].split('/')
            if len(date[0]) == 1:
                date[0] = '0'+date[0]
            if len(date[1]) == 1:
                date[1] = '0'+date[1]
            date2 = datetime.strptime(date[0]+"/"+date[1]+"/"+date[2],'%m/%d/%Y %H:%M').strftime('%Y-%m-%d')
            if len(ship_list) == 0:
                ship_list.append((line[pos[10]],line[pos[0]],line[pos[1]],line[pos[2]],date2,line[pos[4]],line[pos[5]],line[pos[6]],line[pos[7]],line[pos[8]],line[pos[9]]))
            flag = 1
            for i in ship_list:
                if i[1] == line[pos[0]]:
                    flag = 0
                    break
            if flag:
                ship_list.append((line[pos[10]],line[pos[0]],line[pos[1]],line[pos[2]],date2,line[pos[4]],line[pos[5]],line[pos[6]],line[pos[7]],line[pos[8]],line[pos[9]]))
    ship_data = "INSERT INTO ShippingDetails (CustomerID, OrderID, OrderStatus, PaymentType, OrderDate, ActualNoDays, EstimateNoDays, DeliveryStatus, LateRisk, ShippingDate, ShippingMode) VALUES (?,?,?,?,?,?,?,?,?,?,?);"
    cur = conn.cursor()
    cur.executemany(ship_data,ship_list)
    conn.commit()
    conn.close

def create_order(db_file,data_file,csc_dict):
    conn = create_connection(db_file)
    table = 'CREATE TABLE OrderDetails (ItemID INTEGER NOT NULL PRIMARY KEY, OrderID INTEGER NOT NULL, VendorID INTEGER NOT NULL, ProductID INTEGER NOT NULL, ItemDiscountRate REAL, ItemQuantity INTEGER, ProfitpreItem REAL, Sales REAL, FOREIGN KEY(OrderID) REFERENCES ShippingDetails(OrderID), FOREIGN KEY(VendorID) REFERENCES VendorDetails(VendorID), FOREIGN KEY(ProductID) REFERENCES ProductDetails(ProductID));'
    create_table(conn, table, 'OrderDetails')
    order_list = []
    header = None
    pos = [None,None,None,None,None,None,None,None,None,None]
    with open(data_file, 'r') as file:
        for line in file:
            line = line.strip().strip('\n')
            if header == None:
                header = line.split(',')
                for i in range(0, len(header)):
                    if header[i] == 'Order Id':
                        pos[0] = i
                    elif header[i] == 'Order City':
                        pos[1] = i
                    elif header[i] == 'Order State':
                        pos[2] = i
                    elif header[i] == 'Order Country':
                        pos[3] = i
                    elif header[i] == 'Order Profit Per Order':
                        pos[4] = i
                    elif header[i] == 'Product Name':
                        pos[5] = i
                    elif header[i] == 'Order Item Discount Rate':
                        pos[6] = i
                    elif header[i] == 'Order Item Quantity':
                        pos[7] = i
                    elif header[i] == 'Order Zipcode':
                        pos[8] = i
                    elif header[i] == 'Sales':
                        pos[9] = i
                    elif None not in pos:
                        break
                continue
            line = line.split(',')
            cityid = csc_dict[line[pos[1]]+","+line[pos[2]]+","+line[pos[3]]]
            vendid = execute_sql_statement("SELECT VendorID FROM VendorDetails WHERE CityID = "+str(cityid)+" AND Zipcode = \""+line[pos[8]]+"\";",conn)
            prodid = execute_sql_statement("SELECT ProductID FROM ProductDetails WHERE Product = \""+line[pos[5]]+"\";",conn)
            order_list.append((line[pos[0]],vendid[0][0],prodid[0][0],line[pos[6]],line[pos[7]],line[pos[4]],line[pos[9]]))
    order_data = "INSERT INTO OrderDetails (OrderID, VendorID, ProductID, ItemDiscountRate, ItemQuantity, ProfitpreItem,Sales) VALUES (?,?,?,?,?,?,?);"
    cur = conn.cursor()
    cur.executemany(order_data,order_list)
    conn.commit()
    conn.close

db_filename = 'DataCoSupply.db'
data_file = 'DataCoSupplyChainDataset.csv'
conn = create_connection(db_filename, True)
conn.close()
print('start')
start = timeit.default_timer()
create_market(db_filename,data_file)
print('Market done')
s1 = timeit.default_timer()
print('Time :',s1-start)
create_region(db_filename,data_file)
print('Region Done')
s2 = timeit.default_timer()
print('Time :',s2-start)
create_country(db_filename,data_file)
print('Country Done')
s3 = timeit.default_timer()
print('Time :',s3-start)
create_state(db_filename,data_file)
print('State Done')
s4 = timeit.default_timer()
print('Time :',s4-start)
create_city(db_filename,data_file)
print("City Done")
s5 = timeit.default_timer()
print('Time :',s5-start)
create_dept(db_filename,data_file)
print("Dept Done")
s5 = timeit.default_timer()
print('Time :',s5-start)
create_cat(db_filename, data_file)
print("Cat Done")
s6 = timeit.default_timer()
print('Time :',s6-start)
create_prod(db_filename,data_file)
print("Prod Done")
s7 = timeit.default_timer()
print('Time :',s7-start)
csc_dict = create_csc_dict(db_filename)
create_vend(db_filename,data_file,csc_dict)
print("Vend Done")
s8 = timeit.default_timer()
print('Time :',s8-start)
create_cust(db_filename,data_file,csc_dict)
print("Cust Done")
s9 = timeit.default_timer()
print('Time :',s9-start)
create_ship(db_filename,data_file)
print("Ship Done")
s10 = timeit.default_timer()
print('Time :',s10-start)
create_order(db_filename,data_file,csc_dict)
print("Order Done")
s11 = timeit.default_timer()
print('Time :',s11-start)
