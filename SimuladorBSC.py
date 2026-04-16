import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import copy

# --- DATOS GLOBAL: DECISIONES ---
# He incluido aquí la variable global que tu código mencionaba como externa
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
        # Guardar estado previo para el resumen
        before = copy.deepcopy(st.session_state.kpis)
        st.session_state.presupuesto -= decision['costo']
        
        # Aplicar impacto
        for cat, impacts in decision['impacto'].items():
            for kpi, val in impacts.items():
                st.session_state.kpis[cat][kpi]['actual'] = round(st.session_state.kpis[cat][kpi]['actual'] + val, 2)
        
        st.session_state.resumen_impacto = {"nombre": decision['nombre'], "costo": decision['costo'], "before": before}
    else:
        st.error("Presupuesto insuficiente")

# --- INTERFAZ ---

# PASO 1 Y 2: DIAGNÓSTICO (En la barra lateral para dejar espacio al simulador)
with st.sidebar:
    st.header("📝 Diagnóstico Estratégico")
    if st.session_state.paso == 1:
        st.session_state.empresa = st.text_input("Empresa:", "Nombre")
        st.session_state.industria = st.selectbox("Industria:", ['Manufactura/CPG', 'Servicios', 'Tecnología', 'Retail'])
        st.text_area("Canvas (VP):")
        st.text_area("Cadena Valor:")
        st.text_area("FODA/PESTEL:")
        if st.button("Siguiente: Play to Win"):
            st.session_state.paso = 2
            st.rerun()
    
    elif st.session_state.paso == 2:
        st.subheader("Play to Win")
        st.session_state.donde = st.text_input("¿Dónde jugar?", "Mercado...")
        st.session_state.como = st.text_input("¿Cómo ganar?", "Diferenciación...")
        st.text_area("Capacidades:")
        if st.button("Generar Simulador"):
            st.session_state.paso = 3
            st.rerun()
        if st.button("Volver"):
            st.session_state.paso = 1
            st.rerun()

# PASO 3: EL SIMULADOR (Panel Principal)
if st.session_state.paso == 3:
    st.title(f"Tablero de Control: {st.session_state.empresa}")
    st.markdown(f"**Estrategia:** Ganaremos en *{st.session_state.donde}* mediante *{st.session_state.como}*")
    
    col_kpi, col_dec = st.columns([2, 1])

    with col_kpi:
        st.subheader("Visualización del BSC")
        vistas = st.tabs(["📋 Matriz", "📊 Barras (Gap)", "🕸 Radar"])
        
        # Recopilar datos para tablas/gráficos
        data_rows = []
        labels, vals, targets = [], [], []
        for p, kpis in st.session_state.kpis.items():
            for k, d in kpis.items():
                data_rows.append({"Perspectiva": p, "KPI": k, "Actual": d['actual'], "Ideal": d['ideal'], "Unidad": d['unit']})
                labels.append(k)
                vals.append(d['actual'])
                targets.append(d['ideal'])

        with vistas[0]:
            st.table(pd.DataFrame(data_rows))
        
        with vistas[1]:
            fig, ax = plt.subplots(figsize=(10, 5))
            x = np.arange(len(labels))
            ax.bar(x - 0.2, vals, 0.4, label='Actual', color='skyblue')
            ax.bar(x + 0.2, targets, 0.4, label='Ideal', color='lightcoral', alpha=0.7)
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=45, ha='right')
            ax.legend()
            st.pyplot(fig)

        with vistas[2]:
            # Lógica de Radar
            N = len(labels)
            angles = [n / float(N) * 2 * np.pi for n in range(N)]
            angles += angles[:1]
            v_radar = vals + vals[:1]
            t_radar = targets + targets[:1]
            
            fig_rad = plt.figure(figsize=(6,6))
            ax_rad = plt.subplot(111, polar=True)
            ax_rad.plot(angles, t_radar, 'r', alpha=0.3, label="Ideal")
            ax_rad.fill(angles, t_radar, 'r', alpha=0.1)
            ax_rad.plot(angles, v_radar, 'b', label="Actual")
            ax_rad.fill(angles, v_radar, 'b', alpha=0.2)
            ax_rad.set_xticks(angles[:-1])
            ax_rad.set_xticklabels(labels)
            st.pyplot(fig_rad)

    with col_dec:
        st.subheader("Decisiones")
        st.metric("Presupuesto Disponible", f"${st.session_state.presupuesto}M")
        
        opciones = {d['nombre']: k for k, d in st.session_state.DECISIONES.items()}
        seleccion = st.selectbox("Seleccionar Acción:", options=list(opciones.keys()))
        
        if st.button("Aplicar Decisión Strategic", use_container_width=True):
            aplicar_decision(opciones[seleccion])
            st.rerun()
            
        if st.button("🔄 Resetear Todo", type="secondary"):
            st.session_state.kpis = copy.deepcopy(st.session_state.initial_kpis)
            st.session_state.presupuesto = 20.0
            st.session_state.resumen_impacto = None
            st.rerun()

    # RESUMEN DE IMPACTO (Debajo de todo)
    if st.session_state.resumen_impacto:
        st.divider()
        res = st.session_state.resumen_impacto
        st.info(f"**Último Impacto:** {res['nombre']} (Costo: ${res['costo']}M)")
        # Aquí podrías generar una pequeña tabla comparativa del cambio actual
