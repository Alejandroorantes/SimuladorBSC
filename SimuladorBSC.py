import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import copy

# Configuración inicial
st.set_page_config(page_title="Simulador de Estrategia Digital y Negocios", layout="wide")

# --- ESTADO DE SESIÓN (Persistencia de datos) ---
if 'paso' not in st.session_state:
    st.session_state.paso = 1
    st.session_state.presupuesto = 20.0
    st.session_state.historial = []
    st.session_state.diagnostico = {}
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

DECISIONES = {
    "Transformación Digital Core": {"costo": 7.0, "impacto": {"Procesos": {"Eficiencia OEE": 15, "Tiempo Ciclo": -4}, "Aprendizaje": {"Índice Innovación": 2}}},
    "Marketing Automation & CRM": {"costo": 4.0, "impacto": {"Clientes": {"Satisfacción (NPS)": 12, "Cuota Mercado": 5}, "Financiera": {"ROI": 1}}},
    "Ciberseguridad y Resiliencia": {"costo": 3.0, "impacto": {"Procesos": {"Eficiencia OEE": 5}, "Financiera": {"Margen EBITDA": -1}}},
    "Upskilling Talento Tech": {"costo": 2.5, "impacto": {"Aprendizaje": {"Capacitación": 25, "Índice Innovación": 3}, "Procesos": {"Eficiencia OEE": 3}}},
    "Expansión E-commerce Global": {"costo": 6.0, "impacto": {"Clientes": {"Cuota Mercado": 8}, "Financiera": {"ROI": 3, "Margen EBITDA": 2}}}
}

# --- FUNCIONES ---
def aplicar_cambio(nombre_accion):
    accion = DECISIONES[nombre_accion]
    if st.session_state.presupuesto >= accion['costo']:
        cambios = []
        st.session_state.presupuesto -= accion['costo']
        for cat, kpis in accion['impacto'].items():
            for kpi, val in kpis.items():
                st.session_state.kpis[cat][kpi]['actual'] += val
                cambios.append(f"{kpi}: {'+' if val>0 else ''}{val}")
        
        st.session_state.historial.append({
            "Acción": nombre_accion,
            "Costo": f"${accion['costo']}M",
            "Impacto": ", ".join(cambios)
        })
        st.success(f"Ejecutado: {nombre_accion}")
    else:
        st.error("Presupuesto insuficiente")

# --- NAVEGACIÓN ---
if st.session_state.paso == 1:
    st.title("🛡️ Fase 1: Diagnóstico de Modelo de Negocio")
    with st.form("f1"):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Business Model Canvas")
            st.session_state.diagnostico['empresa'] = st.text_input("Nombre de la Organización", "Mi Empresa")
            st.session_state.diagnostico['vp'] = st.text_area("Propuesta de Valor (¿Qué nos hace únicos?)")
            st.session_state.diagnostico['segmentos'] = st.text_area("Segmentos de Cliente")
        with col2:
            st.subheader("Análisis FODA")
            st.session_state.diagnostico['fortalezas'] = st.text_area("Fortalezas y Oportunidades")
            st.session_state.diagnostico['debilidades'] = st.text_area("Debilidades y Amenazas")
        
        if st.form_submit_button("Siguiente: Definir Estrategia"):
            st.session_state.paso = 2
            st.rerun()

elif st.session_state.paso == 2:
    st.title("🎯 Fase 2: Play to Win")
    with st.form("f2"):
        st.session_state.diagnostico['donde'] = st.text_input("¿Dónde jugar? (Mercado, Geografía, Canales)")
        st.session_state.diagnostico['como'] = st.text_input("¿Cómo ganar? (Estrategia de diferenciación o costos)")
        st.session_state.diagnostico['capacidades'] = st.text_area("Capacidades necesarias (Sistemas, Talento)")
        
        if st.form_submit_button("Generar Simulador y BSC"):
            st.session_state.paso = 3
            st.rerun()

elif st.session_state.paso == 3:
    st.title(f"🚀 Tablero Estratégico: {st.session_state.diagnostico['empresa']}")
    
    # Resumen Estratégico (Header)
    with st.expander("📄 Ver Resumen Estratégico Completo", expanded=False):
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"**Propuesta:** {st.session_state.diagnostico['vp']}")
        c2.markdown(f"**Dónde Jugar:** {st.session_state.diagnostico['donde']}")
        c3.markdown(f"**Cómo Ganar:** {st.session_state.diagnostico['como']}")

    col_main, col_side = st.columns([2, 1])

    with col_main:
        tabs = st.tabs(["📋 Matriz BSC", "📊 Comparativa Gaps", "🕸 Radar Balance", "📜 Historial de Impacto"])
        
        # Preparación de datos
        labels, vals, goals = [], [], []
        bsc_data = []
        for cat, kpis in st.session_state.kpis.items():
            for k, d in kpis.items():
                labels.append(k)
                vals.append(d['actual'])
                goals.append(d['ideal'])
                # Lógica de semáforo
                status = "🟢" if d['actual'] >= d['ideal'] else "🟡" if d['actual'] >= (d['ideal']*0.8) else "🔴"
                bsc_data.append([status, cat, k, d['actual'], d['ideal'], d['unit']])

        with tabs[0]:
            st.subheader("Balanced Scorecard (Matriz)")
            df_bsc = pd.DataFrame(bsc_data, columns=["Estado", "Perspectiva", "Indicador", "Actual", "Meta", "Unidad"])
            st.table(df_bsc)

        with tabs[1]:
            fig, ax = plt.subplots(figsize=(10, 5))
            x = np.arange(len(labels))
            ax.bar(x - 0.2, vals, 0.4, label='Actual', color='#007bff')
            ax.bar(x + 0.2, goals, 0.4, label='Meta', color='#cccccc', alpha=0.5)
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=45)
            ax.legend()
            st.pyplot(fig)

        with tabs[2]:
            N = len(labels)
            angles = [n / float(N) * 2 * np.pi for n in range(N)]
            angles += angles[:1]
            fig_r, ax_r = plt.subplots(subplot_kw=dict(polar=True))
            ax_r.plot(angles, goals + goals[:1], 'r--', alpha=0.3, label="Ideal")
            ax_r.plot(angles, vals + vals[:1], 'b-', linewidth=2, label="Actual")
            ax_r.fill(angles, vals + vals[:1], 'b', alpha=0.1)
            ax_r.set_xticks(angles[:-1])
            ax_r.set_xticklabels(labels)
            st.pyplot(fig_r)

        with tabs[3]:
            if st.session_state.historial:
                st.table(pd.DataFrame(st.session_state.historial))
            else:
                st.write("No se han tomado decisiones aún.")

    with col_side:
        st.subheader("Panel de Decisiones")
        st.metric("Presupuesto Disponible", f"${st.session_state.presupuesto}M")
        
        sel = st.selectbox("Seleccione Iniciativa:", list(DECISIONES.keys()))
        costo = DECISIONES[sel]['costo']
        st.write(f"**Inversión requerida:** ${costo}M")
        
        if st.button("Ejecutar Inversión", use_container_width=True):
            aplicar_cambio(sel)
            st.rerun()

        st.divider()
        if st.button("🔄 Reiniciar Simulación", type="secondary"):
            st.session_state.clear()
            st.rerun()
