import streamlit as st
import requests
import pandas as pd
import os
import folium
import time
from streamlit_folium import st_folium

# ==============================
# CONFIGURACIÓN Y SEGURIDAD
# ==============================
API_URL = os.getenv("API_URL", "https://hernan556.pythonanywhere.com")
st.set_page_config(page_title="Ecoganga", page_icon="🌿", layout="wide")

# USUARIOS AUTORIZADOS PARA EL TP
USUARIOS_AUTORIZADOS = {
    "hernan": "231Ran@#",           
    "grupo3ppi": "pipistrello7"     
}

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
    [data-testid="stSidebar"] {
        background-color: #9FBF6E !important;
    }
    [data-testid="stSidebar"] * {
        color: #1E2D1E !important;
    }
    .promo-card {
        background-color: #ffffff;
        border: 1.5px solid #9FBF6E;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        color: #1E2D1E;
    }
    .promo-card h4 {
        color: #2E4828;
        margin-bottom: 6px;
    }
    .promo-card p {
        color: #1E2D1E;
    }
    .comercio-info {
        background-color: #F0F7E6;
        padding: 0.5rem;
        border-radius: 8px;
        margin-top: 0.5rem;
        border-left: 4px solid #9FBF6E;
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
# SISTEMA DE AUTENTICACIÓN
# ==============================
def mostrar_login():
    """Pantalla de login para administradores"""
    st.sidebar.title("🔐 Acceso Administrativo")
    st.sidebar.info("Ingresa tus credenciales para gestionar comercios y promociones")
    
    with st.sidebar.form("login_form"):
        usuario = st.text_input("👤 Usuario")
        password = st.text_input("🔒 Contraseña", type="password")
        submit = st.form_submit_button("🚀 Ingresar")
        
        if submit:
            if usuario in USUARIOS_AUTORIZADOS and USUARIOS_AUTORIZADOS[usuario] == password:
                st.session_state.logged_in = True
                st.session_state.usuario_actual = usuario
                st.success("✅ ¡Acceso concedido!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos")
    
    # Mostrar información pública aunque no esté logueado
    st.sidebar.markdown("---")
    st.sidebar.info("🌿 **Ecoganga** - Encuentra comercios y promociones saludables")

def mostrar_app_completa():
    """App completa con todas las funciones para administradores"""
    usuario = st.session_state.get('usuario_actual', 'Administrador')
    
    # Header con info de usuario
    st.sidebar.title(f"👋 Hola, {usuario}")
    st.sidebar.success("🔧 **Modo Administrador Activado**")
    
    # Botón de logout
    if st.sidebar.button("🚪 Cerrar sesión"):
        st.session_state.logged_in = False
        st.session_state.usuario_actual = None
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Navegación completa
    st.sidebar.title("🌱 Navegación")
    pagina = st.sidebar.radio("Ir a:", ["🏠 Inicio", "🛠️ CRUD Comercios", "🎯 CRUD Promos"])
    
    # Filtros (solo en inicio)
    if pagina == "🏠 Inicio":
        st.sidebar.title("🔍 Filtros")
        comercios = get_comercios()
        promociones = get_promociones()
        
        if comercios and isinstance(comercios, list):
            tipos_comercio = list(set([c.get('tipo', '') for c in comercios if c.get('tipo')]))
            tipos_comercio.sort()
            tipo_seleccionado = st.sidebar.selectbox("Filtrar por tipo de comercio", ["Todos"] + tipos_comercio)
        else:
            tipo_seleccionado = "Todos"
        
        if promociones and isinstance(promociones, list):
            categorias_promo = list(set([p.get('categoria', '') for p in promociones if p.get('categoria')]))
            categorias_promo.sort()
            categoria_seleccionada = st.sidebar.selectbox("Filtrar promociones por categoría", ["Todas"] + categorias_promo)
        else:
            categoria_seleccionada = "Todas"
    else:
        tipo_seleccionado = "Todos"
        categoria_seleccionada = "Todas"

    # Contenido según página
    if pagina == "🏠 Inicio":
        mostrar_inicio(tipo_seleccionado, categoria_seleccionada)
    elif pagina == "🛠️ CRUD Comercios":
        crud_comercios()
    else:
        crud_promos()

    # Refresh automático
    if st.session_state.get('refresh', False):
        st.session_state.refresh = False
        st.rerun()

    st.markdown("<footer>💚 Grupo 3 – ¡Vamos equipo!</footer>", unsafe_allow_html=True)

# ==============================
# FUNCIONES API
# ==============================
def get_comercios():
    try:
        r = requests.get(f"{API_URL}/comercios/")
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                return data
            else:
                st.error("❌ El backend devolvió un formato incorrecto")
                return []
        else:
            st.error(f"❌ Error HTTP {r.status_code}")
            return []
    except Exception as e:
        st.error(f"❌ Error al conectar con backend: {e}")
        return []

def get_promociones():
    try:
        r = requests.get(f"{API_URL}/promociones/")
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                return data
            else:
                st.error("❌ El backend devolvió un formato incorrecto")
                return []
        else:
            st.error(f"❌ Error HTTP {r.status_code}")
            return []
    except Exception as e:
        st.error(f"❌ Error al conectar con backend: {e}")
        return []

def obtener_comercio_por_id(comercio_id, comercios):
    """Busca un comercio por su ID en la lista de comercios"""
    for comercio in comercios:
        if isinstance(comercio, dict) and comercio.get('id') == comercio_id:
            return comercio
    return None

# ==============================
# INTERFAZ PRINCIPAL
# ==============================
def main():
    aplicar_estilos()

    # Inicializar estado de login
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # LOGO
    logo_path = os.path.join("static", "ecoganga_logo.jpg")
    if not os.path.exists(logo_path):
        logo_path = os.path.join("backend", "static", "ecoganga_logo.jpg")
    if os.path.exists(logo_path):
        st.image(logo_path, width=120)

    st.markdown("<h1>🌿 Ecoganga</h1>", unsafe_allow_html=True)

    # Verificar autenticación
    if not st.session_state.logged_in:
        # MODO PÚBLICO - Solo mostrar inicio
        st.sidebar.title("🌱 Navegación")
        st.sidebar.info("📍 Explora comercios y promociones cerca de ti")
        mostrar_inicio()
        
        # Mostrar login en sidebar para administradores
        mostrar_login()
        return
    
    # MODO ADMINISTRADOR - App completa
    mostrar_app_completa()

# ==============================
# MÓDULOS EXISTENTES (TUS FUNCIONES ORIGINALES)
# ==============================
def mostrar_inicio(tipo_filtro="Todos", categoria_filtro="Todas"):
    comercios = get_comercios()
    promociones = get_promociones()

    # Aplicar filtros
    if tipo_filtro != "Todos" and comercios and isinstance(comercios, list):
        comercios = [c for c in comercios if c.get('tipo') == tipo_filtro]
    
    if categoria_filtro != "Todas" and promociones and isinstance(promociones, list):
        promociones = [p for p in promociones if p.get('categoria') == categoria_filtro]

    # Mostrar contadores
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📍 Comercios", len(comercios) if comercios else 0)
    with col2:
        st.metric("🎉 Promociones", len(promociones) if promociones else 0)
    with col3:
        st.metric("🏪 Tipos", len(set([c.get('tipo') for c in comercios])) if comercios else 0)

    # MAPA
    st.subheader("📍 Mapa de Comercios")
    if comercios and isinstance(comercios, list) and len(comercios) > 0:
        comercios_validos = [c for c in comercios if isinstance(c, dict) and 'latitud' in c and 'longitud' in c]
        
        if comercios_validos:
            avg_lat = sum(float(c.get("latitud", -34.6)) for c in comercios_validos) / len(comercios_validos)
            avg_lon = sum(float(c.get("longitud", -58.4)) for c in comercios_validos) / len(comercios_validos)
            mapa = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)
            colores = {'dietetica': 'green', 'supermercado': 'blue', 'farmacia': 'red', 'restaurante': 'orange'}

            for c in comercios_validos:
                folium.Marker(
                    [float(c.get("latitud", -34.6)), float(c.get("longitud", -58.4))],
                    popup=f"<b>{c.get('nombre', 'Sin nombre')}</b><br>{c.get('direccion', '')}<br>{c.get('telefono','')}",
                    icon=folium.Icon(color=colores.get(c.get("tipo", ""), "gray"), icon="shopping-cart")
                ).add_to(mapa)
            st_folium(mapa, width=None, height=400)
        else:
            st.info("No hay comercios con coordenadas válidas.")
    else:
        st.info("No hay comercios cargados aún.")

    # PROMOCIONES
    st.subheader("🎉 Promociones")
    if promociones and isinstance(promociones, list) and len(promociones) > 0:
        cols = st.columns(2)
        for i, p in enumerate(promociones):
            with cols[i % 2]:
                # Obtener información del comercio asociado
                comercio_info = "📍 Información no disponible"
                if comercios and isinstance(comercios, list):
                    comercio_asociado = obtener_comercio_por_id(p.get('comercio_id'), comercios)
                    if comercio_asociado:
                        comercio_info = f"🏪 **{comercio_asociado.get('nombre', 'Sin nombre')}**\n\n📍 {comercio_asociado.get('direccion', 'Dirección no disponible')}"
                
                st.markdown(f"""
                <div class='promo-card'>
                    <h4>{p.get('nombre', 'Sin nombre')}</h4>
                    <p><b>💰 Precio:</b> ${p.get('precio', 'N/A')}</p>
                    <p><b>🏷️ Categoría:</b> {p.get('categoria', 'N/A').replace('_',' ').title()}</p>
                    <p>{p.get('descripcion', '')}</p>
                    <div class='comercio-info'>
                        {comercio_info}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No hay promociones registradas.")

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
                if r.status_code == 201:
                    st.success("✅ Comercio agregado.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"Error al guardar: {r.text}")

    if comercios and isinstance(comercios, list):
        st.write("### 📋 Comercios existentes")
        for c in comercios:
            if isinstance(c, dict):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{c.get('nombre', 'Sin nombre')}** — {c.get('tipo', '')} ({c.get('direccion', '')})")
                
                with col2:
                    if st.button(f"✏️ Editar {c.get('id', '')}", key=f"edit_{c.get('id', '')}"):
                        st.session_state[f'editar_comercio_{c.get("id")}'] = True
                
                with col3:
                    if st.button(f"🗑️ Eliminar {c.get('id', '')}", key=f"del_{c.get('id', '')}"):
                        requests.delete(f"{API_URL}/comercios/{c.get('id', '')}")
                        time.sleep(1)
                        st.rerun()
                
                # Formulario de edición
                if st.session_state.get(f'editar_comercio_{c.get("id")}', False):
                    with st.form(f"form_editar_comercio_{c.get('id')}"):
                        st.write("#### ✏️ Editar Comercio")
                        nuevo_nombre = st.text_input("Nombre", value=c.get('nombre', ''))
                        nuevo_tipo = st.selectbox("Tipo", ["supermercado", "dietetica", "farmacia", "restaurante"], 
                                                index=["supermercado", "dietetica", "farmacia", "restaurante"].index(c.get('tipo', 'supermercado')))
                        nueva_direccion = st.text_input("Dirección", value=c.get('direccion', ''))
                        nueva_lat = st.number_input("Latitud", value=float(c.get('latitud', -34.6037)))
                        nueva_lon = st.number_input("Longitud", value=float(c.get('longitud', -58.3816)))
                        nuevo_telefono = st.text_input("Teléfono", value=c.get('telefono', ''))
                        nuevo_horario = st.text_input("Horario", value=c.get('horario', ''))
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Guardar Cambios"):
                                datos_actualizados = {
                                    "nombre": nuevo_nombre,
                                    "tipo": nuevo_tipo,
                                    "direccion": nueva_direccion,
                                    "latitud": nueva_lat,
                                    "longitud": nueva_lon,
                                    "telefono": nuevo_telefono,
                                    "email": c.get('email', ''),
                                    "horario": nuevo_horario
                                }
                                r = requests.put(f"{API_URL}/comercios/{c.get('id')}", json=datos_actualizados)
                                if r.status_code == 200:
                                    st.success("✅ Comercio actualizado.")
                                    st.session_state[f'editar_comercio_{c.get("id")}'] = False
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(f"Error al actualizar: {r.text}")
                        
                        with col2:
                            if st.form_submit_button("❌ Cancelar"):
                                st.session_state[f'editar_comercio_{c.get("id")}'] = False
                                st.rerun()
    else:
        st.info("No hay comercios registrados.")

def crud_promos():
    st.subheader("🎯 Gestión de Promociones")
    promociones = get_promociones()
    comercios = get_comercios()

    if not comercios or not isinstance(comercios, list):
        st.warning("Primero cargá comercios para asociar promociones.")
        return

    with st.expander("➕ Agregar promoción"):
        with st.form("form_promo"):
            nombre = st.text_input("Nombre*")
            desc = st.text_area("Descripción*")
            precio = st.number_input("Precio*", min_value=0.0, step=100.0)
            categoria = st.selectbox("Categoría*", ["gluten_free", "vegano", "sin_lactosa", "organico", "bajo_sodio"])
            comercio_id = st.selectbox("Comercio*", [c["id"] for c in comercios if isinstance(c, dict)],
                                       format_func=lambda x: next((c["nombre"] for c in comercios if c["id"] == x), str(x)))

            if st.form_submit_button("💾 Guardar Promoción"):
                promo = {"nombre": nombre, "descripcion": desc, "precio": precio,
                         "categoria": categoria, "comercio_id": comercio_id}
                r = requests.post(f"{API_URL}/promociones/", json=promo)
                if r.status_code == 201:
                    st.success("✅ Promoción creada.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"Error al guardar: {r.text}")

    if promociones and isinstance(promociones, list):
        st.write("### 📋 Promociones registradas")
        for p in promociones:
            if isinstance(p, dict):
                comercio_nombre = next((c["nombre"] for c in comercios if c["id"] == p.get('comercio_id')), "Comercio no encontrado")
                comercio_direccion = next((c["direccion"] for c in comercios if c["id"] == p.get('comercio_id')), "Dirección no disponible")
                
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{p.get('nombre', 'Sin nombre')}** — ${p.get('precio', '')} ({p.get('categoria', '')})")
                    st.caption(f"📌 {comercio_nombre} | {p.get('descripcion', '')}")
                    st.caption(f"📍 {comercio_direccion}")
                
                with col2:
                    if st.button(f"✏️ Editar {p.get('id', '')}", key=f"edit_promo_{p.get('id', '')}"):
                        st.session_state[f'editar_promo_{p.get("id")}'] = True
                
                with col3:
                    if st.button(f"🗑️ Eliminar {p.get('id', '')}", key=f"del_promo_{p.get('id', '')}"):
                        requests.delete(f"{API_URL}/promociones/{p.get('id', '')}")
                        time.sleep(1)
                        st.rerun()
                
                # Formulario de edición
                if st.session_state.get(f'editar_promo_{p.get("id")}', False):
                    with st.form(f"form_editar_promo_{p.get('id')}"):
                        st.write("#### ✏️ Editar Promoción")
                        nuevo_nombre = st.text_input("Nombre", value=p.get('nombre', ''))
                        nueva_desc = st.text_area("Descripción", value=p.get('descripcion', ''))
                        nuevo_precio = st.number_input("Precio", min_value=0.0, step=100.0, value=float(p.get('precio', 0)))
                        nueva_categoria = st.selectbox("Categoría", ["gluten_free", "vegano", "sin_lactosa", "organico", "bajo_sodio"],
                                                     index=["gluten_free", "vegano", "sin_lactosa", "organico", "bajo_sodio"].index(p.get('categoria', 'vegano')))
                        nuevo_comercio_id = st.selectbox("Comercio", [c["id"] for c in comercios if isinstance(c, dict)],
                                                        index=[c["id"] for c in comercios].index(p.get('comercio_id', 1)) if p.get('comercio_id') in [c["id"] for c in comercios] else 0,
                                                        format_func=lambda x: next((c["nombre"] for c in comercios if c["id"] == x), str(x)))
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Guardar Cambios"):
                                datos_actualizados = {
                                    "nombre": nuevo_nombre,
                                    "descripcion": nueva_desc,
                                    "precio": nuevo_precio,
                                    "categoria": nueva_categoria,
                                    "comercio_id": nuevo_comercio_id
                                }
                                r = requests.put(f"{API_URL}/promociones/{p.get('id')}", json=datos_actualizados)
                                if r.status_code == 200:
                                    st.success("✅ Promoción actualizada.")
                                    st.session_state[f'editar_promo_{p.get("id")}'] = False
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(f"Error al actualizar: {r.text}")
                        
                        with col2:
                            if st.form_submit_button("❌ Cancelar"):
                                st.session_state[f'editar_promo_{p.get("id")}'] = False
                                st.rerun()
    else:
        st.info("No hay promociones cargadas.")

if __name__ == "__main__":
    main()

