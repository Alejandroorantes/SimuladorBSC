import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import copy

# Configuración de página - Debe ser la primera instrucción de Streamlit
st.set_page_config(page_title="Simulador Estratégico BSC", layout="wide")

# --- DATOS GLOBAL: DECISIONES ---
if 'DECISIONES' not in st.session_state:
    st.session_state.DECISIONES = {
        1: {
            "nombre": "Automatización Industrial",
            "descripcion": "Inversión en robótica y sensores para la planta.",
            "costo": 5.0,
            "impacto": {
                "Financiera": {"ROI": 1.0, "Margen EBITDA": 2.5},
                "Procesos": {"Eficiencia OEE": 12.0, "Tiempo Ciclo": -3.0}
            }
        },
        2: {
            "nombre": "Programa de Lealtad Digital",
            "descripcion": "Desarrollo de APP y CRM para retención de clientes.",
            "costo": 3.0,
            "impacto": {
                "Clientes": {"Satisfacción (NPS)": 15.0, "Cuota Mercado": 4.0},
                "Financiera": {"Margen EBITDA": -0.5}
            }
        },
        3: {
            "nombre": "Capacitación Agile & Lean",
            "descripcion": "Entrenamiento intensivo para personal operativo.",
            "costo": 2.0,
            "impacto": {
                "Aprendizaje": {"Capacitación": 20.0, "Índice Innovación": 2.0},
                "Procesos": {"Eficiencia OEE": 5.0}
            }
        }
    }

# --- INICIALIZACIÓN DE ESTADO ---
if 'paso' not in st.session_state:
    st.session_state.paso = 1
if 'presupuesto' not in st.session_state:
    st.session_state.presupuesto = 20.0
if 'kpis' not in st.session_state:
    st.session_state.kpis = {
        "Financiera": {
            "ROI": {"actual": 8.0, "min": 7.0, "medio": 10.0, "ideal": 15.0, "unit": "%"},
            "Margen EBITDA": {"actual": 12.0, "min": 10.0, "medio": 14.0, "ideal": 18.0, "unit": "%"}
        },
        "Clientes": {
            "Satisfacción (NPS)": {"actual": 65.0, "min": 60.0, "medio": 75.0, "ideal": 90.0, "unit": "pts"},
            "Cuota Mercado": {"actual": 15.0, "min": 14.0, "medio": 18.0, "ideal": 25.0, "unit": "%"}
        },
        "Procesos": {
            "Eficiencia OEE": {"actual": 70.0, "min": 68.0, "medio": 80.0, "ideal": 90.0, "unit": "%"},
            "Tiempo Ciclo": {"actual": 15.0, "min": 16.0, "medio": 12.0, "ideal": 8.0, "unit": "días"}
        },
        "Aprendizaje": {
            "Índice Innovación": {"actual": 3.0, "min": 2.0, "medio": 5.0, "ideal": 9.0, "unit": "proy"},
            "Capacitación": {"actual": 20.0, "min": 15.0, "medio": 35.0, "ideal": 55.0, "unit": "hrs"}
        }
    }
    st.session_state.initial_kpis = copy.deepcopy(st.session_state.kpis)
if 'resumen_impacto' not in st.session_state:
    st.session_state.resumen_impacto = None

# --- FUNCIONES DE APOYO ---
def aplicar_decision(d_id):
    decision = st.session_state.DECISIONES[d_id]
    if st.session_state.presupuesto >= decision['costo']:
        before = copy.deepcopy(st.session_state.kpis)
        st.session_state.presupuesto -= decision['costo']
        
        for cat, impacts in decision['impacto'].items():
            for kpi, val in impacts.items():
                st.session_state.kpis[cat][kpi]['actual'] = round(st.session_state.kpis[cat][kpi]['actual'] + val, 2)
        
        st.session_state.resumen_impacto = {"nombre": decision['nombre'], "costo": decision['costo']}
        st.success(f"¡Decisión '{decision['nombre']}' aplicada con éxito!")
    else:
        st.error("Presupuesto insuficiente para esta acción.")

# --- INTERFAZ ---
with st.sidebar:
    st.header("📝 Diagnóstico Estratégico")
    if st.session_state.paso == 1:
        st.session_state.empresa = st.text_input("Empresa:", "Empresa Global")
        st.session_state.industria = st.selectbox("Industria:", ['Manufactura/CPG', 'Servicios', 'Tecnología', 'Retail'])
        st.text_area("Canvas (VP):", placeholder="Describe tu propuesta de valor...")
        if st.button("Siguiente: Play to Win"):
            st.session_state.paso = 2
            st.rerun()
    
    elif st.session_state.paso == 2:
        st.subheader("Fase: Play to Win")
        st.session_state.donde = st.text_input("¿Dónde jugar?", placeholder="Mercados, canales...")
        st.session_state.como = st.text_input("¿Cómo ganar?", placeholder="Estrategia de diferenciación...")
        if st.button("Generar Simulador"):
            st.session_state.paso = 3
            st.rerun()
        if st.button("Volver"):
            st.session_state.paso = 1
            st.rerun()

# PANEL PRINCIPAL (Simulador)
if st.session_state.paso == 3:
    st.title(f"Tablero de Control: {st.session_state.empresa}")
    st.info(f"**Estrategia:** Ganaremos en *{st.session_state.donde}* mediante *{st.session_state.como}*")
    
    col_visual, col_control = st.columns([2, 1])

    with col_visual:
        tab_matriz, tab_gap, tab_radar = st.tabs(["📋 Matriz BSC", "📊 Análisis de Brechas", "🕸 Radar de Balance"])
        
        # Preparación de datos comunes
        labels, vals, targets = [], [], []
        data_rows = []
        for p, kpis in st.session_state.kpis.items():
            for k, d in kpis.items():
                data_rows.append({"Perspectiva": p, "KPI": k, "Actual": d['actual'], "Ideal": d['ideal'], "Und": d['unit']})
                labels.append(k)
                vals.append(d['actual'])
                targets.append(d['ideal'])

        with tab_matriz:
            st.table(pd.DataFrame(data_rows))

        with tab_gap:
            fig_gap, ax_gap = plt.subplots(figsize=(10, 5))
            x = np.arange(len(labels))
            ax_gap.bar(x - 0.2, vals, 0.4, label='Estado Actual', color='#1E88E5')
            ax_gap.bar(x + 0.2, targets, 0.4, label='Meta Ideal', color='#E53935', alpha=0.3)
            ax_gap.set_xticks(x)
            ax_gap.set_xticklabels(labels, rotation=45, ha='right')
            ax_gap.legend()
            st.pyplot(fig_gap)

        with tab_radar:
            N = len(labels)
            angles = [n / float(N) * 2 * np.pi for n in range(N)]
            angles += angles[:1]
            v_radar = vals + vals[:1]
            t_radar = targets + targets[:1]
            
            fig_rad, ax_rad = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
            ax_rad.plot(angles, t_radar, color='red', linestyle='dashed', alpha=0.4, label="Meta")
            ax_rad.fill(angles, t_radar, color='red', alpha=0.1)
            ax_rad.plot(angles, v_radar, color='blue', linewidth=2, label="Actual")
            ax_rad.fill(angles, v_radar, color='blue', alpha=0.2)
            ax_rad.set_xticks(angles[:-1])
            ax_rad.set_xticklabels(labels)
            st.pyplot(fig_rad)

    with col_control:
        st.subheader("Decision Making")
        st.metric("Presupuesto USD", f"${st.session_state.presupuesto}M")
        
        opciones = {d['nombre']: k for k, d in st.session_state.DECISIONES.items()}
        seleccion = st.selectbox("Elegir Iniciativa:", options=list(opciones.keys()))
        
        if st.button("Ejecutar Acción", use_container_width=True):
            aplicar_decision(opciones[seleccion])
            st.rerun()
            
        st.divider()
        if st.button("🔄 Reiniciar Todo", type="secondary", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    if st.session_state.resumen_impacto:
        st.toast(f"Última acción: {st.session_state.resumen_impacto['nombre']}")
