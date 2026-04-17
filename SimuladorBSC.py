import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF

# Configuración inicial
st.set_page_config(page_title="Simulador de Estrategia Alex", layout="wide")

# --- FUNCIÓN GENERADORA DE PDF ---
def crear_pdf(nombre, empresa, industria, estrategia, kpis, historial, reflexion):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        
        # Título
        pdf.cell(190, 10, txt="REPORTE ESTRATÉGICO FINAL", ln=True, align='C')
        pdf.ln(10)
        
        # Datos Generales
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(50, 10, "Participante: ", 0)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, nombre.encode('latin-1', 'replace').decode('latin-1'), ln=True)
        
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(50, 10, "Organización: ", 0)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"{empresa} ({industria})".encode('latin-1', 'replace').decode('latin-1'), ln=True)
        
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Estrategia Definida:", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 10, estrategia.encode('latin-1', 'replace').decode('latin-1'))
        
        # Resultados KPIs
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Resultados Finales (KPIs):", ln=True)
        pdf.set_font("Arial", '', 10)
        for p, ks in kpis.items():
            for k, d in ks.items():
                linea = f"- {p} | {k}: {d['actual']} (Meta: {d['ideal']})"
                pdf.cell(0, 8, linea.encode('latin-1', 'replace').decode('latin-1'), ln=True)
        
        # Reflexión
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Análisis de Aprendizaje:", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 8, reflexion.encode('latin-1', 'replace').decode('latin-1'))
        
        return pdf.output(dest='S').encode('latin-1')
    except Exception as e:
        return str(e)

# --- LÓGICA DEL MOTOR (Se mantiene igual) ---
def calcular_modificador(texto_diagnostico, accion_nombre):
    texto = texto_diagnostico.lower()
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

# --- INICIALIZACIÓN ---
if 'paso' not in st.session_state:
    st.session_state.paso = 1
    st.session_state.presupuesto = 20.0
    st.session_state.historial = []
    st.session_state.ultimo_impacto = None
    st.session_state.kpis = {
        "Financiera": {"ROI": {"actual": 8.0, "ideal": 15.0}, "Margen EBITDA": {"actual": 12.0, "ideal": 18.0}},
        "Clientes": {"Satisfacción (NPS)": {"actual": 65.0, "ideal": 90.0}, "Cuota Mercado": {"actual": 15.0, "ideal": 25.0}},
        "Procesos": {"Eficiencia OEE": {"actual": 70.0, "ideal": 90.0}, "Tiempo Ciclo": {"actual": 15.0, "ideal": 8.0}},
        "Aprendizaje": {"Índice Innovación": {"actual": 3.0, "ideal": 9.0}, "Capacitación": {"actual": 20.0, "ideal": 55.0}}
    }

# FASE 1: DIAGNÓSTICO
if st.session_state.paso == 1:
    st.title("Fase 1: Diagnóstico")
    with st.form("f1"):
        empresa = st.text_input("Nombre de la Empresa:")
        industria = st.selectbox("Industria:", ["Manufactura", "Servicios", "Bancario", "Tecnología", "Retail"])
        c1, c2 = st.columns(2)
        with c1:
            vp = st.text_area("Propuesta de Valor:"); pr = st.text_area("Procesos Clave:")
            ft = st.text_area("Fortalezas:"); op = st.text_area("Oportunidades:")
        with c2:
            rc = st.text_area("Recursos Clave:"); sc = st.text_area("Socios Clave:")
            db = st.text_area("Debilidades:"); am = st.text_area("Amenazas:")
        if st.form_submit_button("Siguiente"):
            if empresa:
                st.session_state.datos_f1 = {"empresa": empresa, "industria": industria, "vp": vp, "proc": pr, "recursos": rc, "socios": sc, "fort": ft, "opp": op, "deb": db, "ame": am}
                st.session_state.diagnostico_texto = f"{vp} {pr} {rc} {sc} {ft} {op} {db} {am}"
                st.session_state.paso = 2; st.rerun()
            else: st.error("Ingresa el nombre")

# FASE 2: ESTRATEGIA
elif st.session_state.paso == 2:
    st.title("Fase 2: Estrategia")
    with st.form("f2"):
        dj = st.text_input("¿Dónde jugar?"); cg = st.text_input("¿Cómo ganar?")
        if st.form_submit_button("Iniciar"):
            st.session_state.donde = dj; st.session_state.como = cg
            st.session_state.paso = 3; st.rerun()

# FASE 3: SIMULADOR
elif st.session_state.paso == 3:
    st.title(f"Simulando: {st.session_state.datos_f1['empresa']}")
    col_vis, col_ctrl = st.columns([2, 1])
    
    with col_vis:
        t1, t2 = st.tabs(["📋 BSC", "📊 Gaps"])
        with t1:
            rows = [{"KPI": k, "Actual": d['actual'], "Meta": d['ideal']} for p, ks in st.session_state.kpis.items() for k, d in ks.items()]
            st.table(pd.DataFrame(rows))
        with t2:
            # Gráfico simple
            labels = [k for p, ks in st.session_state.kpis.items() for k in ks]
            vals = [d['actual'] for p, ks in st.session_state.kpis.items() for d in ks.values()]
            fig, ax = plt.subplots(figsize=(10, 3))
            ax.bar(labels, vals, color='#007bff')
            plt.xticks(rotation=45)
            st.pyplot(fig)

    with col_ctrl:
        st.subheader("Acciones")
        st.metric("Presupuesto", f"${round(st.session_state.presupuesto, 2)}M")
        # Por brevedad, simplifico el diccionario DECISIONES (puedes usar el tuyo completo)
        acciones = ["1. Automatización Robótica (RPA/AI)", "2. Programa de Lealtad Omnicanal", "3. I+D: Productos Sustentables"]
        sel = st.selectbox("Inversión:", acciones)
        if st.button("Ejecutar"):
            # Aquí iría tu lógica de impacto (DECISIONES[sel])
            st.session_state.presupuesto -= 2.0
            st.session_state.historial.append({"Iniciativa": sel, "Costo": "$2M"})
            st.rerun()
        if st.button("GENERAR REPORTE"): st.session_state.paso = 4; st.rerun()

# FASE 4: REPORTE FINAL Y PDF
elif st.session_state.paso == 4:
    st.title("Reporte Estratégico Final")
    
    nombre_u = st.text_input("Tu Nombre Completo:")
    analisis_u = st.text_area("Análisis de Aprendizaje:", height=150)
    
    if st.button("Volver"): st.session_state.paso = 3; st.rerun()
    
    if nombre_u and analisis_u:
        estr_completa = f"{st.session_state.como} en {st.session_state.donde}"
        
        pdf_res = crear_pdf(
            nombre_u, 
            st.session_state.datos_f1['empresa'], 
            st.session_state.datos_f1['industria'],
            estr_completa,
            st.session_state.kpis,
            st.session_state.historial,
            analisis_u
        )
        
        if isinstance(pdf_res, bytes):
            st.download_button(
                label="📥 DESCARGAR REPORTE PDF",
                data=pdf_res,
                file_name="Reporte_Estrategico.pdf",
                mime="application/pdf"
            )
        else:
            st.error(f"Error al generar PDF: {pdf_res}")
    else:
        st.info("Completa tu nombre y el análisis para descargar el PDF.")
