import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import google.generativeai as genai  # Importamos la librería de Gemini

# --- CONFIGURACIÓN DE GEMINI ---
# Reemplaza 'TU_API_KEY_AQUI' con tu llave real o usa un secreto de Streamlit
API_KEY = "AQ.Ab8RN6Lv4M2Kr87aQ-Vf_4cLpRXrzKONLBeoNPzzNbqVpP-nJA" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Simulador de Estrategia Pro + IA", layout="wide")

# --- MOTOR DE COHERENCIA (Lógica Interna) ---
def calcular_modificador(texto_diagnostico, accion_nombre):
    texto = texto_diagnostico.lower()
    keywords = {
        "1. Automatización Robótica (RPA/AI)": ["procesos", "eficiencia", "costos", "manual", "lento", "operación"],
        "2. Programa de Lealtad Omnicanal": ["clientes", "nps", "fidelidad", "ventas", "servicio", "mercado"],
        "3. I+D: Productos Sustentables": ["innovacion", "producto", "verde", "sustentable", "futuro", "desarrollo"],
        "4. Reskilling de Talento Digital": ["talento", "capacitacion", "gente", "personas", "habilidades", "recursos"],
        "5. Expansión de Mercados": ["crecimiento", "mercado", "global", "ventas", "nuevo", "socios"],
        "6. Smart Logistics": ["logistica", "entrega", "inventario", "cadena", "transporte", "procesos"],
        "7. Ciberseguridad": ["riesgo", "seguridad", "datos", "nube", "ataque", "recursos"]
    }
    if any(word in texto for word in keywords.get(accion_nombre, [])):
        return 1.2
    return 1.0

# --- FUNCIÓN PARA CONSULTAR A GEMINI ---
def obtener_recomendacion_ia(datos_empresa, estrategia):
    prompt = f"""
    Actúa como un Consultor de Estrategia Senior y experto en Transformación Digital.
    Analiza la siguiente información de un estudiante de maestría:
    
    EMPRESA: {datos_empresa['empresa']}
    INDUSTRIA: {datos_empresa['industria']}
    ARQUITECTURA (CANVAS): {datos_empresa['vp']}, {datos_empresa['proc']}, {datos_empresa['recursos']}
    FODA: Fortalezas: {datos_empresa['fort']}, Debilidades: {datos_empresa['deb']}
    ESTRATEGIA (Play to Win): Jugar en {estrategia['donde']} y ganar mediante {estrategia['como']}.
    
    PROPORCIONA:
    1. Una validación breve de si la estrategia es coherente con el FODA.
    2. Dos recomendaciones críticas de cosas que el estudiante NO está tomando en cuenta.
    Sé conciso, profesional y retador académicamente.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error al conectar con Gemini: {str(e)}"

# --- INICIALIZACIÓN DE ESTADO ---
if 'paso' not in st.session_state:
    st.session_state.paso = 1
    st.session_state.presupuesto = 20.0
    st.session_state.historial = []
    st.session_state.ultimo_impacto = None
    st.session_state.diagnostico_texto = ""
    st.session_state.empresa = ""
    st.session_state.industria = ""
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

# --- NAVEGACIÓN ---

if st.session_state.paso == 1:
    st.title("Fase 1: Diagnóstico Integral")
    with st.form("f1"):
        st.session_state.empresa = st.text_input("Empresa:")
        st.session_state.industria = st.selectbox("Industria:", ["Manufactura", "Servicios", "Tecnología", "Retail"])
        c1, c2 = st.columns(2)
        with c1:
            vp = st.text_area("Propuesta de Valor:"); proc = st.text_area("Procesos Clave:")
            fort = st.text_area("Fortalezas:"); opp = st.text_area("Oportunidades:")
        with c2:
            recursos = st.text_area("Recursos Clave:"); socios = st.text_area("Socios Clave:")
            deb = st.text_area("Debilidades:"); ame = st.text_area("Amenazas:")
        if st.form_submit_button("Siguiente"):
            st.session_state.datos_f1 = {"empresa": st.session_state.empresa, "industria": st.session_state.industria, "vp": vp, "proc": proc, "recursos": recursos, "socios": socios, "fort": fort, "opp": opp, "deb": deb, "ame": ame}
            st.session_state.diagnostico_texto = f"{vp} {proc} {recursos} {socios} {fort} {opp} {deb} {ame}"
            st.session_state.paso = 2
            st.rerun()

elif st.session_state.paso == 2:
    st.title("Fase 2: Estrategia")
    with st.form("f2"):
        donde = st.text_input("¿Dónde jugar?"); como = st.text_input("¿Cómo ganar?")
        if st.form_submit_button("Iniciar Simulador"):
            st.session_state.donde = donde; st.session_state.como = como
            st.session_state.paso = 3
            st.rerun()

elif st.session_state.paso == 3:
    st.title(f"Simulador: {st.session_state.empresa}")
    col_vis, col_ctrl = st.columns([2, 1])

    with col_vis:
        t_matriz, t_gap, t_ia = st.tabs(["📋 BSC", "📊 Gaps", "🤖 CONSULTORÍA IA"])
        
        # Lógica de Matriz y Gaps (Simplificada para el ejemplo)
        with t_matriz:
            rows = [{"KPI": k, "Actual": d['actual'], "Meta": d['ideal']} for p, ks in st.session_state.kpis.items() for k, d in ks.items()]
            st.table(pd.DataFrame(rows))
        
        with t_ia:
            st.subheader("Análisis Estratégico por Gemini")
            if st.button("Solicitar Recomendación a la IA"):
                with st.spinner("Analizando tu estrategia..."):
                    estrategia_data = {"donde": st.session_state.donde, "como": st.session_state.como}
                    feedback = obtener_recomendacion_ia(st.session_state.datos_f1, estrategia_data)
                    st.markdown(feedback)

    with col_ctrl:
        st.subheader("Simulación")
        st.metric("Presupuesto", f"${round(st.session_state.presupuesto, 2)}M")
        sel = st.selectbox("Acción:", list(DECISIONES.keys()))
        if st.button("Invertir"):
            info = DECISIONES[sel]
            if st.session_state.presupuesto >= info['costo']:
                mod = calcular_modificador(st.session_state.diagnostico_texto, sel)
                st.session_state.presupuesto -= info['costo']
                for p, ks in info['impacto'].items():
                    for k, v in ks.items():
                        st.session_state.kpis[p][k]['actual'] = round(st.session_state.kpis[p][k]['actual'] + (v * mod), 2)
                st.session_state.historial.append({"Iniciativa": sel, "Coherencia": "Alta" if mod > 1 else "Normal"})
                st.rerun()
        
        st.divider()
        if st.button("📊 GENERAR REPORTE FINAL", type="primary"):
            st.session_state.paso = 4
            st.rerun()

elif st.session_state.paso == 4:
    st.title("Reporte Final")
    # Mostrar resumen de Fase 1 (Canvas/FODA) como en el prompt anterior...
    st.subheader("Diagnóstico Inicial")
    st.write(st.session_state.datos_f1)
    st.subheader("KPIs Finales")
    st.write(st.session_state.kpis)
    if st.button("Reiniciar"):
        st.session_state.clear()
        st.rerun()
