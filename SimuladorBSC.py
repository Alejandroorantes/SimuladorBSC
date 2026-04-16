import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import copy

# Configuración inicial de la página
st.set_page_config(page_title="Simulador de Estrategia y BSC", layout="wide")

# --- INICIALIZACIÓN DE ESTADO DE SESIÓN ---
if 'paso' not in st.session_state:
    st.session_state.paso = 1
    st.session_state.presupuesto = 20.0
    st.session_state.historial = []
    st.session_state.ultimo_impacto = None
    st.session_state.diagnostico = {} # Para almacenar Canvas y FODA
    st.session_state.kpis = {
        "Financiera": {
            "ROI": {"actual": 8.0, "ideal": 15.0, "unit": "%"},
            "Margen EBITDA": {"actual": 12.0, "ideal": 18.0, "unit": "%"}
        },
        "Clientes": {
            "Satisfacción (NPS)": {"actual": 65.0, "ideal": 90.0, "unit": "pts"},
            "Cuota Mercado": {"actual": 15.0, "ideal": 25.0, "unit": "%"}
        },
        "Procesos": {
            "Eficiencia OEE": {"actual": 70.0, "ideal": 90.0, "unit": "%"},
            "Tiempo Ciclo": {"actual": 15.0, "ideal": 8.0, "unit": "días"}
        },
        "Aprendizaje": {
            "Índice Innovación": {"actual": 3.0, "ideal": 9.0, "unit": "proy"},
            "Capacitación": {"actual": 20.0, "ideal": 55.0, "unit": "hrs"}
        }
    }
    st.session_state.initial_kpis = copy.deepcopy(st.session_state.kpis)

# --- DEFINICIÓN DE LAS 7 DECISIONES ESTRATÉGICAS ---
DECISIONES = {
    "1. Automatización Robótica (RPA/AI)": {
        "costo": 5.5, 
        "impacto": {"Procesos": {"Eficiencia OEE": 12.0, "Tiempo Ciclo": -3.0}, "Financiera": {"Margen EBITDA": 2.5}}
    },
    "2. Programa de Lealtad Omnicanal": {
        "costo": 3.5, 
        "impacto": {"Clientes": {"Satisfacción (NPS)": 18.0, "Cuota Mercado": 4.0}, "Financiera": {"Margen EBITDA": -0.5}}
    },
    "3. I+D: Productos Sustentables": {
        "costo": 6.5, 
        "impacto": {"Aprendizaje": {"Índice Innovación": 5.0}, "Clientes": {"Cuota Mercado": 6.0}, "Financiera": {"ROI": -1.5}}
    },
    "4. Reskilling de Talento Digital": {
        "costo": 2.5, 
        "impacto": {"Aprendizaje": {"Capacitación": 25.0, "Índice Innovación": 2.0}, "Procesos": {"Eficiencia OEE": 4.0}}
    },
    "5. Expansión a Mercados Emergentes": {
        "costo": 7.5, 
        "impacto": {"Clientes": {"Cuota Mercado": 10.0}, "Financiera": {"ROI": 4.0}, "Procesos": {"Tiempo Ciclo": 2.0}}
    },
    "6. Smart Logistics (Supply Chain)": {
        "costo": 4.0, 
        "impacto": {"Procesos": {"Tiempo Ciclo": -4.0}, "Financiera": {"Margen EBITDA": 3.0}}
    },
    "7. Ciberseguridad y Cloud": {
        "costo": 3.0, 
        "impacto": {"Procesos": {"Eficiencia OEE": 5.0}, "Aprendizaje": {"Índice Innovación": 1.0}}
    }
}

# --- NAVEGACIÓN ---

# PASO 1: DIAGNÓSTICO
if st.session_state.paso == 1:
    st.title("Fase 1: Diagnóstico Organizacional")
    with st.form("form_f1"):
        st.session_state.empresa = st.text_input("Nombre de la Organización:", "")
        st.session_state.industria = st.selectbox("Industria:", ['Manufactura', 'Servicios', 'Tecnología', 'Retail'])
        st.subheader("Business Model Canvas")
        st.session_state.diagnostico['vp'] = st.text_area("Propuesta de Valor:")
        st.session_state.diagnostico['seg'] = st.text_area("Segmentos de Cliente:")
        st.subheader("Análisis FODA")
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.diagnostico['fortalezas'] = st.text_area("Fortalezas:")
            st.session_state.diagnostico['oportunidades'] = st.text_area("Oportunidades:")
        with c2:
            st.session_state.diagnostico['debilidades'] = st.text_area("Debilidades:")
            st.session_state.diagnostico['amenazas'] = st.text_area("Amenazas:")
        if st.form_submit_button("Siguiente"):
            if st.session_state.empresa:
                st.session_state.paso = 2
                st.rerun()
            else:
                st.error("Ingresa el nombre de la empresa.")

# PASO 2: PLAY TO WIN
elif st.session_state.paso == 2:
    st.title("Fase 2: Play to Win (Estrategia)")
    with st.form("form_f2"):
        st.session_state.donde = st.text_input("¿Dónde jugar?")
        st.session_state.como = st.text_input("¿Cómo ganar?")
        st.session_state.diagnostico['capacidades'] = st.text_area("Capacidades Requeridas:")
        if st.form_submit_button("Iniciar Simulador"):
            st.session_state.paso = 3
            st.rerun()

# PASO 3: SIMULADOR
elif st.session_state.paso == 3:
    st.title(f"Tablero Estratégico: {st.session_state.empresa}")
    st.markdown(f"**Estrategia:** {st.session_state.como} en {st.session_state.donde}")
    
    col_vis, col_ctrl = st.columns([2, 1])

    with col_vis:
        t_matriz, t_gap, t_radar, t_hist = st.tabs(["📋 Matriz BSC", "📊 Análisis Gaps", "🕸 Radar", "📜 Historial"])
        
        labels, vals, targets, rows = [], [], [], []
        for p, k_dict in st.session_state.kpis.items():
            for k, d in k_dict.items():
                labels.append(k)
                vals.append(d['actual'])
                targets.append(d['ideal'])
                status = "🟢" if d['actual'] >= d['ideal'] else "🟡" if d['actual'] >= (d['ideal']*0.8) else "🔴"
                rows.append({"Estado": status, "Perspectiva": p, "KPI": k, "Actual": d['actual'], "Meta": d['ideal'], "Unidad": d['unit']})
        
        with t_matriz:
            st.table(pd.DataFrame(rows))
        with t_gap:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.bar(np.arange(len(labels)) - 0.2, vals, 0.4, label='Actual', color='#0D47A1')
            ax.bar(np.arange(len(labels)) + 0.2, targets, 0.4, label='Meta', color='#CFD8DC', alpha=0.6)
            ax.set_xticks(np.arange(len(labels)))
            ax.set_xticklabels(labels, rotation=45, ha='right')
            ax.legend()
            st.pyplot(fig)
        with t_radar:
            N = len(labels)
            angles = [n / float(N) * 2 * np.pi for n in range(N)]
            angles += angles[:1]
            fig_r, ax_r = plt.subplots(subplot_kw=dict(polar=True))
            ax_r.plot(angles, targets + targets[:1], 'r--', alpha=0.3)
            ax_r.plot(angles, vals + vals[:1], 'b-', linewidth=2)
            ax_r.set_xticks(angles[:-1])
            ax_r.set_xticklabels(labels)
            st.pyplot(fig_r)
        with t_hist:
            st.table(pd.DataFrame(st.session_state.historial)) if st.session_state.historial else st.write("Sin registros.")

    with col_ctrl:
        st.subheader("Panel de Inversión")
        st.metric("Presupuesto Disponible", f"${round(st.session_state.presupuesto, 2)}M")
        
        sel = st.selectbox("Elegir Iniciativa:", list(DECISIONES.keys()))
        info = DECISIONES[sel]
        
        if st.button("Ejecutar Decisión", use_container_width=True):
            if st.session_state.presupuesto >= info['costo']:
                cambios_recientes = []
                st.session_state.presupuesto -= info['costo']
                
                for p, kpis_impact in info['impacto'].items():
                    for k, v in kpis_impact.items():
                        anterior = st.session_state.kpis[p][k]['actual']
                        nuevo = round(anterior + v, 2)
                        st.session_state.kpis[p][k]['actual'] = nuevo
                        cambios_recientes.append({"KPI": k, "Anterior": anterior, "Cambio": f"{'+' if v>0 else ''}{v}", "Nuevo": nuevo})
                
                st.session_state.ultimo_impacto = {"nombre": sel, "detalles": cambios_recientes}
                st.session_state.historial.append({"Iniciativa": sel, "Costo": f"${info['costo']}M", "Resultados": ", ".join([f"{c['KPI']}: {c['Nuevo']}" for c in cambios_recientes])})
                st.rerun()
            else:
                st.error("Presupuesto insuficiente.")

        if st.session_state.ultimo_impacto:
            st.markdown("---")
            st.dataframe(pd.DataFrame(st.session_state.ultimo_impacto['detalles']), hide_index=True)

        st.divider()
        # BOTÓN DE REPORTE
        if st.button("📊 GENERAR REPORTE FINAL", type="primary", use_container_width=True):
            st.session_state.paso = 4
            st.rerun()
            
        if st.button("🔄 Reiniciar Todo", type="secondary"):
            st.session_state.clear()
            st.rerun()

# PASO 4: REPORTE FINAL
elif st.session_state.paso == 4:
    st.title(f"Reporte de Desempeño Estratégico: {st.session_state.empresa}")
    
    st.header("1. Diagnóstico y Estrategia")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"**Industria:** {st.session_state.industria}")
        st.markdown(f"**Propuesta de Valor:** {st.session_state.diagnostico['vp']}")
        st.markdown(f"**Segmentos:** {st.session_state.diagnostico['seg']}")
    with col_b:
        st.markdown(f"**¿Dónde ganar?:** {st.session_state.donde}")
        st.markdown(f"**¿Cómo ganar?:** {st.session_state.como}")

    st.header("2. Resultados del Balanced Scorecard")
    report_rows = []
    for p, kpis in st.session_state.kpis.items():
        for k, d in kpis.items():
            gap = round(d['actual'] - d['ideal'], 2)
            status = "CUMPLIDO" if gap >= 0 else "PENDIENTE"
            report_rows.append({"Perspectiva": p, "KPI": k, "Valor Final": d['actual'], "Meta": d['ideal'], "Brecha": gap, "Estado": status})
    st.table(pd.DataFrame(report_rows))

    st.header("3. Historial de Decisiones Tomadas")
    if st.session_state.historial:
        st.table(pd.DataFrame(st.session_state.historial))
    else:
        st.write("No se ejecutaron inversiones durante la sesión.")

    st.markdown(f"**Presupuesto Remanente:** ${round(st.session_state.presupuesto, 2)}M")

    if st.button("Volver al Simulador"):
        st.session_state.paso = 3
        st.rerun()
