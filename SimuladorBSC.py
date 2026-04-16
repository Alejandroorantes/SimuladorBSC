import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import copy

# Configuración inicial de la página
st.set_page_config(page_title="Simulador Estratégico Alex", layout="wide")

# --- INICIALIZACIÓN DE ESTADO DE SESIÓN ---
if 'paso' not in st.session_state:
    st.session_state.paso = 1
    st.session_state.presupuesto = 20.0
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

# Definición de Decisiones
DECISIONES = {
    "Automatización Industrial": {"costo": 5.0, "impacto": {"Procesos": {"Eficiencia OEE": 12.0}, "Financiera": {"Margen EBITDA": 2.5}}},
    "Programa de Lealtad Digital": {"costo": 3.0, "impacto": {"Clientes": {"Satisfacción (NPS)": 15.0, "Cuota Mercado": 4.0}}},
    "Capacitación Agile & Lean": {"costo": 2.0, "impacto": {"Aprendizaje": {"Capacitación": 20.0}, "Procesos": {"Eficiencia OEE": 5.0}}}
}

# --- NAVEGACIÓN Y FLUJO ---

# PASO 1: DIAGNÓSTICO (EMPRESA, CANVAS Y FODA)
if st.session_state.paso == 1:
    st.title("Fase 1: Diagnóstico y Análisis")
    with st.form("form_diagnostico"):
        st.session_state.empresa = st.text_input("Nombre de la Empresa:", "")
        st.session_state.industria = st.selectbox("Industria:", ['Manufactura/CPG', 'Servicios', 'Tecnología', 'Retail'])
        
        st.subheader("Business Model Canvas")
        st.session_area_canvas = st.text_area("Propuesta de Valor Clave:", placeholder="¿Qué valor entregamos?")
        
        st.subheader("Análisis FODA")
        col1, col2 = st.columns(2)
        with col1:
            st.text_area("Fortalezas:", placeholder="Puntos fuertes internos")
            st.text_area("Oportunidades:", placeholder="Factores externos positivos")
        with col2:
            st.text_area("Debilidades:", placeholder="Puntos a mejorar internos")
            st.text_area("Amenazas:", placeholder="Riesgos externos")
            
        if st.form_submit_button("Siguiente: Play to Win"):
            if st.session_state.empresa:
                st.session_state.paso = 2
                st.rerun()
            else:
                st.warning("Por favor, ingresa el nombre de la empresa.")

# PASO 2: PLAY TO WIN
elif st.session_state.paso == 2:
    st.title("Fase 2: Play to Win (Estrategia)")
    with st.form("form_play"):
        st.session_state.donde = st.text_input("¿Dónde jugar?", placeholder="Mercado, Clientes, Canales")
        st.session_state.como = st.text_input("¿Cómo ganar?", placeholder="Ventaja competitiva")
        st.text_area("Capacidades Requeridas:", placeholder="Sistemas y talento")
        
        if st.form_submit_button("Generar Simulador"):
            st.session_state.paso = 3
            st.rerun()
        if st.form_submit_button("Volver al Diagnóstico"):
            st.session_state.paso = 1
            st.rerun()

# PASO 3: SIMULADOR COMPLETO
elif st.session_state.paso == 3:
    st.title(f"Tablero de Control: {st.session_state.empresa}")
    st.markdown(f"**Estrategia:** {st.session_state.como} en {st.session_state.donde}")
    
    col_vis, col_ctrl = st.columns([2, 1])

    with col_vis:
        tab_matriz, tab_gap, tab_radar = st.tabs(["📋 Matriz BSC", "📊 Barras (Gap)", "🕸 Radar"])
        
        # Datos para visualización
        labels, vals, targets, bsc_rows = [], [], [], []
        for p, kpis in st.session_state.kpis.items():
            for k, d in kpis.items():
                labels.append(k)
                vals.append(d['actual'])
                targets.append(d['ideal'])
                bsc_rows.append({"Perspectiva": p, "KPI": k, "Actual": d['actual'], "Meta": d['ideal'], "Unidad": d['unit']})
        
        with tab_matriz:
            st.table(pd.DataFrame(bsc_rows))

        with tab_gap:
            fig, ax = plt.subplots(figsize=(10, 4))
            x = np.arange(len(labels))
            ax.bar(x - 0.2, vals, 0.4, label='Actual', color='#1E88E5')
            ax.bar(x + 0.2, targets, 0.4, label='Meta', color='#CFD8DC')
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=45)
            ax.legend()
            st.pyplot(fig)

        with tab_radar:
            N = len(labels)
            angles = [n / float(N) * 2 * np.pi for n in range(N)]
            angles += angles[:1]
            fig_r, ax_r = plt.subplots(subplot_kw=dict(polar=True))
            ax_r.plot(angles, targets + targets[:1], 'r--', alpha=0.3)
            ax_r.plot(angles, vals + vals[:1], 'b-')
            ax_r.set_xticks(angles[:-1])
            ax_r.set_xticklabels(labels)
            st.pyplot(fig_r)

    with col_ctrl:
        st.subheader("Decisiones")
        st.metric("Presupuesto", f"${st.session_state.presupuesto}M")
        
        opcion = st.selectbox("Seleccionar Acción:", list(DECISIONES.keys()))
        info = DECISIONES[opcion]
        
        if st.button("Aplicar Inversión", use_container_width=True):
            if st.session_state.presupuesto >= info['costo']:
                st.session_state.presupuesto -= info['costo']
                for p, impacts in info['impacto'].items():
                    for k, v in impacts.items():
                        st.session_state.kpis[p][k]['actual'] += v
                st.success(f"Aplicado: {opcion}")
                st.rerun()
            else:
                st.error("Presupuesto insuficiente")

        if st.button("🔄 Reiniciar"):
            st.session_state.clear()
            st.rerun()
