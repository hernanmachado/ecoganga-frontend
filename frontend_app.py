import streamlit as st
import requests
import pandas as pd
import os
import folium
from streamlit_folium import st_folium

# ==============================
# CONFIGURACIÓN GENERAL
# ==============================
API_URL = os.getenv("API_URL", "https://hernan556.pythonanywhere.com")
st.set_page_config(page_title="Ecoganga", page_icon="🌿", layout="wide")

# ==============================
# ESTILOS VISUALES
# ==============================
def aplicar_estilos():
    st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
        background-color: #E9F5E1;
        color: #1E2D1E;
    }
    h1, h2, h3, h4 {
        color: #2E4828;
        font-weight: 700;
    }
    h1 {
        text-align: center;
        background-color: #9FBF6E;
        color: #1E2D1E;
        padding: 0.6rem;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    section.main > div {
        background-color: #F9FCF5;
        padding: 1.2rem;
        border-radius: 10px;
    }
    /* --- SIDEBAR --- */
    [data-testid="stSidebar"] {
        background-color: #9FBF6E !important;
    }
    [data-testid="stSidebar"] * {
        color: #1E2D1E !important;
    }
    /* --- TARJETAS DE PROMOS / COMERCIOS --- */
    .promo-card {
        background-color: #ffffff;
        border: 1.5px solid #9FBF6E;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        color: #1E2D1E; /* 👈 texto oscuro visible */
    }
    .promo-card h4 {
        color: #2E4828;
        margin-bottom: 6px;
    }
    .promo-card p {
        color: #1E2D1E;
    }
    footer {
        margin-top: 2rem;
        text-align: center;
        color: #2E4828;
        font-weight: 600;
        font-size: 1.05em;
        border-top: 1px solid #9FBF6E;
        padding-top: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)


# ==============================
# FUNCIONES API
# ==============================
def get_comercios():
    try:
        r = requests.get(f"{API_URL}/comercios/")
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        st.error(f"❌ Error al conectar con backend: {e}")
    return []

def get_promociones():
    try:
        r = requests.get(f"{API_URL}/promociones/")
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        st.error(f"❌ Error al conectar con backend: {e}")
    return []

# ==============================
# INTERFAZ PRINCIPAL
# ==============================
def main():
    aplicar_estilos()

    # LOGO
    logo_path = os.path.join("static", "ecoganga_logo.jpg")
    if not os.path.exists(logo_path):
        logo_path = os.path.join("backend", "static", "ecoganga_logo.jpg")
    if os.path.exists(logo_path):
        st.image(logo_path, width=120)

    st.markdown("<h1>🌿 Ecoganga</h1>", unsafe_allow_html=True)
    st.sidebar.title("🌱 Navegación")
    pagina = st.sidebar.radio("Ir a:", ["🏠 Inicio", "🛠️ CRUD Comercios", "🎯 CRUD Promos"])

    if pagina == "🏠 Inicio":
        mostrar_inicio()
    elif pagina == "🛠️ CRUD Comercios":
        crud_comercios()
    else:
        crud_promos()

    st.markdown("<footer>💚 Grupo 3 – ¡Vamos equipo!</footer>", unsafe_allow_html=True)

# ==============================
# MÓDULO: INICIO
# ==============================
def mostrar_inicio():
    comercios = get_comercios()
    promociones = get_promociones()

    # MAPA
    st.subheader("📍 Mapa de Comercios")
    if comercios:
        avg_lat = sum(c.get("latitud", -34.6) for c in comercios) / len(comercios)
        avg_lon = sum(c.get("longitud", -58.4) for c in comercios) / len(comercios)
        mapa = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)
        colores = {'dietetica': 'green', 'supermercado': 'blue', 'farmacia': 'red', 'restaurante': 'orange'}

        for c in comercios:
            folium.Marker(
                [c.get("latitud", -34.6), c.get("longitud", -58.4)],
                popup=f"<b>{c['nombre']}</b><br>{c['direccion']}<br>{c.get('telefono','')}",
                icon=folium.Icon(color=colores.get(c["tipo"], "gray"), icon="shopping-cart")
            ).add_to(mapa)
        st_folium(mapa, width=None, height=400)
    else:
        st.info("No hay comercios cargados aún.")

    # PROMOCIONES
    st.subheader("🎉 Promociones")
    if promociones:
        cols = st.columns(2)
        for i, p in enumerate(promociones):
            with cols[i % 2]:
                st.markdown(f"""
                <div class='promo-card'>
                    <h4>{p['nombre']}</h4>
                    <p><b>💰 Precio:</b> ${p['precio']}</p>
                    <p><b>🏷️ Categoría:</b> {p['categoria'].replace('_',' ').title()}</p>
                    <p>{p['descripcion']}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No hay promociones registradas.")

# ==============================
# MÓDULO: CRUD COMERCIOS
# ==============================
def crud_comercios():
    st.subheader("🛠️ Gestión de Comercios")
    comercios = get_comercios()

    with st.expander("➕ Agregar nuevo comercio"):
        with st.form("form_comercio"):
            nombre = st.text_input("Nombre*")
            tipo = st.selectbox("Tipo*", ["supermercado", "dietetica", "farmacia", "restaurante"])
            direccion = st.text_input("Dirección*")
            lat = st.number_input("Latitud", value=-34.6037)
            lon = st.number_input("Longitud", value=-58.3816)
            telefono = st.text_input("Teléfono")
            horario = st.text_input("Horario", value="Lun-Sab 9:00-20:00")

            if st.form_submit_button("💾 Guardar"):
                nuevo = {"nombre": nombre, "tipo": tipo, "direccion": direccion,
                         "latitud": lat, "longitud": lon, "telefono": telefono,
                         "email": "", "horario": horario}
                r = requests.post(f"{API_URL}/comercios/", json=nuevo)
                if r.status_code == 200:
                    st.success("✅ Comercio agregado.")
                    st.rerun()
                else:
                    st.error(f"Error al guardar: {r.text}")

    if comercios:
        st.write("### 📋 Comercios existentes")
        for c in comercios:
            st.markdown(f"**{c['nombre']}** — {c['tipo']} ({c['direccion']})")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"🗑️ Eliminar {c['id']}"):
                    requests.delete(f"{API_URL}/comercios/{c['id']}")
                    st.rerun()
            with col2:
                if st.button(f"✏️ Editar {c['id']}"):
                    st.warning("Edición pendiente de implementar.")
    else:
        st.info("No hay comercios registrados.")

# ==============================
# MÓDULO: CRUD PROMOS
# ==============================
def crud_promos():
    st.subheader("🎯 Gestión de Promociones")
    promociones = get_promociones()
    comercios = get_comercios()

    if not comercios:
        st.warning("Primero cargá comercios para asociar promociones.")
        return

    with st.expander("➕ Agregar promoción"):
        with st.form("form_promo"):
            nombre = st.text_input("Nombre*")
            desc = st.text_area("Descripción*")
            precio = st.number_input("Precio*", min_value=0.0, step=100.0)
            categoria = st.selectbox("Categoría*", ["gluten_free", "vegano", "sin_lactosa", "organico", "bajo_sodio"])
            comercio_id = st.selectbox("Comercio*", [c["id"] for c in comercios],
                                       format_func=lambda x: next((c["nombre"] for c in comercios if c["id"] == x), str(x)))

            if st.form_submit_button("💾 Guardar Promoción"):
                promo = {"nombre": nombre, "descripcion": desc, "precio": precio,
                         "categoria": categoria, "comercio_id": comercio_id}
                r = requests.post(f"{API_URL}/promociones/", json=promo)
                if r.status_code == 200:
                    st.success("✅ Promoción creada.")
                    st.rerun()
                else:
                    st.error(f"Error al guardar: {r.text}")

    if promociones:
        st.write("### 📋 Promociones registradas")
        for p in promociones:
            st.markdown(f"**{p['nombre']}** — ${p['precio']} ({p['categoria']})")
            if st.button(f"🗑️ Eliminar Promo {p['id']}"):
                requests.delete(f"{API_URL}/promociones/{p['id']}")
                st.rerun()
    else:
        st.info("No hay promociones cargadas.")

# ==============================
if __name__ == "__main__":
    main()

