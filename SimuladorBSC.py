import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF

# Configuración inicial
st.set_page_config(page_title="Simulador de Estrategia Alex", layout="wide")

# --- FUNCIÓN GENERADORA DE PDF ---
def crear_pdf(nombre, datos_f1, estrategia, kpis, historial, reflexion):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        
        # Título
        pdf.cell(190, 10, txt="REPORTE ESTRATEGICO FINAL", ln=True, align='C')
        pdf.ln(5)
        
        # Información General
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(40, 10, "Participante: ", 0); pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, nombre.encode('latin-1', 'replace').decode('latin-1'), ln=True)
        
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(40, 10, "Empresa: ", 0); pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"{datos_f1['empresa']} ({datos_f1['industria']})".encode('latin-1', 'replace').decode('latin-1'), ln=True)
        
        # Estrategia
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "Estrategia Definida:", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 7, f"Donde jugar: {estrategia['donde']}\nComo ganar: {estrategia['como']}".encode('latin-1', 'replace').decode('latin-1'))
        
        # KPIs Finales
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "Resultados Finales de KPIs:", ln=True)
        pdf.set_font("Arial", '', 10)
        for p, ks in kpis.items():
            for k, d in ks.items():
                txt_kpi = f"- {p} | {k}: {d['actual']} (Meta: {d['ideal']})"
                pdf.cell(0, 7, txt_kpi.encode('latin-1', 'replace').decode('latin-1'), ln=True)
        
        # Reflexion
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "Analisis de Aprendizaje:", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 7, reflexion.encode('latin-1', 'replace').decode('latin-1'))
        
        return pdf.output(dest='S').encode('latin-1')
    except Exception as e:
        return str(e)

# --- MOTOR DE COHERENCIA ---
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

# --- INICIALIZACIÓN DE ESTADO ---
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

DECISIONES = {
    "1. Automatización Robótica (RPA/AI)": {"costo": 5.5, "impacto": {"Procesos": {"Eficiencia OEE": 12.0, "Tiempo Ciclo": -3.0}, "Financiera": {"Margen EBITDA": 2.5}}},
    "2. Programa de Lealtad Omnicanal": {"costo": 3.5, "impacto": {"Clientes": {"Satisfacción (NPS)": 18.0, "Cuota Mercado": 4.0}, "Financiera": {"Margen EBITDA": -0.5}}},
    "3. I+D: Productos Sustentables": {"costo": 6.5, "impacto": {"Aprendizaje": {"Índice Innovación": 5.0}, "Clientes": {"Cuota Mercado": 6.0}, "Financiera": {"ROI": -1.5}}},
    "4. Reskilling de Talento Digital": {"costo": 2.5, "impacto": {"Aprendizaje": {"Capacitación": 25.0, "Índice Innovación": 2.0}, "Procesos": {"Eficiencia OEE": 4.0}}},
    "5. Expansión de Mercados": {"costo": 7.5, "impacto": {"Clientes": {"Cuota Mercado": 10.0}, "Financiera": {"ROI": 4.0}, "Procesos": {"Tiempo Ciclo": 2.0}}},
    "6. Smart Logistics": {"costo": 4.0, "impacto": {"Procesos": {"Tiempo Ciclo": -4.0}, "Financiera": {"Margen EBITDA": 3.0}}},
    "7. Ciberseguridad": {"costo": 3.0, "impacto": {"Procesos": {"Eficiencia OEE": 5.0}, "Aprendizaje": {"Índice Innovación": 1.0}}}
}

# FASE 1: DIAGNÓSTICO
if st.session_state.paso == 1:
    st.title("Fase 1: Diagnóstico Integral de Negocio")
    with st.form("f1"):
        c_i1, c_i2 = st.columns(2)
        with c_i1: emp_in = st.text_input("Nombre de la Organización:")
        with c_i2: ind_in = st.selectbox("Industria:", ["Manufactura", "Servicios", "Bancario", "Agroindustria", "Alimentos y Bebidas", "Tecnología", "Retail"])
        
        st.subheader("I. Arquitectura (Canvas) y II. FODA")
        col1, col2 = st.columns(2)
        with col1:
            vp = st.text_area("Propuesta de Valor:"); pr = st.text_area("Procesos Clave:")
            ft = st.text_area("Fortalezas:"); op = st.text_area("Oportunidades:")
        with col2:
            rc = st.text_area("Recursos Clave:"); sc = st.text_area("Socios Clave:")
            db = st.text_area("Debilidades:"); am = st.text_area("Amenazas:")
            
        if st.form_submit_button("Siguiente"):
            if emp_in:
                st.session_state.datos_f1 = {"empresa": emp_in, "industria": ind_in, "vp": vp, "proc": pr, "recursos": rc, "socios": sc, "fort": ft, "opp": op, "deb": db, "ame": am}
                st.session_state.diagnostico_texto = f"{vp} {pr} {rc} {sc} {ft} {op} {db} {am}"
                st.session_state.paso = 2; st.rerun()
            else: st.error("Ingresa el nombre de la empresa.")

# FASE 2: ESTRATEGIA
elif st.session_state.paso == 2:
    st.title("Fase 2: Estrategia Play to Win")
    with st.form("f2"):
        donde = st.text_input("¿Dónde jugar?"); como = st.text_input("¿Cómo ganar?")
        if st.form_submit_button("Iniciar Simulador"):
            st.session_state.donde = donde; st.session_state.como = como
            st.session_state.paso = 3; st.rerun()

# FASE 3: TABLERO
elif st.session_state.paso == 3:
    st.title(f"Tablero de Control: {st.session_state.datos_f1['empresa']}")
    col_vis, col_ctrl = st.columns([2, 1])

    with col_vis:
        t_mat, t_gap, t_hist = st.tabs(["📋 Matriz BSC", "📊 Gaps", "📜 Historial"])
        rows = []
        labels, vals, targets = [], [], []
        for p, ks in st.session_state.kpis.items():
            for k, d in ks.items():
                labels.append(k); vals.append(d['actual']); targets.append(d['ideal'])
                status = "🟢" if d['actual'] >= d['ideal'] else "🟡" if d['actual'] >= (d['ideal']*0.8) else "🔴"
                rows.append({"Estado": status, "Perspectiva": p, "KPI": k, "Actual": d['actual'], "Meta": d['ideal']})
        with t_mat: st.table(pd.DataFrame(rows))
        with t_gap:
            fig, ax = plt.subplots(figsize=(10, 4))
            x = np.arange(len(labels))
            ax.bar(x - 0.2, vals, 0.4, label='Actual', color='#007bff')
            ax.bar(x + 0.2, targets, 0.4, label='Meta', color='#e9ecef', alpha=0.5)
            ax.set_xticks(x); ax.set_xticklabels(labels, rotation=45); ax.legend(); st.pyplot(fig)
        with t_hist: st.table(pd.DataFrame(st.session_state.historial)) if st.session_state.historial else st.info("Sin inversiones.")

    with col_ctrl:
        st.subheader("Simulación")
        st.metric("Presupuesto", f"${round(st.session_state.presupuesto, 2)}M")
        sel = st.selectbox("Elegir Iniciativa:", list(DECISIONES.keys()))
        if st.button("Invertir", use_container_width=True):
            info = DECISIONES[sel]
            if st.session_state.presupuesto >= info['costo']:
                mod = calcular_modificador(st.session_state.diagnostico_texto, sel)
                st.session_state.presupuesto -= info['costo']
                detalles = []
                for p, k_impacts in info['impacto'].items():
                    for kpi_nom, val in k_impacts.items():
                        v_final = round(val * mod, 2)
                        st.session_state.kpis[p][kpi_nom]['actual'] = round(st.session_state.kpis[p][kpi_nom]['actual'] + v_final, 2)
                        detalles.append({"KPI": kpi_nom, "Impacto": f"+{v_final}"})
                st.session_state.ultimo_impacto = detalles
                st.session_state.historial.append({"Iniciativa": sel, "Costo": f"${info['costo']}M", "Bono": "Sí" if mod > 1 else "No"})
                st.rerun()
        if st.button("📊 REPORTE FINAL", type="primary", use_container_width=True): st.session_state.paso = 4; st.rerun()

# FASE 4: REPORTE FINAL CON PDF
elif st.session_state.paso == 4:
    st.title("Reporte Estratégico Final")
    nombre_u = st.text_input("Nombre de la persona que completó la simulación:")
    
    # Resumen Visual
    st.markdown("---")
    c_r1, c_r2 = st.columns(2)
    with c_r1:
        st.info(f"**Empresa:** {st.session_state.datos_f1['empresa']}\n\n**Propuesta:** {st.session_state.datos_f1['vp']}")
    with c_r2:
        st.warning(f"**Estrategia:** {st.session_state.como}\n\n**Donde:** {st.session_state.donde}")

    st.subheader("Análisis de Aprendizaje")
    analisis_u = st.text_area("Análisis de lo aprendido (Estrategia vs Decisiones vs KPIs):", height=150)
    
    if st.button("Volver"): st.session_state.paso = 3; st.rerun()

    if nombre_u and analisis_u:
        res_pdf = crear_pdf(nombre_u, st.session_state.datos_f1, {"donde": st.session_state.donde, "como": st.session_state.como}, st.session_state.kpis, st.session_state.historial, analisis_u)
        
        if isinstance(res_pdf, bytes):
            st.download_button("📥 DESCARGAR REPORTE PDF", data=res_pdf, file_name=f"Reporte_{st.session_state.datos_f1['empresa']}.pdf", mime="application/pdf")
        else: st.error(f"Error: {res_pdf}")
    else: st.info("Ingresa nombre y análisis para habilitar el PDF.")
