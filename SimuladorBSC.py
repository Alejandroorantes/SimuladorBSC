import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests  # Usaremos peticiones directas para evitar el error 401
import json

# ==========================================
# 1. CONFIGURACIÓN DE IA (MÉTODO DIRECTO)
# ==========================================
# PEGA AQUÍ TU API KEY
API_KEY = "AQ.Ab8RN6Lv4M2Kr87aQ-Vf_4cLpRXrzKONLBeoNPzzNbqVpP-nJA" 

def obtener_recomendacion_ia(datos, estrategia):
    # URL directa de la API de Google Gemini
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    
    prompt_text = f"""
    Actúa como un Consultor de Estrategia Senior. Analiza este modelo de negocio:
    EMPRESA: {datos['empresa']} ({datos['industria']})
    ARQUITECTURA: Valor: {datos['vp']}, Procesos: {datos['proc']}, Recursos: {datos['recursos']}, Socios: {datos['socios']}
    FODA: Fortalezas: {datos['fort']}, Oportunidades: {datos['opp']}, Debilidades: {datos['deb']}, Amenazas: {datos['ame']}
    ESTRATEGIA: Jugar en {estrategia['donde']} y ganar mediante {estrategia['como']}
    
    TAREA: Da un diagnóstico de coherencia breve y menciona 2 puntos ciegos estratégicos.
    """

    payload = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response_json = response.json()
        
        # Extraer el texto de la respuesta
        if response.status_code == 200:
            return response_json['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"⚠️ Error de la API ({response.status_code}): {response_json.get('error', {}).get('message', 'Error desconocido')}"
    except Exception as e:
        return f"⚠️ Error de conexión: {str(e)}"

# ==========================================
# 2. CONFIGURACIÓN DE PÁGINA E INICIALIZACIÓN
# ==========================================
st.set_page_config(page_title="Simulador Estratégico Alex", layout="wide")

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

# --- MOTOR DE COHERENCIA ---
def calcular_modificador(texto_diagnostico, accion_nombre):
    texto = str(texto_diagnostico).lower()
    keywords = {
        "1. Automatización Robótica (RPA/AI)": ["procesos", "eficiencia", "operación"],
        "2. Programa de Lealtad Omnicanal": ["clientes", "nps", "fidelidad"],
        "3. I+D: Productos Sustentables": ["innovacion", "producto", "verde"],
        "4. Reskilling de Talento Digital": ["talento", "capacitacion", "gente"],
        "5. Expansión de Mercados": ["crecimiento", "mercado", "global"],
        "6. Smart Logistics": ["logistica", "entrega", "cadena"],
        "7. Ciberseguridad": ["riesgo", "seguridad", "datos"]
    }
    if any(word in texto for word in keywords.get(accion_nombre, [])):
        return 1.2
    return 1.0

# ==========================================
# 3. INTERFAZ DE USUARIO
# ==========================================

if st.session_state.paso == 1:
    st.title("Fase 1: Diagnóstico Integral")
    with st.form("f1"):
        emp_in = st.text_input("Empresa:")
        ind_in = st.selectbox("Industria:", ["Manufactura", "Servicios", "Tecnología", "Retail"])
        c1, c2 = st.columns(2)
        with c1:
            vp = st.text_area("Propuesta de Valor:"); pr = st.text_area("Procesos Clave:")
            ft = st.text_area("Fortalezas:"); op = st.text_area("Oportunidades:")
        with c2:
            rc = st.text_area("Recursos Clave:"); sc = st.text_area("Socios Clave:")
            db = st.text_area("Debilidades:"); am = st.text_area("Amenazas:")
        if st.form_submit_button("Siguiente"):
            st.session_state.datos_f1 = {"empresa": emp_in, "industria": ind_in, "vp": vp, "proc": pr, "recursos": rc, "socios": sc, "fort": ft, "opp": op, "deb": db, "ame": am}
            st.session_state.paso = 2; st.rerun()

elif st.session_state.paso == 2:
    st.title("Fase 2: Estrategia")
    with st.form("f2"):
        dj = st.text_input("¿Dónde jugar?"); cg = st.text_input("¿Cómo ganar?")
        if st.form_submit_button("Iniciar Simulador"):
            st.session_state.donde = dj; st.session_state.como = cg
            st.session_state.paso = 3; st.rerun()

elif st.session_state.paso == 3:
    st.title(f"Simulador: {st.session_state.datos_f1['empresa']}")
    col_vis, col_ctrl = st.columns([2, 1])

    with col_vis:
        t_mat, t_gap, t_ia = st.tabs(["📋 BSC", "📊 Gaps", "🤖 CONSULTORÍA IA"])
        with t_mat:
            rows = [{"KPI": k, "Actual": d['actual'], "Meta": d['ideal']} for p, ks in st.session_state.kpis.items() for k, d in ks.items()]
            st.table(pd.DataFrame(rows))
        with t_gap:
            labels = [k for p, ks in st.session_state.kpis.items() for k in ks]
            vals = [d['actual'] for p, ks in st.session_state.kpis.items() for d in ks.values()]
            targets = [d['ideal'] for p, ks in st.session_state.kpis.items() for d in ks.values()]
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.bar(np.arange(len(labels)) - 0.2, vals, 0.4, label='Actual', color='#007bff')
            ax.bar(np.arange(len(labels)) + 0.2, targets, 0.4, label='Meta', color='#e9ecef')
            ax.set_xticks(np.arange(len(labels))); ax.set_xticklabels(labels, rotation=45); ax.legend(); st.pyplot(fig)
        with t_ia:
            if st.button("Consultar a Gemini"):
                with st.spinner("Analizando..."):
                    feedback = obtener_recomendacion_ia(st.session_state.datos_f1, {"donde": st.session_state.donde, "como": st.session_state.como})
                    st.markdown(feedback)

    with col_ctrl:
        st.subheader("Inversiones")
        st.metric("Presupuesto", f"${round(st.session_state.presupuesto, 2)}M")
        sel = st.selectbox("Acción:", list(DECISIONES.keys()))
        if st.button("Invertir", use_container_width=True):
            info = DECISIONES[sel]
            if st.session_state.presupuesto >= info['costo']:
                mod = calcular_modificador(str(st.session_state.datos_f1), sel)
                st.session_state.presupuesto -= info['costo']
                for p, ks in info['impacto'].items():
                    for k, v in ks.items():
                        st.session_state.kpis[p][k]['actual'] = round(st.session_state.kpis[p][k]['actual'] + (v * mod), 2)
                st.session_state.historial.append({"Acción": sel, "Bono": "Sí" if mod > 1 else "No"})
                st.rerun()
        if st.button("📊 REPORTE FINAL", type="primary", use_container_width=True):
            st.session_state.paso = 4; st.rerun()
        if st.button("🔄 Reiniciar"): st.session_state.clear(); st.rerun()

elif st.session_state.paso == 4:
    st.title("Reporte Final")
    d = st.session_state.datos_f1
    st.subheader("I. Resumen del Diagnóstico")
    c_a, c_b = st.columns(2)
    with c_a: st.info(f"**Canvas:** {d['vp']} / {d['proc']}")
    with c_b: st.warning(f"**FODA:** {d['fort']} / {d['deb']}")
    st.subheader("II. Resultados")
    st.success(f"Estrategia: {st.session_state.como}")
    f_rows = [{"KPI": k, "Final": d['actual'], "Meta": d['ideal']} for p, ks in st.session_state.kpis.items() for k, d in ks.items()]
    st.table(pd.DataFrame(f_rows))
    if st.button("Volver"): st.session_state.paso = 3; st.rerun()
