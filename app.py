# app_delivery.py
import streamlit as st
import pandas as pd
from datetime import datetime
from bd.base_datos import BaseDatos

# -------------------- Config --------------------
bd = BaseDatos()

st.set_page_config(page_title="Panel Delivery", layout="wide")

st.title("🚚 Panel Delivery - Pedidos Activos y Reporte de Ventas")

# -------------------- PEDIDOS ACTIVOS --------------------
st.header("📋 Pedidos Activos")

query_activos = """
SELECT 
    p.id AS Pedido,
    c.nombre AS Cliente,
    c.telefono AS Telefono,
    p.direccion_entrega AS Direccion,
    p.total AS Total,
    p.medio_pago AS MedioPago,
    p.fecha_inicio
FROM pedidos p
LEFT JOIN clientes c ON c.id = p.cliente_id
WHERE p.estado_cocina_id IN (1,2,3)
ORDER BY p.fecha_inicio ASC
"""

resultado = bd.consultar(query_activos)

# Columnas correctas
cols = ["Pedido","Cliente","Teléfono","Dirección","Total","MedioPago","fecha_inicio"]
if resultado:
    pedidos_activos = pd.DataFrame(resultado, columns=cols)
    
    # Calcular tiempo desde creación
    pedidos_activos["fecha_inicio"] = pd.to_datetime(pedidos_activos["fecha_inicio"])
    pedidos_activos["Tiempo (min)"] = (datetime.now() - pedidos_activos["fecha_inicio"]).dt.total_seconds() // 60

    st.dataframe(pedidos_activos[["Pedido","Cliente","Teléfono","Dirección","Total","MedioPago","Tiempo (min)"]])
else:
    st.info("No hay pedidos activos ahora.")

# -------------------- REPORTE DE VENTAS --------------------
st.header("💰 Reporte de Ventas")

# Filtros
col1, col2 = st.columns(2)
with col1:
    fecha_inicio = st.date_input("Desde", value=pd.to_datetime("today"))
with col2:
    fecha_fin = st.date_input("Hasta", value=pd.to_datetime("today"))

medio_pago = st.multiselect("Filtrar por Medio de Pago", options=["EFECTIVO","Mercado Pago QR","Transferencia","Cuenta Corriente","Débito","Crédito"], default=None)

query_ventas = """
SELECT 
    p.id AS Pedido,
    c.nombre AS Cliente,
    p.total AS Total,
    p.medio_pago AS MedioPago,
    p.fecha_inicio
FROM pedidos p
LEFT JOIN clientes c ON c.id = p.cliente_id
WHERE p.estado_cocina_id <> 5
AND DATE(p.fecha_inicio) BETWEEN %s AND %s
"""

params = [fecha_inicio, fecha_fin]

ventas = bd.consultar(query_ventas, params)

if ventas:
    ventas_df = pd.DataFrame(ventas, columns=["Pedido","Cliente","Total","MedioPago","fecha_inicio"])
    
    # Filtrar por medio de pago si se seleccionó
    if medio_pago:
        ventas_df = ventas_df[ventas_df["MedioPago"].isin(medio_pago)]
    
    st.dataframe(ventas_df)

    total_general = ventas_df["Total"].sum()
    st.markdown(f"**Total Ventas:** ${total_general:,.2f}")
else:
    st.info("No hay ventas en el rango seleccionado.")


