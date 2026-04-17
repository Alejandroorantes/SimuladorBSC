import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import google.generativeai as genai

# ==========================================
# 1. CONFIGURACIÓN DE IA (GEMINI) - CORREGIDA
# ==========================================
# Reemplaza con tu llave de Google AI Studio
API_KEY = "AQ.Ab8RN6JbuRr2l-2IUw-qVas7zG0n2sOmSZv2M3IJY-G6y-qRag" 

# Configuración robusta para evitar el error 401
try:
    genai.configure(api_key=API_KEY)
    # Forzamos al modelo a usar la configuración de la API Key
    model = genai.GenerativeModel(model_name='gemini-3-flash')
    ia_disponible = True
except Exception as e:
    ia_disponible = False
    error_config = str(e)

# Configuración de página
st.set_page_config(page_title="Simulador Estratégico Alex", layout="wide")

# --- MOTOR DE COHERENCIA (Lógica Interna) ---
def calcular_modificador(texto_diagnostico, accion_nombre):
    texto = texto_diagnostico.lower()
    keywords = {
        "1. Automatización Robótica (RPA/AI)": ["procesos", "eficiencia", "operación", "manual", "lento"],
        "2. Programa de Lealtad Omnicanal": ["clientes", "nps", "fidelidad", "ventas", "servicio"],
        "3. I+D: Productos Sustentables": ["innovacion", "producto", "verde", "sustentable", "desarrollo"],
        "4. Reskilling de Talento Digital": ["talento", "capacitacion", "gente", "personas", "habilidades"],
        "5. Expansión de Mercados": ["crecimiento", "mercado", "global", "ventas", "socios"],
        "6. Smart Logistics": ["logistica", "entrega", "inventario", "cadena", "transporte"],
        "7. Ciberseguridad": ["riesgo", "seguridad", "datos", "ataque", "nube"]
    }
    if any(word in texto for word in keywords.get(accion_nombre, [])):
        return 1.2
    return 1.0

def obtener_recomendacion_ia(datos, estrategia):
    # Prompt optimizado para análisis estructural
    prompt = f"""
    Actúa como un Consultor de Estrategia Senior. Analiza este modelo de negocio:
    EMPRESA: {datos['empresa']} ({datos['industria']})
    ARQUITECTURA: Valor: {datos['vp']}, Procesos: {datos['proc']}, Recursos: {datos['recursos']}, Socios: {datos['socios']}
    FODA: Fortalezas: {datos['fort']}, Oportunidades: {datos['opp']}, Debilidades: {datos['deb']}, Amenazas: {datos['ame']}
    ESTRATEGIA: Jugar en {estrategia['donde']} y ganar mediante {estrategia['como']}
    
    TAREA: Da un diagnóstico de coherencia y menciona 2 puntos ciegos estratégicos.
    """
    try:
        # Importante: No pasar parámetros de seguridad si no es necesario para evitar conflictos de tokens
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Error técnico real: {str(e)}"

# ==========================================
# 2. INICIALIZACIÓN DE ESTADO
# ==========================================
if 'paso' not in st.session_state:
    st.session_state.paso = 1
    st.session_state.presupuesto = 20.0
    st.session_state.historial = []
    st.session_state.ultimo_impacto = None
    st.session_state.datos_f1 = {}
    st.session_state.kpis = {
        "Financiera": {"ROI": {"actual": 8.0, "ideal": 15.0}, "Margen EBITDA": {"actual": 12.0, "ideal": 18.0}},
        "Clientes": {"Satisfacción (NPS)": {"actual": 65.0, "ideal": 90.0}, "Cuota Mercado": {"actual": 15.0, "ideal": 25.0}},
        "Procesos": {"Eficiencia OEE": {"actual": 70.0, "ideal": 90.0}, "Tiempo Ciclo": {"actual": 15.0, "ideal": 8.0}},
        "Aprendizaje": {"Índice Innovación": {"actual": 3.0, "ideal": 9.0}, "Capacitación": {"actual": 20.0, "ideal": 55.0}}
    }

DECISIONES = {
    "1. Automatización Robótica (RPA/AI)": {"costo": 5.5, "impacto": {"Procesos": {"Eficiencia OEE": 12.0, "Tiempo Ciclo": -3.0}, "Financiera": {"Margen EBITDA": 2.5}}},
    "2. Programa de Lealtad Omnicanal": {"costo": 3.5, "impacto": {"Clientes": {"Satisfacción (NPS)": 18.0, "Cuota Mercado": 4.0}, "Financiera": {"Margen EBITDA": -0.5}}},
    "3. I+D: Productos Sustentables": {"costo": 6.5, "impacto": {"Aprendizaje": {"Índice Innovación": 5.0}, "Clientes": {"Cuota Mercado": 6.0}, "Financiera": {"ROI": -1.5}}},
    "4. Reskilling de Talento Digital": {"costo": 2.5, "impacto": {"Aprendizaje": {"Capacitación": 25.0, "Índice Innovación": 2.0}, "Procesos": {"Eficiencia OEE": 4.0}}},
    "5. Expansión de Mercados": {"costo": 7.5, "impacto": {"Clientes": {"Cuota Mercado": 10.0}, "Financiera": {"ROI": 4.0}, "Procesos": {"Tiempo Ciclo": 2.0}}},
    "6. Smart Logistics": {"costo": 4.0, "impacto": {"Procesos": {"Tiempo Ciclo": -4.0}, "Financiera": {"Margen EBITDA": 3.0}}},
    "7. Ciberseguridad": {"costo": 3.0, "impacto": {"Procesos": {"Eficiencia OEE": 5.0}, "Aprendizaje": {"Índice Innovación": 1.0}}}
}

# ==========================================
# 3. NAVEGACIÓN Y FASES
# ==========================================

# FASE 1: DIAGNÓSTICO
if st.session_state.paso == 1:
    st.title("Fase 1: Diagnóstico Integral")
    with st.form("f1_form"):
        empresa_in = st.text_input("Nombre de la Empresa:")
        industria_in = st.selectbox("Industria:", ["Manufactura", "Servicios", "Tecnología", "Retail"])
        
        st.subheader("I. Arquitectura de Negocio (Canvas)")
        c1, c2 = st.columns(2)
        with c1:
            vp = st.text_area("Propuesta de Valor:")
            proc = st.text_area("Procesos Clave:")
        with c2:
            recursos = st.text_area("Recursos Clave:")
            socios = st.text_area("Socios Clave:")
            
        st.subheader("II. Análisis FODA")
        f1, f2 = st.columns(2)
        with f1:
            fort = st.text_area("Fortalezas:"); opp = st.text_area("Oportunidades:")
        with f2:
            deb = st.text_area("Debilidades:"); ame = st.text_area("Amenazas:")
            
        if st.form_submit_button("Siguiente"):
            if empresa_in:
                st.session_state.datos_f1 = {
                    "empresa": empresa_in, "industria": industria_in,
                    "vp": vp, "proc": proc, "recursos": recursos, "socios": socios,
                    "fort": fort, "opp": opp, "deb": deb, "ame": ame
                }
                st.session_state.paso = 2
                st.rerun()
            else: st.error("Ingresa el nombre de la empresa")

# FASE 2: ESTRATEGIA
elif st.session_state.paso == 2:
    st.title("Fase 2: Estrategia Play to Win")
    with st.form("f2_form"):
        donde = st.text_input("¿Dónde jugar?")
        como = st.text_input("¿Cómo ganar?")
        if st.form_submit_button("Iniciar Simulador"):
            st.session_state.donde = donde
            st.session_state.como = como
            st.session_state.paso = 3
            st.rerun()

# FASE 3: SIMULADOR
elif st.session_state.paso == 3:
    st.title(f"Simulador: {st.session_state.datos_f1['empresa']}")
    col_vis, col_ctrl = st.columns([2, 1])

    with col_vis:
        t_matriz, t_gap, t_ia = st.tabs(["📋 BSC", "📊 Gaps", "🤖 CONSULTORÍA IA"])
        with t_matriz:
            rows = [{"Perspectiva": p, "KPI": k, "Actual": d['actual'], "Meta": d['ideal']} for p, ks in st.session_state.kpis.items() for k, d in ks.items()]
            st.table(pd.DataFrame(rows))
        with t_gap:
            labels = [k for p, ks in st.session_state.kpis.items() for k in ks]
            vals = [d['actual'] for p, ks in st.session_state.kpis.items() for d in ks.values()]
            targets = [d['ideal'] for p, ks in st.session_state.kpis.items() for d in ks.values()]
            fig, ax = plt.subplots(figsize=(10, 4))
            x = np.arange(len(labels))
            ax.bar(x - 0.2, vals, 0.4, label='Actual', color='#007bff')
            ax.bar(x + 0.2, targets, 0.4, label='Meta', color='#e9ecef')
            ax.set_xticks(x); ax.set_xticklabels(labels, rotation=45); ax.legend()
            st.pyplot(fig)
        with t_ia:
            st.subheader("Consultoría Estratégica con Gemini")
            if st.button("Obtener Validación de la IA"):
                with st.spinner("Analizando modelo de negocio..."):
                    estr = {"donde": st.session_state.donde, "como": st.session_state.como}
                    feedback = obtener_recomendacion_ia(st.session_state.datos_f1, estr)
                    st.markdown(feedback)

    with col_ctrl:
        st.subheader("Simulación")
        st.metric("Presupuesto", f"${round(st.session_state.presupuesto, 2)}M")
        sel = st.selectbox("Elegir Iniciativa Estratégica:", list(DECISIONES.keys()))
        if st.button("Ejecutar Inversión", use_container_width=True):
            info = DECISIONES[sel]
            if st.session_state.presupuesto >= info['costo']:
                diag_total = " ".join(str(v) for v in st.session_state.datos_f1.values())
                mod = calcular_modificador(diag_total, sel)
                st.session_state.presupuesto -= info['costo']
                for p, ks in info['impacto'].items():
                    for k, v in ks.items():
                        st.session_state.kpis[p][k]['actual'] = round(st.session_state.kpis[p][k]['actual'] + (v * mod), 2)
                st.session_state.historial.append({"Acción": sel, "Costo": info['costo'], "Coherencia": "Bono Aplicado" if mod > 1 else "Normal"})
                st.rerun()
        
        st.divider()
        if st.button("📊 GENERAR REPORTE FINAL", type="primary", use_container_width=True):
            st.session_state.paso = 4
            st.rerun()
        if st.button("🔄 Reiniciar Simulación"):
            st.session_state.clear()
            st.rerun()

# FASE 4: REPORTE
elif st.session_state.paso == 4:
    st.title("Reporte Estratégico Final")
    d = st.session_state.datos_f1
    
    st.subheader("I. Resumen del Diagnóstico Inicial")
    ra, rb = st.columns(2)
    with ra:
        st.markdown("**Arquitectura (Canvas)**")
        st.info(f"**Valor:** {d['vp']}\n\n**Procesos:** {d['proc']}\n\n**Recursos:** {d['recursos']}\n\n**Socios:** {d['socios']}")
    with rb:
        st.markdown("**FODA**")
        st.warning(f"**Fortalezas:** {d['fort']}\n\n**Oportunidades:** {d['opp']}\n\n**Debilidades:** {d['deb']}\n\n**Amenazas:** {d['ame']}")
    
    st.divider()
    st.subheader("II. Estrategia y Desempeño")
    st.success(f"**Estrategia Definida:** {st.session_state.como} en {st.session_state.donde}")
    
    f_rows = [{"KPI": k, "Resultado Final": d['actual'], "Meta": d['ideal']} for p, ks in st.session_state.kpis.items() for k, d in ks.items()]
    st.table(pd.DataFrame(f_rows))
    
    st.subheader("III. Bitácora de Inversiones")
    st.table(pd.DataFrame(st.session_state.historial))
    
    if st.button("Volver al Tablero"):
        st.session_state.paso = 3
        st.rerun()
