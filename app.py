import streamlit as st
import pandas as pd
import sqlite3

# --- 1. CONFIGURACIÓN Y BASE DE DATOS ---
st.set_page_config(page_title="Sorteo UDLAP - Eduardo Galván", layout="centered")

# Crear conexión a SQLite (se crea el archivo si no existe)
conn = sqlite3.connect('sorteo_udlap.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute('''
        CREATE TABLE IF NOT EXISTS boletos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            talonario TEXT,
            boleto TEXT UNIQUE,
            estatus TEXT,
            comprador TEXT,
            whatsapp TEXT,
            metodo_pago TEXT,
            pagado REAL
        )
    ''')
    # Insertar los 33 boletos si la tabla está vacía
    c.execute("SELECT COUNT(*) FROM boletos")
    if c.fetchone()[0] == 0:
        talonarios = {
            "05859": ["008339", "042760", "083771", "100942", "123033", "175534", "188395", "217616", "253197", "275868", "308749"],
            "05860": ["005160", "045631", "068092", "116623", "140024", "155585", "193196", "206687", "263248", "264369", "295310"],
            "05861": ["003581", "058082", "070943", "101164", "137745", "160416", "194297", "210538", "237129", "272470", "298911"]
        }
        for tal, boletos in talonarios.items():
            for bol in boletos:
                c.execute("INSERT INTO boletos (talonario, boleto, estatus, comprador, whatsapp, metodo_pago, pagado) VALUES (?, ?, 'Disponible', '', '', '', 0)", 
                          (tal, bol))
        conn.commit()

init_db()

# --- 2. VISTA PÚBLICA (Para tus clientes) ---
def vista_publica():
    st.image("https://www.udlap.mx/sorteo/assets/img/logo-sorteo-udlap.png", width=200) # Logo de ejemplo
    st.title("🍀 Gran Sorteo UDLAP")
    st.markdown("""
    **¡Gánate una residencia de $34 Millones, un Porsche Macan o un BMW!**
    Apóyame a mantener mi beca de Actuaría adquiriendo tu boleto. Costo: **$720 MXN**.
    """)
    
    # Consultar boletos disponibles
    df_disponibles = pd.read_sql("SELECT boleto FROM boletos WHERE estatus='Disponible'", conn)
    boletos_lista = df_disponibles['boleto'].tolist()
    
    if not boletos_lista:
        st.error("¡Se han agotado todos los boletos! Muchas gracias por tu apoyo.")
        return

    with st.form("registro_boleto"):
        nombre = st.text_input("Tu Nombre Completo *")
        whatsapp = st.text_input("Tu WhatsApp *")
        boletos_select = st.multiselect("Selecciona los boletos que quieres apartar *", boletos_lista)
        metodo = st.radio("¿Cómo prefieres pagarlo? *", 
                          ["De contado ($720)", "Plan 3 Quincenas (Enganche $120 + 2 pagos de $300)"])
        
        submit = st.form_submit_button("¡Apartar mis boletos!")
        
        if submit:
            if nombre and whatsapp and boletos_select:
                for b in boletos_select:
                    c.execute("UPDATE boletos SET estatus='Apartado', comprador=?, whatsapp=?, metodo_pago=? WHERE boleto=?", 
                              (nombre, whatsapp, metodo, b))
                conn.commit()
                st.success(f"¡Gracias {nombre}! Tus boletos han sido apartados. Te contactaré por WhatsApp para los detalles de pago.")
                st.balloons()
            else:
                st.warning("Por favor, llena todos los campos obligatorios.")

# --- 3. VISTA PRIVADA (Tu CRM / Panel de Control) ---
def vista_admin():
    st.title("⚙️ Panel de Administración")
    password = st.text_input("Contraseña de acceso", type="password")
    
    if password == "udlap2026": # ¡Cambia esta contraseña!
        st.success("Acceso concedido.")
        
        # Dashboard Rápido
        df = pd.read_sql("SELECT * FROM boletos", conn)
        total_recaudado = df['pagado'].sum()
        boletos_vendidos = len(df[df['estatus'].isin(['Apartado', 'Pagado Total'])])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Dinero Recaudado", f"${total_recaudado:,.2f}")
        col2.metric("Boletos Colocados", f"{boletos_vendidos} / 30")
        col3.metric("Faltante para Meta", f"${21600 - total_recaudado:,.2f}")
        
        st.subheader("Gestión de Boletos y Pagos")
        
        # Filtro
        filtro_estatus = st.selectbox("Filtrar por estatus", ["Todos", "Disponible", "Apartado", "Pagado Total"])
        if filtro_estatus != "Todos":
            df = df[df['estatus'] == filtro_estatus]
            
        st.dataframe(df[['talonario', 'boleto', 'estatus', 'comprador', 'metodo_pago', 'pagado']], use_container_width=True)
        
        # Módulo de Cobranza (Actualizar pagos)
        st.subheader("💰 Registrar Pago / Abono")
        with st.form("actualizar_pago"):
            boleto_a_pagar = st.selectbox("Selecciona el boleto", df[df['estatus'] != 'Disponible']['boleto'].tolist())
            monto_abono = st.number_input("Monto a abonar", min_value=0.0, step=50.0)
            
            if st.form_submit_button("Registrar Cobro"):
                if boleto_a_pagar:
                    # Obtener pago actual
                    c.execute("SELECT pagado FROM boletos WHERE boleto=?", (boleto_a_pagar,))
                    pagado_actual = c.fetchone()[0]
                    nuevo_pago = pagado_actual + monto_abono
                    
                    nuevo_estatus = "Pagado Total" if nuevo_pago >= 720 else "Apartado"
                    
                    c.execute("UPDATE boletos SET pagado=?, estatus=? WHERE boleto=?", (nuevo_pago, nuevo_estatus, boleto_a_pagar))
                    conn.commit()
                    st.success(f"Cobro registrado. Total pagado de este boleto: ${nuevo_pago}")
                    st.rerun()

# --- 4. CONTROLADOR DE VISTAS ---
st.sidebar.title("Navegación")
opcion = st.sidebar.radio("Ir a:", ["Registro Público", "Acceso Admin (Eduardo)"])

if opcion == "Registro Público":
    vista_publica()
else:
    vista_admin()