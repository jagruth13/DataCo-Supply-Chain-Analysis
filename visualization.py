import plotly.express as px
import pandas as pd
import sqlite3
import os


conn = sqlite3.connect('DataCoSupply.db')

if not os.path.exists("images"):
    os.mkdir("images")

query = "SELECT DeliveryStatus, COUNT(OrderID) AS NumberofOrders FROM ShippingDetails GROUP BY DeliveryStatus ORDER BY NumberofOrders DESC;"
data_delivery_status=pd.read_sql_query(query,conn)
fig1 = px.bar(x=data_delivery_status['DeliveryStatus'] , y=data_delivery_status['NumberofOrders']  , color=data_delivery_status['NumberofOrders'],
      labels = { 'DeliveryStatus': 'Delivery Status', 'NumberofOrders': 'Number of Orders'})
fig1.show()
if os.path.exists('images\DeliveryStatusVsNumberofOrders.jpeg'):
    os.remove('images\DeliveryStatusVsNumberofOrders.jpeg')
fig1.write_image("images\DeliveryStatusVsNumberofOrders.jpeg")

query2 = """
SELECT SD.DeliveryStatus AS DeliveryStatus, RD.Region AS OrderRegion, COUNT(SD.OrderID) AS NumberofOrders
FROM ShippingDetails AS SD, OrderDetails AS OD, VendorDetails AS VD, CityDetails AS CD, StateDetails AS ST, CountryDetails As CO, RegionDetails AS RD
WHERE SD.OrderID = OD.OrderID AND OD.VendorID = VD.VendorID AND VD.CityID = CD.CityID AND CD.StateID = ST.StateID AND ST.CountryID = CO.CountryID AND CO.RegionID = RD.RegionID
GROUP BY SD.DeliveryStatus, RD.Region ORDER BY NumberofOrders DESC;"""
data_delivery_status_region=pd.read_sql_query(query2,conn)
fig2 = px.bar(data_delivery_status_region, x='DeliveryStatus', y='NumberofOrders'  , color='OrderRegion',)
fig2.show()
if os.path.exists('images\DeliveryStatusVsNumberofOrders_OrderRegion.jpeg'):
    os.remove('images\DeliveryStatusVsNumberofOrders_OrderRegion.jpeg')
fig2.write_image("images\DeliveryStatusVsNumberofOrders_OrderRegion.jpeg")

query3 = """
SELECT CD.Segment AS CustomerSegment, Count(SD.OrderID) AS NumberofOrders
FROM CustomerDetails AS CD, ShippingDetails AS SD
WHERE CD.CustomerID = SD.CustomerID
GROUP BY CustomerSegment
ORDER BY NumberofOrders DESC
"""
data_Customer_Segment=pd.read_sql_query(query3,conn)
fig3 = px.pie(data_Customer_Segment, values='NumberofOrders', names= 'CustomerSegment', hole=0.4, title= 'Number of Orders of different Customer Segments', 
       width=600 , height=600 , color_discrete_sequence = px.colors.sequential.Jet)
fig3.show()
if os.path.exists('images\CustomerSegmentVsNumberofOrders.jpeg'):
    os.remove('images\CustomerSegmentVsNumberofOrders.jpeg')
fig3.write_image("images\CustomerSegmentVsNumberofOrders.jpeg")

query4 = """
SELECT ShippingMode, COUNT(OrderID) AS NumberofOrders
FROM ShippingDetails
GROUP BY ShippingMode
ORDER BY NumberofOrders DESC;
"""
data_Customer_Segment=pd.read_sql_query(query4,conn)
fig4 = px.pie(data_Customer_Segment, values='NumberofOrders', names= 'ShippingMode', hole=0.4, title= 'Number of Orders of different Shipping Mode', 
       width=600 , height=600 , color_discrete_sequence = px.colors.sequential.thermal)
fig4.show()
if os.path.exists('images\ShippingModeVsNumberofOrders.jpeg'):
    os.remove('images\ShippingModeVsNumberofOrders.jpeg')
fig4.write_image("images\ShippingModeVsNumberofOrders.jpeg")

query5 = """
SELECT PaymentType, COUNT(OrderID) AS NumberofOrders
FROM ShippingDEtails
GROUP BY PaymentType
ORDER BY NumberofOrders DESC;
"""
data_Customer_Segment=pd.read_sql_query(query5,conn)
fig5 = px.pie(data_Customer_Segment, values='NumberofOrders', names= 'PaymentType', hole=0.4, title= 'Number of Orders of different Payment Types', 
       width=600 , height=600 , color_discrete_sequence = px.colors.sequential.Agsunset)
fig5.show()
if os.path.exists('PaymentTypeVsNumberofOrders.jpeg'):
    os.remove('PaymentTypeVsNumberofOrders.jpeg')
fig5.write_image("images\PaymentTypeVsNumberofOrders.jpeg")

query6 = """
SELECT CD.Category AS Category, COUNT(OD.OrderID) AS NumberofOrders
FROM CategoryDetails AS CD, ProductDetails AS PD, OrderDetails AS OD
WHERE CD.CategoryID = PD.CategoryID AND PD.ProductID = OD.ProductID
GROUP BY Category
ORDER BY NumberofOrders DESC;
"""
data_Category_Name=pd.read_sql_query(query6,conn)
fig6 = px.bar(data_Category_Name, x='NumberofOrders',y = 'Category',color ='NumberofOrders')
fig6.show()
if os.path.exists('images\CategoryVsNumberofOrders.jpeg'):
    os.remove('images\CategoryVsNumberofOrders.jpeg')
fig6.write_image("images\CategoryVsNumberofOrders.jpeg")

query7 = """
SELECT CO.Country AS Country, SUM(OD.ProfitpreItem) AS ProfitofOrders
FROM OrderDetails AS OD, VendorDetails AS VD, CityDetails AS CD, StateDetails AS SD, CountryDetails AS CO
WHERE OD.VendorID = VD.VendorID AND VD.CityID = CD.CityID AND CD.StateID = SD.StateID AND SD.CountryID = CO.CountryID
GROUP BY Country
ORDER BY ProfitofOrders DESC;
"""
df_geo=pd.read_sql_query(query7,conn)
fig7 = px.choropleth(df_geo ,  locationmode='country names', locations='Country',
                    color='ProfitofOrders', # lifeExp is a column of data
                    hover_name='Country', 
                    #hover_data ='Order City',
                    color_continuous_scale=px.colors.sequential.haline)

fig7.show()
if os.path.exists('images\Country_ProfitofOrders_map.jpeg'):
    os.remove('images\Country_ProfitofOrders_map.jpeg')
fig7.write_image("images\Country_ProfitofOrders_map.jpeg")
conn.close()
