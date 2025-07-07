import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Ventas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("📊 Dashboard de Análisis de Ventas")
st.markdown("---")

# Función para cargar datos
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/ventas.csv')
        df['fecha'] = pd.to_datetime(df['fecha'])
        df['total_venta'] = df['cantidad'] * df['precio_unitario']
        return df
    except FileNotFoundError:
        # Crear datos de ejemplo si no existe el archivo
        np.random.seed(42)
        fechas = pd.date_range('2024-01-01', '2024-03-31', freq='D')
        productos = ['Laptop', 'Mouse', 'Teclado', 'Monitor', 'Auriculares']
        vendedores = ['Juan', 'Maria', 'Carlos', 'Ana', 'Luis']
        regiones = ['Norte', 'Sur', 'Centro', 'Este', 'Oeste']
        
        data = []
        for fecha in fechas:
            n_ventas = np.random.randint(1, 4)
            for _ in range(n_ventas):
                producto = np.random.choice(productos)
                precio_map = {'Laptop': 1200, 'Mouse': 25, 'Teclado': 80, 'Monitor': 300, 'Auriculares': 150}
                data.append({
                    'fecha': fecha,
                    'producto': producto,
                    'vendedor': np.random.choice(vendedores),
                    'cantidad': np.random.randint(1, 10),
                    'precio_unitario': precio_map[producto],
                    'region': np.random.choice(regiones)
                })
        
        df = pd.DataFrame(data)
        df['total_venta'] = df['cantidad'] * df['precio_unitario']
        return df

# Cargar datos
df = load_data()

# Sidebar para filtros
st.sidebar.header("🔍 Filtros")

# Filtro por fecha
fecha_min = df['fecha'].min()
fecha_max = df['fecha'].max()
fecha_inicio, fecha_fin = st.sidebar.date_input(
    "Selecciona rango de fechas",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max
)

# Filtro por región
regiones_disponibles = df['region'].unique()
regiones_seleccionadas = st.sidebar.multiselect(
    "Selecciona regiones",
    regiones_disponibles,
    default=regiones_disponibles
)

# Filtro por producto
productos_disponibles = df['producto'].unique()
productos_seleccionados = st.sidebar.multiselect(
    "Selecciona productos",
    productos_disponibles,
    default=productos_disponibles
)

# Aplicar filtros
df_filtrado = df[
    (df['fecha'] >= pd.to_datetime(fecha_inicio)) &
    (df['fecha'] <= pd.to_datetime(fecha_fin)) &
    (df['region'].isin(regiones_seleccionadas)) &
    (df['producto'].isin(productos_seleccionados))
]

# Métricas principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_ventas = df_filtrado['total_venta'].sum()
    st.metric("💰 Ventas Totales", f"${total_ventas:,.2f}")

with col2:
    total_productos = df_filtrado['cantidad'].sum()
    st.metric("📦 Productos Vendidos", f"{total_productos:,}")

with col3:
    promedio_venta = df_filtrado['total_venta'].mean()
    st.metric("📊 Promedio por Venta", f"${promedio_venta:.2f}")

with col4:
    num_transacciones = len(df_filtrado)
    st.metric("🔢 Transacciones", f"{num_transacciones:,}")

st.markdown("---")

# Gráficos
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Ventas por Día")
    ventas_diarias = df_filtrado.groupby('fecha')['total_venta'].sum().reset_index()
    
    fig_linea = px.line(
        ventas_diarias, 
        x='fecha', 
        y='total_venta',
        title="Tendencia de Ventas Diarias"
    )
    fig_linea.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Ventas ($)",
        hovermode='x unified'
    )
    st.plotly_chart(fig_linea, use_container_width=True)

with col2:
    st.subheader("🥧 Ventas por Región")
    ventas_region = df_filtrado.groupby('region')['total_venta'].sum().reset_index()
    
    fig_pie = px.pie(
        ventas_region, 
        values='total_venta', 
        names='region',
        title="Distribución de Ventas por Región"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# Gráficos adicionales
col3, col4 = st.columns(2)

with col3:
    st.subheader("📊 Productos Más Vendidos")
    productos_ventas = df_filtrado.groupby('producto')['cantidad'].sum().reset_index()
    productos_ventas = productos_ventas.sort_values('cantidad', ascending=False)
    
    fig_bar = px.bar(
        productos_ventas,
        x='cantidad',
        y='producto',
        orientation='h',
        title="Cantidad Vendida por Producto"
    )
    fig_bar.update_layout(
        xaxis_title="Cantidad",
        yaxis_title="Producto"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col4:
    st.subheader("👥 Rendimiento de Vendedores")
    vendedores_ventas = df_filtrado.groupby('vendedor')['total_venta'].sum().reset_index()
    vendedores_ventas = vendedores_ventas.sort_values('total_venta', ascending=False)
    
    fig_bar_vendedores = px.bar(
        vendedores_ventas,
        x='vendedor',
        y='total_venta',
        title="Ventas por Vendedor"
    )
    fig_bar_vendedores.update_layout(
        xaxis_title="Vendedor",
        yaxis_title="Ventas ($)"
    )
    st.plotly_chart(fig_bar_vendedores, use_container_width=True)

# Tabla de datos
st.markdown("---")
st.subheader("📋 Datos Detallados")

# Configurar la tabla
st.dataframe(
    df_filtrado.sort_values('fecha', ascending=False),
    use_container_width=True,
    height=400
)

# Estadísticas adicionales
st.markdown("---")
st.subheader("📊 Estadísticas Resumidas")

col1, col2 = st.columns(2)

with col1:
    st.write("**Top 3 Productos por Ventas:**")
    top_productos = df_filtrado.groupby('producto')['total_venta'].sum().sort_values(ascending=False).head(3)
    for i, (producto, venta) in enumerate(top_productos.items(), 1):
        st.write(f"{i}. {producto}: ${venta:,.2f}")

with col2:
    st.write("**Top 3 Vendedores:**")
    top_vendedores = df_filtrado.groupby('vendedor')['total_venta'].sum().sort_values(ascending=False).head(3)
    for i, (vendedor, venta) in enumerate(top_vendedores.items(), 1):
        st.write(f"{i}. {vendedor}: ${venta:,.2f}")

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** Usa los filtros en la barra lateral para explorar diferentes segmentos de datos.")
