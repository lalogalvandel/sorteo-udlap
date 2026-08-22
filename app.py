import streamlit as st
import pandas as pd
import psycopg2

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Sorteo UDLAP | Lalo Galván", layout="centered", initial_sidebar_state="collapsed")

# Metas del panel de administración
META_BOLETOS = 30
META_MONTO = 21600

# --- 2. INYECCIÓN DE CSS FRONTEND (Se llama de inmediato para evitar parpadeos) ---
def aplicar_diseno():
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap');

    :root {
        --ink: #262920;
        --green: #1E3A2D;
        --green-deep: #142A20;
        --gold: #9C6428;
        --gold-soft: #C99958;
        --paper: #FBFAF6;
        --card: #FFFFFF;
        --line: #E4E0D3;
        --muted: #726D5F;
    }

    /* 1. BLINDAJE ANTI-MODO OSCURO */
    html, body, [class*="css"], .stApp { 
        font-family: 'Inter', sans-serif; 
        background-color: var(--paper) !important;
        color: var(--ink) !important;
    }
    .block-container { max-width: 760px; padding-top: 2.4rem; padding-bottom: 4rem; }

    p, span, label, li { color: var(--ink); }
    /* Se quitó el !important del color para no chocar con la tarjeta Hero */
    h1, h2, h3 { font-family: 'Source Serif 4', serif !important; color: var(--green); font-weight: 600 !important; }

    /* 2. CORRECCIÓN FLECHITA LATERAL: Ocultar basura visual, pero mantener flecha de menú */
    #MainMenu, footer, .stDeployButton {
        display: none !important;
        visibility: hidden !important;
    }
    header { background: transparent !important; }

    /* ---------- Hero / letterhead (CORRECCIÓN DE COLORIMETRÍA) ---------- */
    .hero {
        background: linear-gradient(165deg, var(--green) 0%, var(--green-deep) 100%);
        border-radius: 8px; padding: 2.5rem 2rem 2.1rem; text-align: center; margin-bottom: 1.6rem;
        box-shadow: 0 10px 30px rgba(20,42,32,0.2);
    }
    .hero .eyebrow {
        font-family: 'IBM Plex Mono', monospace; letter-spacing: 0.16em; font-size: 0.72rem;
        color: var(--gold-soft); text-transform: uppercase; margin-bottom: 0.9rem;
    }
    .hero h1 { color: #FFFFFF !important; font-size: 2.2rem !important; margin: 0 0 0.7rem !important; line-height: 1.18; }
    .hero .rule { width: 38px; height: 1px; background: var(--gold-soft); margin: 0 auto 0.7rem; opacity: 0.65; }
    .hero .meta { font-family: 'IBM Plex Mono', monospace; color: #F6F1E4 !important; font-size: 0.95rem; opacity: 0.92; }

    .teaser { text-align: center; color: var(--muted); font-size: 1.05rem; line-height: 1.6; margin: 0 0 1.8rem; }
    .teaser b { color: var(--ink); font-weight: 600; }

    /* ---------- Bio card ---------- */
    .bio-card {
        background: var(--card) !important; border: 1px solid var(--line); border-left: 4px solid var(--green);
        padding: 1.6rem 1.8rem; border-radius: 6px; margin-bottom: 2.2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.02);
    }
    .bio-card p { line-height: 1.68; margin: 0; font-size: 1.05rem; color: var(--ink) !important; }
    .bio-card .firma { font-family: 'Source Serif 4', serif; font-style: italic; color: var(--green) !important; font-size: 1.1rem; display: block; margin-top: 1rem; }

    /* ---------- Section headers ---------- */
    .section-label {
        font-family: 'IBM Plex Mono', monospace; letter-spacing: 0.14em; text-transform: uppercase;
        font-size: 0.75rem; color: var(--muted); text-align: center; margin: 0 0 0.35rem;
    }
    .section-title { font-family: 'Source Serif 4', serif; text-align: center; color: var(--green); font-size: 1.6rem; margin: 0 0 1.5rem; font-weight: 600; }

    /* ---------- Prize cards ---------- */
    .prize-card { border-radius: 8px; padding: 1.5rem 1.4rem; height: 100%; box-shadow: 0 8px 20px rgba(0,0,0,0.06); }
    .prize-card.tier-1 { background: linear-gradient(165deg, var(--green) 0%, var(--green-deep) 100%); }
    .prize-card.tier-2 { background: #fff !important; border: 1px solid var(--line); }
    
    .prize-card .rank { font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; letter-spacing: 0.12em; text-transform: uppercase; }
    
    .prize-card.tier-1 h4, .prize-card.tier-1 p, .prize-card.tier-1 span, .prize-card.tier-1 li { color: #FFFFFF !important; }
    .prize-card.tier-1 .rank, .prize-card.tier-1 .value { color: var(--gold-soft) !important; }
    
    .prize-card.tier-2 h4 { color: var(--green) !important; }
    .prize-card.tier-2 p, .prize-card.tier-2 span, .prize-card.tier-2 li { color: var(--ink) !important; }
    .prize-card.tier-2 .rank, .prize-card.tier-2 .value { color: var(--gold) !important; }
    
    .prize-card h4 { font-family: 'Source Serif 4', serif; font-size: 1.15rem; margin: 0.55rem 0 0.15rem; font-weight: 600; }
    .prize-card .sub { font-size: 0.86rem; opacity: 0.85; display: block; margin-bottom: 0.5rem; }
    .prize-card ul { margin: 0.5rem 0; padding-left: 1.05rem; font-size: 0.95rem; line-height: 1.55; }
    .prize-card .value { font-family: 'IBM Plex Mono', monospace; font-weight: 600; margin-top: 0.8rem; display: block; font-size: 1rem; }

    /* ---------- Data tables ---------- */
    .data-table { width: 100%; border-collapse: collapse; font-size: 0.95rem; margin: 0.3rem 0 0.6rem; }
    .data-table th {
        text-align: left; font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; letter-spacing: 0.08em;
        text-transform: uppercase; color: var(--muted); border-bottom: 1px solid var(--line); padding: 0.6rem;
    }
    .data-table td { padding: 0.6rem; border-bottom: 1px solid var(--line); color: var(--ink) !important; }
    .data-table td.num { font-family: 'IBM Plex Mono', monospace; white-space: nowrap; font-weight: 600; color: var(--green) !important; }

    /* ---------- Legal / mechanics ---------- */
    .legal-block { margin-bottom: 1.2rem; }
    .legal-block .lbl { font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--gold); display: block; margin-bottom: 0.3rem; }
    .legal-block p { font-size: 0.95rem; line-height: 1.6; margin: 0; color: var(--ink) !important; }

    /* ---------- Buttons ---------- */
    .stButton > button, [data-testid="stFormSubmitButton"] > button {
        background: var(--green) !important; border: none !important;
        border-radius: 6px !important; width: 100%; box-shadow: 0 4px 10px rgba(30,58,45,0.2) !important;
        transition: background 0.2s ease, transform 0.1s ease;
        padding: 0.8rem 1.4rem !important;
    }
    .stButton > button p, [data-testid="stFormSubmitButton"] > button p, 
    .stButton > button div, [data-testid="stFormSubmitButton"] > button div {
        color: #FFFFFF !important; 
        font-family: 'Inter', sans-serif !important; 
        font-weight: 600 !important;
        letter-spacing: 0.02em;
        font-size: 1.1rem !important;
    }
    .stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
        background: var(--green-deep) !important; transform: translateY(-2px); box-shadow: 0 6px 15px rgba(30,58,45,0.3) !important;
    }

    /* ---------- Inputs ---------- */
    .stTextInput label p, .stNumberInput label p, .stRadio label p, .stMultiSelect label p { color: var(--green) !important; font-weight: 600; }
    .stTextInput input, .stNumberInput input { 
        border-radius: 4px !important; border-color: var(--line) !important; 
        background-color: #FFFFFF !important; color: var(--ink) !important; 
        padding: 0.6rem !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus { border-color: var(--gold) !important; box-shadow: 0 0 0 1px var(--gold) !important; }
    
    [data-baseweb="select"] { background-color: #FFFFFF !important; border-radius: 4px !important; border-color: var(--line) !important; }
    [data-baseweb="radio"] div { color: var(--ink) !important; }

    /* ---------- Expanders ---------- */
    [data-testid="stExpander"] { border: 1px solid var(--line) !important; border-radius: 6px !important; background: #FFFFFF !important; margin-bottom: 0.8rem; box-shadow: 0 2px 8px rgba(0,0,0,0.03); }
    [data-testid="stExpander"] summary { font-family: 'Source Serif 4', serif !important; color: var(--green) !important; font-weight: 600 !important; font-size: 1.1rem !important; padding: 1rem !important; }
    [data-testid="stExpander"] summary p { color: var(--green) !important; font-weight: 600 !important; font-size: 1.1rem !important;}
    [data-testid="stExpander"] div[role="region"] p, [data-testid="stExpander"] div[role="region"] li { color: var(--ink) !important; }

    /* ---------- Metrics (admin) ---------- */
    [data-testid="stMetric"] { background: #FFFFFF !important; border: 1px solid var(--line); border-radius: 6px; padding: 1rem 1.2rem; box-shadow: 0 4px 10px rgba(0,0,0,0.03); }
    [data-testid="stMetricValue"] div { font-family: 'IBM Plex Mono', monospace !important; color: var(--green) !important; font-weight: 600 !important;}
    [data-testid="stMetricLabel"] p { font-family: 'Inter', sans-serif !important; color: var(--muted) !important; font-weight: 600 !important; }

    hr { border-color: var(--line) !important; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Llama al diseño inmediatamente para que cargue con la página
aplicar_diseno()


def render_prize_table(rows):
    html = "<table class='data-table'><thead><tr><th>Lugar</th><th>Premio</th></tr></thead><tbody>"
    for lugar, premio in rows:
        html += f"<tr><td class='num'>{lugar}</td><td>{premio}</td></tr>"
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)

def render_benefit_table(rows):
    html = "<table class='data-table'><thead><tr><th>Comercio</th><th>Beneficio</th></tr></thead><tbody>"
    for negocio, beneficio in rows:
        html += f"<tr><td class='num'>{negocio}</td><td>{beneficio}</td></tr>"
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)

# --- 3. BASE DE DATOS (PostgreSQL) ---
conn = psycopg2.connect(st.secrets["db_url"])
conn.autocommit = True
c = conn.cursor()

def init_db():
    c.execute('''CREATE TABLE IF NOT EXISTS boletos 
                 (id SERIAL PRIMARY KEY, talonario TEXT, boleto TEXT UNIQUE, 
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
                c.execute("INSERT INTO boletos (talonario, boleto, estatus, comprador, whatsapp, metodo_pago, pagado) VALUES (%s, %s, 'Disponible', '', '', '', 0) ON CONFLICT DO NOTHING", (tal, bol))

init_db()

# --- 4. VISTA PÚBLICA (LANDING PAGE) ---
def vista_publica():
    st.markdown("""
    <div class="hero">
        <div class="eyebrow">Sorteo UDLAP &nbsp;·&nbsp; 40.ª edición</div>
        <h1 style="color: #E8D8B0 !important; text-shadow: 0px 2px 4px rgba(0,0,0,0.3);">Cuadragésimo Sorteo UDLAP</h1>
        <div class="rule"></div>
        <div class="meta">Boleto: $720 MXN &nbsp;·&nbsp; Sorteo: 21 de noviembre de 2026</div>
    </div>
    """, unsafe_allow_html=True)


    st.markdown("""
    <p class="teaser">Participa por una <b>residencia valuada en $34,000,000 MXN</b>, totalmente amueblada,
    además de autos y cheques en efectivo.</p>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="bio-card">
        <p>
            Soy Lalo Galván, estudiante de tercer semestre de Actuaría en la UDLAP. La venta de estos boletos
            es el requisito principal para conservar mi apoyo educativo. Al apartar el tuyo no solo participas
            por la residencia, los autos y los cheques del sorteo: me ayudas de forma directa a continuar con
            mi carrera.
            <span class="firma">Te agradezco de verdad el apoyo. — Lalo</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

    url_imagen = "https://i.postimg.cc/2jKnNdd4/premios-sorteo-jpg.png"
    st.markdown(f"""
    <div style="text-align:center; margin-bottom: 2.2rem;">
        <img src="{url_imagen}" style="width:100%; border-radius:6px; box-shadow:0 10px 26px rgba(20,42,32,0.18); border:1px solid var(--line);">
    </div>
    """, unsafe_allow_html=True)

    # --- SECCIÓN DE PREMIOS ---
    st.markdown('<div class="section-label">Premios principales</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">¿Qué te puedes ganar?</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('''
        <div class="prize-card tier-1">
            <span class="rank">1.er premio</span>
            <h4>Residencia en Lomas de Angelópolis</h4>
            <span class="sub">Completamente amueblada y decorada.</span>
            <ul>
                <li>Audi Q2</li>
                <li>Audi A1</li>
                <li>Cheque por $200,000 MXN</li>
            </ul>
            <span class="value">Valor: $20.8 millones</span>
        </div>
        ''', unsafe_allow_html=True)

    with col2:
        st.markdown('''
        <div class="prize-card tier-2">
            <span class="rank">2.º premio</span>
            <h4>Residencia en Lomas de Angelópolis</h4>
            <span class="sub">Completamente amueblada y decorada.</span>
            <ul>
                <li>Audi A1</li>
                <li>Cheque por $150,000 MXN</li>
            </ul>
            <span class="value">Valor: $12.8 millones</span>
        </div>
        ''', unsafe_allow_html=True)

    st.write("")

    with st.expander("Ver lista completa de los 250 premios"):
        render_prize_table([
            ("3.º", "$4,000,000 MXN en cheque"),
            ("4.º", "$3,000,000 MXN en cheque"),
            ("5.º", "Porsche Macan Eléctrica"),
            ("6.º", "BMW Z4"),
            ("7.º", "Audi A5"),
            ("8.º", "BMW Serie 2"),
            ("9.º", "Cupra Terramar"),
            ("10.º", "Mini Aceman"),
            ("11.º", "Buick Envista Avenir"),
            ("12.º – 13.º", "VW Jetta"),
            ("14.º – 18.º", "VW Taigun"),
            ("19.º – 40.º", "VW Polo"),
            ("41.º – 47.º", "$150,000 MXN"),
            ("48.º – 57.º", "$100,000 MXN"),
            ("58.º – 67.º", "$50,000 MXN"),
            ("68.º – 77.º", "$20,000 MXN"),
            ("78.º – 250.º", "$10,000 MXN"),
        ])

    with st.expander("Promociones exclusivas con tu boleto"):
        st.caption("Tu boleto físico da acceso inmediato a estos beneficios en Puebla.")
        render_benefit_table([
            ("Berry Munch", "Un topping extra gratis."),
            ("Club Deportivo de Élite", "Inscripción sin costo, 20% de descuento el primer mes, fisioterapia y más."),
            ("Cosmetología Integral", "20% de descuento en faciales o masajes, 15% en depilación y en lipo sin bisturí (paquetes)."),
            ("Isabella Helados Artesanales", "Medio litro de nieve de limón gratis al comprar tu boleto en sucursal."),
            ("La Momochina", "20% de descuento en consumo, o 2 tacos y agua de 500 ml gratis si lo compras ahí."),
            ("Los Culichis Aguachiles", "Porción extra de proteína en ceviches y aguachiles; envío gratis en paquetes."),
            ("Los Pinchos Zavaleta", "2x1 en pinchos tradicionales."),
            ("Madison", "15% de descuento en tu cuenta total."),
            ("Men's Fashions", "15% de descuento en productos de línea, más 10% adicional en prendas con menos del 50% de descuento."),
            ("Papa John's", "20% de descuento sobre el precio de menú en todas las sucursales."),
            ("Picosweet", "Pikopapas o un vaso de snacks botanero totalmente gratis."),
            ("Volovanes Jaro 8", "En la compra de uno o más volovanes, te llevas uno gratis."),
        ])

    with st.expander("Mecánica y legales del sorteo"):
        st.markdown("""
        <div class="legal-block">
            <span class="lbl">Mecánica</span>
            <p>Se realizará con esferas por formación de números. Se usarán 5 ánforas: cuatro con esferas del 0
            al 9, y la quinta con esferas del 0 al 31 (emisión de 320,000 boletos). La lectura es de izquierda
            a derecha. Los premios se otorgan de mayor a menor valor (1 al 250). Si un premio cae en un boleto
            no vendido, se re-sorteará hasta tener un ganador válido de acuerdo con el Reglamento de la Ley de
            Juegos y Sorteos.</p>
        </div>
        <div class="legal-block">
            <span class="lbl">Emisión y precio</span>
            <p>320,000 boletos (312,000 físicos y 8,000 electrónicos). Precio por boleto: $720 MXN. Valor total
            de la emisión: $230,400,000.00 MXN.</p>
        </div>
        <div class="legal-block">
            <span class="lbl">Premios entregados</span>
            <p>500 premios en total: 250 a compradores y 250 a colaboradores.</p>
        </div>
        <div class="legal-block">
            <span class="lbl">Fecha y sede</span>
            <p>21 de noviembre de 2026, 12:00 horas, Auditorio Guillermo y Sofía Jenkins de la UDLAP.</p>
        </div>
        <div class="legal-block">
            <span class="lbl">Permisos SEGOB</span>
            <p>20260049PS09 y 20260048PS07. Vigencia del 12 de marzo al 21 de noviembre de 2026.</p>
        </div>
        <div class="legal-block">
            <span class="lbl">Publicación de resultados</span>
            <p>23 de noviembre de 2026, en El Universal y El Sol de Puebla.</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # --- FORMULARIO DE COMPRA ---
    st.markdown('<div class="section-label">Asegura tus números</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Aparta tu boleto</div>', unsafe_allow_html=True)
    
    df_disponibles = pd.read_sql("SELECT boleto FROM boletos WHERE estatus='Disponible'", conn)
    boletos_lista = df_disponibles['boleto'].tolist()

    if not boletos_lista:
        st.info("Por el momento no hay boletos disponibles. Gracias por tu interés y tu apoyo.")
        return

    with st.form("registro_boleto"):
        nombre = st.text_input("Tu nombre completo *")
        whatsapp = st.text_input("Tu WhatsApp *", placeholder="10 dígitos")
        boletos_select = st.multiselect("¿Qué números te dan más suerte? *", boletos_lista)
        st.caption("Cada número tiene un costo de $720 MXN. Puedes seleccionar uno o varios.")
        metodo = st.radio("Método de pago preferido *",
                          ["Pago Único (Transferencia $720)", "Plan 3 Quincenas (Enganche $120 + 2 de $300)"])

        submit = st.form_submit_button("Apartar mi boleto")

        if submit:
            if nombre and whatsapp and boletos_select:
                for b in boletos_select:
                    c.execute("UPDATE boletos SET estatus='Apartado', comprador=%s, whatsapp=%s, metodo_pago=%s WHERE boleto=%s", (nombre, whatsapp, metodo, b))
                conn.commit()
                st.success(f"Gracias, {nombre}. Tus números quedaron apartados; te escribiré por WhatsApp en unos minutos para confirmar el pago.")
            else:
                st.warning("Completa tu nombre, tu WhatsApp y al menos un número para continuar.")

# --- 5. VISTA PRIVADA (ADMINISTRADOR) ---
def vista_admin():
    st.markdown('<div class="section-label">Panel interno</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title" style="text-align: left; margin-bottom: 0.5rem;">Administración</div>', unsafe_allow_html=True)

    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False

    if not st.session_state['autenticado']:
        password = st.text_input("Contraseña de acceso", type="password")
        if st.button("Ingresar"):
            if password == st.secrets["admin_password"]:
                st.session_state['autenticado'] = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")

    if st.session_state['autenticado']:
        st.success("Acceso concedido.")

        if st.button("Cerrar sesión"):
            st.session_state['autenticado'] = False
            st.rerun()

        df = pd.read_sql("SELECT * FROM boletos", conn)
        total_recaudado = df['pagado'].sum()
        boletos_vendidos = len(df[df['estatus'].isin(['Apartado', 'Pagado Total'])])

        c1, c2, c3 = st.columns(3)
        c1.metric("Dinero recaudado", f"${total_recaudado:,.2f}")
        c2.metric("Boletos colocados", f"{boletos_vendidos} / {META_BOLETOS}")
        c3.metric("Faltante", f"${META_MONTO - total_recaudado:,.2f}")

        st.write("")
        st.dataframe(
            df[['talonario', 'boleto', 'estatus', 'comprador', 'pagado']].style.format({'pagado': '${:,.2f}'}),
            use_container_width=True
        )

        st.subheader("Registrar cobro")
        with st.form("actualizar_pago"):
            boleto_a_pagar = st.selectbox("Selecciona el boleto", df[df['estatus'] != 'Disponible']['boleto'].tolist())
            monto_abono = st.number_input("Monto a abonar", min_value=0.0, step=50.0)
            if st.form_submit_button("Registrar"):
                if boleto_a_pagar:
                    c.execute("SELECT pagado FROM boletos WHERE boleto=%s", (boleto_a_pagar,))
                    pagado_actual = c.fetchone()[0]
                    nuevo_pago = pagado_actual + monto_abono
                    nuevo_estatus = "Pagado Total" if nuevo_pago >= 720 else "Apartado"

                    c.execute("UPDATE boletos SET pagado=%s, estatus=%s WHERE boleto=%s", (nuevo_pago, nuevo_estatus, boleto_a_pagar))
                    conn.commit()
                    st.success("Cobro registrado correctamente.")
                    st.rerun()

# --- 6. NAVEGADOR ---
opcion = st.sidebar.radio("Menú", ["Sorteo (Público)", "Admin (Privado)"])
if opcion == "Sorteo (Público)":
    vista_publica()
else:
    vista_admin()

