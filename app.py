import streamlit as st
import pandas as pd
import sqlite3

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Sorteo UDLAP | Gana una Residencia", layout="centered", initial_sidebar_state="collapsed")

# --- 2. INYECCIÓN DE CSS FRONTEND ---
def aplicar_diseno():
    css_magico = """
    <style>
    /* Importar tipografías */
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@700;900&family=Montserrat:wght@400;600&display=swap');

    /* Variables de Color y Tipografía Global */
    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
        color: #4A4A4A; /* Gris asfalto para legibilidad */
    }
    h1, h2, h3, .price {
        font-family: 'Nunito', sans-serif !important;
    }

    /* Color Principal (Azul cielo) + Patrón de Tréboles (SVG embebido al 5% opacidad) */
    .stApp {
        background-color: #E3F2FD; 
        background-image: url('data:image/svg+xml;utf8,<svg width="60" height="60" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><text y="50" font-size="25" fill="%23000000" opacity="0.05">🍀</text></svg>');
    }

    /* Color de Acción (Naranja Vibrante) para botones CTA */
    .stButton > button {
        background-color: #FF6600 !important;
        color: #FFFFFF !important;
        border-radius: 30px !important;
        font-weight: 900 !important;
        border: none !important;
        font-family: 'Nunito', sans-serif !important;
        font-size: 1.3rem !important;
        padding: 10px 25px !important;
        width: 100%;
        box-shadow: 0 8px 20px rgba(255, 102, 0, 0.4);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #E65C00 !important;
        transform: translateY(-3px);
        box-shadow: 0 12px 25px rgba(255, 102, 0, 0.5);
    }

    /* Tarjetas de Exhibición de Autos (Fondo Oscuro Neutro) */
    .car-card {
        background-color: #242424;
        background-image: linear-gradient(145deg, #242424, #1a1a1a);
        color: white;
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        border-top: 3px solid #FF6600;
    }
    .car-card h3 {
        color: #FFFFFF;
        margin-bottom: 5px;
        font-size: 1.5rem;
    }
    .car-card p {
        color: #A0A0A0;
        font-size: 0.9rem;
    }

    /* Colores Secundarios para detalles (Mascota) */
    .highlight-green { color: #2E8B57; font-weight: bold; }
    .highlight-blue { color: #4169E1; font-weight: bold; }

    /* Efecto Parallax suave de Billetes Cayendo */
    @keyframes falling {
        0% { transform: translateY(-10vh) rotate(0deg); opacity: 0; }
        10% { opacity: 0.6; }
        90% { opacity: 0.6; }
        100% { transform: translateY(110vh) rotate(360deg); opacity: 0; }
    }
    .billete {
        position: fixed;
        font-size: 28px;
        z-index: 0;
        animation: falling 7s linear infinite;
        pointer-events: none;
    }
    .b1 { left: 15%; animation-duration: 8s; animation-delay: 0s; }
    .b2 { left: 85%; animation-duration: 6s; animation-delay: 2s; }
    .b3 { left: 50%; animation-duration: 9s; animation-delay: 4s; }
    </style>
    """
    st.markdown(css_magico, unsafe_allow_html=True)
    # Inyectar billetes
    st.markdown('''
        <div class="billete b1">💸</div>
        <div class="billete b2">💵</div>
        <div class="billete b3">💸</div>
    ''', unsafe_allow_html=True)

# --- 3. BASE DE DATOS ---
conn = sqlite3.connect('sorteo_udlap.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute('''CREATE TABLE IF NOT EXISTS boletos 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, talonario TEXT, boleto TEXT UNIQUE, 
                 estatus TEXT, comprador TEXT, whatsapp TEXT, metodo_pago TEXT, pagado REAL)''')
    c.execute("SELECT COUNT(*) FROM boletos")
    if c.fetchone()[0] == 0:
        talonarios = {
            "05859": ["008339", "042760", "083771", "100942", "123033", "175534", "188395", "217616", "253197", "275868", "308749"],
            "05860": ["005160", "045631", "068092", "116623", "140024", "155585", "193196", "206687", "263248", "264369", "295310"],
            "05861": ["003581", "058082", "070943", "101164", "137745", "160416", "194297", "210538", "237129", "272470", "298911"]
        }
        for tal, boletos in talonarios.items():
            for bol in boletos:
                c.execute("INSERT INTO boletos (talonario, boleto, estatus, comprador, whatsapp, metodo_pago, pagado) VALUES (?, ?, 'Disponible', '', '', '', 0)", (tal, bol))
        conn.commit()

init_db()

# --- 4. VISTA PÚBLICA (LANDING PAGE) ---
def vista_publica():
    aplicar_diseno()
    
    # Hero Section
    st.markdown('<h1 style="text-align: center; color: #1F4E78; font-size: 2.5rem; margin-bottom: 0;">Cuadragésimo Sorteo UDLAP</h1>', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; color: #FF6600; font-size: 2rem;">Boleto: $720 MXN</h2>', unsafe_allow_html=True)
    st.markdown("""
    <p style="text-align: center; font-size: 1.1rem;">
    Participa por una <b>Residencia de $34,000,000 MXN totalmente amueblada</b>.<br>
    Al asegurar tu lugar, me apoyas directamente a mantener mi beca para continuar mi carrera. ¡El Sorteo es el 21 de Noviembre!
    </p>
    """, unsafe_allow_html=True)

    # Exhibición de Autos (Imagen Premium con CSS)
    # OJO: Para que esto funcione en la nube, es mejor que subas la foto a internet y pegues aquí el link (URL)
    url_imagen = "https://i.postimg.cc/wB3rMjmF/premios-sorteo-jpg.jpg" # <- Cambia este link por el de tu imagen
    
    st.markdown(f'''
    <div style="text-align: center; margin-bottom: 30px;">
        <img src="{url_imagen}" style="width: 100%; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); border-top: 3px solid #FF6600;">
    </div>
    ''', unsafe_allow_html=True)

    # Formulario
    st.markdown("### 👇 Asegura tu boleto ahora")
    df_disponibles = pd.read_sql("SELECT boleto FROM boletos WHERE estatus='Disponible'", conn)
    boletos_lista = df_disponibles['boleto'].tolist()
    
    if not boletos_lista:
        st.error("¡Se han agotado todos los boletos! Muchas gracias por tu apoyo.")
        return

    with st.form("registro_boleto"):
        nombre = st.text_input("Tu Nombre Completo")
        whatsapp = st.text_input("Tu WhatsApp")
        boletos_select = st.multiselect("¿Qué números te dan más suerte?", boletos_lista)
        metodo = st.radio("Método de pago preferido", 
                          ["Pago Único (Transferencia $720)", "Plan 3 Quincenas (Enganche $120 + 2 de $300)"])
        
        submit = st.form_submit_button("¡COMPRAR MI BOLETO!")
        
        if submit:
            if nombre and whatsapp and boletos_select:
                for b in boletos_select:
                    c.execute("UPDATE boletos SET estatus='Apartado', comprador=?, whatsapp=?, metodo_pago=? WHERE boleto=?", 
                              (nombre, whatsapp, metodo, b))
                conn.commit()
                st.success(f"¡Éxito {nombre}! Tus números están apartados. Te enviaré un WhatsApp en unos minutos.")
                st.balloons()
            else:
                st.warning("Por favor, llena tus datos para apartar tus boletos.")

# --- 5. VISTA PRIVADA ---
def vista_admin():
    st.title("⚙️ Panel de Administración")
    
    # Iniciar la variable de estado si no existe
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False

    # Si no está autenticado, mostrar la caja de contraseña
    if not st.session_state['autenticado']:
        password = st.text_input("Contraseña de acceso", type="password")
        if st.button("Entrar"):
            # AQUÍ VALIDAMOS CON st.secrets COMO ACORDAMOS
            if password == st.secrets["admin_password"]: 
                st.session_state['autenticado'] = True
                st.rerun() # Recargar la página para que desaparezca la caja de contraseña
            else:
                st.error("Contraseña incorrecta.")
    
    # Si ya está autenticado, mostrar el panel
    if st.session_state['autenticado']:
        st.success("Acceso concedido.")
        
        # Botón para cerrar sesión (Opcional, pero recomendado)
        if st.button("Cerrar Sesión"):
            st.session_state['autenticado'] = False
            st.rerun()

        df = pd.read_sql("SELECT * FROM boletos", conn)
        total_recaudado = df['pagado'].sum()
        boletos_vendidos = len(df[df['estatus'].isin(['Apartado', 'Pagado Total'])])
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Dinero Recaudado", f"${total_recaudado:,.2f}")
        c2.metric("Boletos Colocados", f"{boletos_vendidos} / 30")
        c3.metric("Faltante", f"${21600 - total_recaudado:,.2f}")
        
        st.dataframe(df[['talonario', 'boleto', 'estatus', 'comprador', 'pagado']], use_container_width=True)
        
        st.subheader("💰 Registrar Cobro")
        with st.form("actualizar_pago"):
            boleto_a_pagar = st.selectbox("Selecciona el boleto", df[df['estatus'] != 'Disponible']['boleto'].tolist())
            monto_abono = st.number_input("Monto a abonar", min_value=0.0, step=50.0)
            if st.form_submit_button("Registrar"):
                if boleto_a_pagar:
                    pagado_actual = c.execute("SELECT pagado FROM boletos WHERE boleto=?", (boleto_a_pagar,)).fetchone()[0]
                    nuevo_pago = pagado_actual + monto_abono
                    nuevo_estatus = "Pagado Total" if nuevo_pago >= 720 else "Apartado"
                    c.execute("UPDATE boletos SET pagado=?, estatus=? WHERE boleto=?", (nuevo_pago, nuevo_estatus, boleto_a_pagar))
                    conn.commit()
                    st.success("Cobro registrado.")
                    st.rerun()

# --- 6. NAVEGADOR ---
opcion = st.sidebar.radio("Menú", ["Sorteo (Público)", "Admin (Privado)"])
if opcion == "Sorteo (Público)":
    vista_publica()
else:
    vista_admin()