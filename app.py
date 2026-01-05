# -------------------- Importaciones --------------------
import streamlit as st
import pandas as pd
from datetime import datetime
import pymysql

# -------------------- Función de conexión --------------------
def ejecutar_query(query, params=None):
    """Se conecta a Clever Cloud, ejecuta la query y cierra la conexión."""
    CLOUD_DB = {
        "host": "bhibtz5dpzno2aa2rxsz-mysql.services.clever-cloud.com",
        "user": "uyri35qixwbzfzpf",
        "password": "32ZI5cJ6oriW01DpE3T0",
        "database": "bhibtz5dpzno2aa2rxsz",
        "port": 3306,
        "cursorclass": pymysql.cursors.DictCursor,
        "connect_timeout": 10,
        "autocommit": True
    }
    resultado = []
    try:
        con = pymysql.connect(**CLOUD_DB)
        with con.cursor() as cur:
            cur.execute(query, params or [])
            resultado = cur.fetchall()
    except Exception as e:
        st.error(f"❌ Error al consultar la BD: {e}")
    finally:
        try:
            con.close()
        except:
            pass
    return resultado

# -------------------- Configuración Streamlit --------------------
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

resultado = ejecutar_query(query_activos)

if resultado:
    pedidos_activos = pd.DataFrame(resultado)
    pedidos_activos["fecha_inicio"] = pd.to_datetime(pedidos_activos["fecha_inicio"])
    pedidos_activos["Tiempo (min)"] = (datetime.now() - pedidos_activos["fecha_inicio"]).dt.total_seconds() // 60
    st.dataframe(pedidos_activos[["Pedido","Cliente","Telefono","Direccion","Total","MedioPago","Tiempo (min)"]])
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

medio_pago = st.multiselect(
    "Filtrar por Medio de Pago",
    options=["EFECTIVO","Mercado Pago QR","Transferencia","Cuenta Corriente","Débito","Crédito"],
    default=None
)

query_ventas = """
SELECT 
    p.id AS Pedido,
    c.nombre AS Cliente,
    p.total AS Total,
    UPPER(p.medio_pago) AS MedioPago,
    CONVERT_TZ(p.fecha_inicio, '+00:00', '-03:00') AS fecha_inicio
FROM pedidos p
LEFT JOIN clientes c ON c.id = p.cliente_id
WHERE p.estado_cocina_id <> 5
AND DATE(CONVERT_TZ(p.fecha_inicio, '+00:00', '-03:00')) BETWEEN %s AND %s
ORDER BY p.fecha_inicio ASC

"""
params = [fecha_inicio.strftime("%Y-%m-%d"), fecha_fin.strftime("%Y-%m-%d")]

ventas = ejecutar_query(query_ventas, params)

if ventas:
    ventas_df = pd.DataFrame(ventas)
    if medio_pago:
        ventas_df = ventas_df[ventas_df["MedioPago"].isin(medio_pago)]
    st.dataframe(ventas_df)
    total_general = ventas_df["Total"].sum()
    st.markdown(f"**Total Ventas:** ${total_general:,.2f}")
else:
    st.info("No hay ventas en el rango seleccionado.")
