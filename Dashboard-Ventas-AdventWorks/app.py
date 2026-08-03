import streamlit as st
import pandas as pd
import pyodbc
import plotly.express as px

st.set_page_config(page_title="Dashboard de Ventas - AdventWorks", layout="wide")
st.title(" Dashboard Interactivo de Ventas (AdventWorks)")

# Conexión a Somee
@st.cache_data
def run_query(query):
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=AdventWorks.mssql.somee.com;"
        "DATABASE=AdventWorks;"
        "UID=HelenAmpie_SQLLogin_1;"
        "PWD=faq9lkinn3;"
    )
    with pyodbc.connect(conn_str) as conn:
        return pd.read_sql(query, conn)

tab1, tab2, tab3 = st.tabs([
    "📍 1. Rendimiento Geográfico", 
    "📦 2. Productos & Tendencias", 
    "👥 3. Vendedores & Clientes"
])

# 1. Reporte Geográfico
with tab1:
    st.header("1. Rendimiento Geográfico y por Ubicación")
    q1 = """
    SELECT a.CountryRegion AS Country, a.StateProvince AS Region, a.City AS StoreOrCity,
           SUM(h.TotalDue) AS TotalIngresos, SUM(d.OrderQty) AS VolumenProductos
    FROM SalesLT.SalesOrderHeader h
    INNER JOIN SalesLT.SalesOrderDetail d ON h.SalesOrderID = d.SalesOrderID
    INNER JOIN SalesLT.Address a ON h.ShipToAddressID = a.AddressID
    GROUP BY a.CountryRegion, a.StateProvince, a.City
    ORDER BY TotalIngresos DESC;
    """
    df1 = run_query(q1)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.plotly_chart(px.bar(df1, x='Region', y='TotalIngresos', color='Country', title="Ingresos por Región"), use_container_width=True)
    with col2:
        st.dataframe(df1, use_container_width=True)

# 2. Productos y Tendencias
with tab2:
    st.header("2. Análisis de Productos y Tendencias Temporales")
    q2 = """
    SELECT YEAR(h.OrderDate) AS Anio, MONTH(h.OrderDate) AS Mes, pc.Name AS Categoria,
           p.Name AS Producto, SUM(d.OrderQty) AS UnidadesVendidas, SUM(d.LineTotal) AS TotalVentas
    FROM SalesLT.SalesOrderHeader h
    INNER JOIN SalesLT.SalesOrderDetail d ON h.SalesOrderID = d.SalesOrderID
    INNER JOIN SalesLT.Product p ON d.ProductID = p.ProductID
    INNER JOIN SalesLT.ProductCategory pc ON p.ProductCategoryID = pc.ProductCategoryID
    GROUP BY YEAR(h.OrderDate), MONTH(h.OrderDate), pc.Name, p.Name
    ORDER BY TotalVentas DESC;
    """
    df2 = run_query(q2)
    col1, col2 = st.columns(2)
    with col1:
        top_prod = df2.groupby('Producto')['UnidadesVendidas'].sum().reset_index().sort_values(by='UnidadesVendidas', ascending=False).head(10)
        st.plotly_chart(px.pie(top_prod, values='UnidadesVendidas', names='Producto', hole=0.4, title="Top 10 Productos"), use_container_width=True)
    with col2:
        st.plotly_chart(px.line(df2, x='Mes', y='TotalVentas', color='Categoria', title="Tendencia de Ventas"), use_container_width=True)

# 3. Vendedores y Clientes
with tab3:
    st.header("3. Desempeño de Vendedores y Clientes")
    q3 = """
    SELECT ISNULL(c.SalesPerson, 'Sin Asignar') AS Vendedor, c.CustomerID,
           ISNULL(c.CompanyName, CONCAT(c.FirstName, ' ', c.LastName)) AS Cliente,
           CASE WHEN c.CompanyName IS NOT NULL THEN 'Corporativo' ELSE 'Individual' END AS TipoCliente,
           SUM(h.TotalDue) AS TotalComprado
    FROM SalesLT.SalesOrderHeader h
    INNER JOIN SalesLT.Customer c ON h.CustomerID = c.CustomerID
    GROUP BY c.SalesPerson, c.CustomerID, c.CompanyName, c.FirstName, c.LastName
    ORDER BY TotalComprado DESC;
    """
    df3 = run_query(q3)
    col1, col2 = st.columns(2)
    with col1:
        vendedores = df3.groupby('Vendedor')['TotalComprado'].sum().reset_index().sort_values(by='TotalComprado', ascending=True)
        st.plotly_chart(px.bar(vendedores, x='TotalComprado', y='Vendedor', orientation='h', title="Ranking Vendedores"), use_container_width=True)
    with col2:
        st.plotly_chart(px.bar(df3.head(10), x='Cliente', y='TotalComprado', color='TipoCliente', title="Top Clientes"), use_container_width=True)