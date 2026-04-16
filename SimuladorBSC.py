import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import copy

# Configuración obligatoria al inicio
st.set_page_config(page_title="Simulador Estratégico Alex", layout="wide")

# --- INICIALIZACIÓN DE DATOS (Session State) ---
if 'DECISIONES' not in st.session_state:
    st.session_state.DECISIONES = {
        1: {
            "nombre": "Automatización Industrial",
            "costo": 5.0,
            "impacto": {"Procesos": {"Eficiencia OEE": 12.0}, "Financiera": {"Margen EBITDA": 2.5}}
        },
        2: {
            "nombre": "Programa de Lealtad Digital",
            "costo": 3.0,
            "impacto": {"Clientes": {"Satisfacción (NPS)": 15.0, "Cuota Mercado": 4.0}}
        },
        3: {
            "nombre": "Capacitación Agile & Lean",
            "costo": 2.0,
            "impacto": {"Aprendizaje": {"Capacitación": 20.0}, "Procesos": {"Eficiencia OEE": 5.0}}
        }
    }

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

# --- LÓGICA DE NEGOCIO ---
def ejecutar_accion(id_accion):
    accion = st.session_state.DECISIONES[id_accion]
    if st.session_state.presupuesto >= accion['costo']:
        st.session_state.presupuesto -= accion['costo']
        for cat, impactos in accion['impacto'].items():
            for kpi, valor in impactos.items():
                st.session_state.kpis[cat][kpi]['actual'] += valor
        st.success(f"Ejecutado: {accion['nombre']}")
    else:
        st.error("Presupuesto insuficiente")

# --- INTERFAZ ---
with st.sidebar:
    st.header("⚙️ Configuración")
    if st.session_state.paso < 3:
        if st.button("Saltar a Simulador"):
            st.session_state.paso = 3
            st.rerun()

if st.session_state.paso == 1:
    st.title("Fase 1: Diagnóstico")
    st.session_state.empresa = st.text_input("Nombre de la Empresa", "Energizer")
    if st.button("Siguiente"):
        st.session_state.paso = 2
        st.rerun()

elif st.session_state.paso == 2:
    st.title("Fase 2: Estrategia")
    st.session_state.donde = st.text_input("¿Dónde jugar?")
    st.session_state.como = st.text_input("¿Cómo ganar?")
    if st.button("Iniciar Simulador"):
        st.session_state.paso = 3
        st.rerun()

elif st.session_state.paso == 3:
    st.title(f"Tablero BSC: {st.session_state.get('empresa', 'Empresa')}")
    
    col_vis, col_ctrl = st.columns([2, 1])
    
    with col_vis:
        t1, t2 = st.tabs(["📊 Gráfico de Gaps", "🕸 Radar"])
        
        # Preparar datos
        labels, vals, targets = [], [], []
        for cat, kpis in st.session_state.kpis.items():
            for k, d in kpis.items():
                labels.append(k)
                vals.append(d['actual'])
                targets.append(d['ideal'])
        
        with t1:
            fig, ax = plt.subplots(figsize=(10, 4))
            x = np.arange(len(labels))
            ax.bar(x - 0.2, vals, 0.4, label='Actual', color='blue')
            ax.bar(x + 0.2, targets, 0.4, label='Meta', color='gray', alpha=0.3)
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=45)
            ax.legend()
            st.pyplot(fig)
            
        with t2:
            N = len(labels)
            angles = [n / float(N) * 2 * np.pi for n in range(N)]
            angles += angles[:1]
            fig_rad, ax_rad = plt.subplots(subplot_kw=dict(polar=True))
            ax_rad.plot(angles, targets + targets[:1], 'r--', alpha=0.3)
            ax_rad.plot(angles, vals + vals[:1], 'b-')
            ax_rad.set_xticks(angles[:-1])
            ax_rad.set_xticklabels(labels)
            st.pyplot(fig_rad)

    with col_ctrl:
        st.subheader("Simulación")
        st.metric("Presupuesto", f"${st.session_state.presupuesto}M")
        
        opciones = {d['nombre']: k for k, d in st.session_state.DECISIONES.items()}
        sel = st.selectbox("Iniciativa:", list(opciones.keys()))
        
        if st.button("Invertir"):
            ejecutar_accion(opciones[sel])
            st.rerun()
            
        if st.button("Reiniciar"):
            st.session_state.clear()
            st.rerun()
