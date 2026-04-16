import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import copy

# Configuración inicial
st.set_page_config(page_title="Simulador de Estrategia Pro", layout="wide")

# --- MOTOR DE COHERENCIA (Lógica de Negocio) ---
def calcular_modificador(texto_diagnostico, accion):
    """Analiza si la acción del usuario coincide con lo redactado en el diagnóstico"""
    texto = texto_diagnostico.lower()
    # Mapeo de palabras clave por decisión
    keywords = {
        "1. Automatización Robótica (RPA/AI)": ["procesos", "eficiencia", "costos", "manual", "lento"],
        "2. Programa de Lealtad Omnicanal": ["clientes", "nps", "fidelidad", "ventas", "servicio"],
        "3. I+D: Productos Sustentables": ["innovacion", "producto", "verde", "sustentable", "futuro"],
        "4. Reskilling de Talento Digital": ["talento", "capacitacion", "gente", "personas", "habilidades"],
        "5. Expansión a Mercados Emergentes": ["crecimiento", "mercado", "global", "ventas", "nuevo"],
        "6. Smart Logistics (Supply Chain)": ["logistica", "entrega", "inventario", "cadena", "transporte"],
        "7. Ciberseguridad y Cloud": ["riesgo", "seguridad", "datos", "nube", "ataque"]
    }
    
    # Si encuentra una palabra clave del diagnóstico en la acción seleccionada, da un bono
    if any(word in texto for word in keywords.get(accion, [])):
        return 1.2  # +20% de impacto por coherencia estratégica
    return 1.0

# --- INICIALIZACIÓN ---
if 'paso' not in st.session_state:
    st.session_state.paso = 1
    st.session_state.presupuesto = 20.0
    st.session_state.historial = []
    st.session_state.ultimo_impacto = None
    st.session_state.diagnostico_texto = "" # Para el motor de coherencia
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
    "1. Automatización Robótica (RPA/AI)": {"costo": 5.5, "impacto": {"Procesos": {"Eficiencia OEE": 12.0, "Tiempo Ciclo": -3.0}, "Financiera": {"Margen EBITDA": 2.5}}},
    "2. Programa de Lealtad Omnicanal": {"costo": 3.5, "impacto": {"Clientes": {"Satisfacción (NPS)": 18.0, "Cuota Mercado": 4.0}, "Financiera": {"Margen EBITDA": -0.5}}},
    "3. I+D: Productos Sustentables": {"costo": 6.5, "impacto": {"Aprendizaje": {"Índice Innovación": 5.0}, "Clientes": {"Cuota Mercado": 6.0}, "Financiera": {"ROI": -1.5}}},
    "4. Reskilling de Talento Digital": {"costo": 2.5, "impacto": {"Aprendizaje": {"Capacitación": 25.0, "Índice Innovación": 2.0}, "Procesos": {"Eficiencia OEE": 4.0}}},
    "5. Expansión a Mercados Emergentes": {"costo": 7.5, "impacto": {"Clientes": {"Cuota Mercado": 10.0}, "Financiera": {"ROI": 4.0}, "Procesos": {"Tiempo Ciclo": 2.0}}},
    "6. Smart Logistics (Supply Chain)": {"costo": 4.0, "impacto": {"Procesos": {"Tiempo Ciclo": -4.0}, "Financiera": {"Margen EBITDA": 3.0}}},
    "7. Ciberseguridad y Cloud": {"costo": 3.0, "impacto": {"Procesos": {"Eficiencia OEE": 5.0}, "Aprendizaje": {"Índice Innovación": 1.0}}}
}

# --- NAVEGACIÓN ---
if st.session_state.paso == 1:
    st.title("Fase 1: Diagnóstico y Recolección de Datos")
    with st.form("f1"):
        st.session_state.empresa = st.text_input("Empresa:", "")
        st.session_state.industria = st.selectbox("Industria:", ['Manufactura', 'Servicios', 'Tecnología', 'Retail'])
        st.session_state.diagnostico['vp'] = st.text_area("Propuesta de Valor (Canvas):")
        foda_txt = st.text_area("Describa su FODA (Fortalezas, Oportunidades, Debilidades, Amenazas):", placeholder="Ej: Nuestra debilidad es el talento digital...")
        if st.form_submit_button("Siguiente"):
            st.session_state.diagnostico_texto = foda_txt + " " + st.session_state.diagnostico['vp']
            st.session_state.paso = 2
            st.rerun()

elif st.session_state.paso == 2:
    st.title("Fase 2: Estrategia Play to Win")
    with st.form("f2"):
        st.session_state.donde = st.text_input("¿Dónde jugar?")
        st.session_state.como = st.text_input("¿Cómo ganar?")
        if st.form_submit_button("Iniciar Simulador"):
            st.session_state.paso = 3
            st.rerun()

elif st.session_state.paso == 3:
    st.title(f"Simulador: {st.session_state.empresa}")
    col_vis, col_ctrl = st.columns([2, 1])

    with col_vis:
        t_matriz, t_gap, t_radar, t_hist = st.tabs(["📋 Matriz BSC", "📊 Gaps", "🕸 Radar", "📜 Historial"])
        
        # Generar datos para tablas y gráficos
        labels, vals, targets, rows = [], [], [], []
        for p, k_dict in st.session_state.kpis.items():
            for k, d in k_dict.items():
                labels.append(k)
                vals.append(d['actual'])
                targets.append(d['ideal'])
                status = "🟢" if d['actual'] >= d['ideal'] else "🟡" if d['actual'] >= (d['ideal']*0.8) else "🔴"
                rows.append({"Estado": status, "Perspectiva": p, "KPI": k, "Actual": d['actual'], "Meta": d['ideal']})
        
        with t_matriz: st.table(pd.DataFrame(rows))
        with t_gap:
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.bar(np.arange(len(labels))-0.2, vals, 0.4, label="Actual")
            ax.bar(np.arange(len(labels))+0.2, targets, 0.4, alpha=0.3, label="Meta")
            ax.set_xticks(np.arange(len(labels))); ax.set_xticklabels(labels, rotation=45)
            st.pyplot(fig)
        with t_radar:
            # Lógica simplificada de radar
            st.write("Visualización Radar activa.")
        with t_hist: st.table(pd.DataFrame(st.session_state.historial)) if st.session_state.historial else st.write("Sin datos.")

    with col_ctrl:
        st.subheader("Panel de Decisiones")
        st.metric("Presupuesto", f"${round(st.session_state.presupuesto, 2)}M")
        sel = st.selectbox("Acción:", list(DECISIONES.keys()))
        
        if st.button("Invertir", use_container_width=True):
            info = DECISIONES[sel]
            if st.session_state.presupuesto >= info['costo']:
                mod = calcular_modificador(st.session_state.diagnostico_texto, sel)
                st.session_state.presupuesto -= info['costo']
                
                cambios = []
                for p, kpis in info['impacto'].items():
                    for k, v in kpis.items():
                        v_final = v * mod # Aplicación del modificador por coherencia
                        st.session_state.kpis[p][k]['actual'] = round(st.session_state.kpis[p][k]['actual'] + v_final, 2)
                        cambios.append({"KPI": k, "Impacto": f"{'+' if v_final>0 else ''}{v_final} ({'Bono Coherencia' if mod > 1 else 'Normal'})"})
                
                st.session_state.ultimo_impacto = cambios
                st.session_state.historial.append({"Acción": sel, "Costo": info['costo'], "Coherencia": "Alta" if mod > 1 else "Estándar"})
                st.rerun()
        
        if st.session_state.ultimo_impacto:
            st.write("**Último Impacto:**")
            st.dataframe(pd.DataFrame(st.session_state.ultimo_impacto), hide_index=True)

        st.divider()
        if st.button("📊 GENERAR REPORTE", type="primary", use_container_width=True):
            st.session_state.paso = 4
            st.rerun()

elif st.session_state.paso == 4:
    st.title("Reporte Final de Estrategia")
    st.header(f"Resultados para {st.session_state.empresa}")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Datos de Entrada")
        st.write(f"**Diagnóstico detectado:** {st.session_state.diagnostico_texto[:200]}...")
        st.write(f"**Estrategia:** {st.session_state.como}")
    with c2:
        st.subheader("Eficiencia Financiera")
        st.write(f"**Presupuesto Final:** ${round(st.session_state.presupuesto, 2)}M")
        puntos_logrados = sum(1 for p, k in st.session_state.kpis.items() for kpi, d in k.items() if d['actual'] >= d['ideal'])
        st.metric("Objetivos Cumplidos", f"{puntos_logrados} / 8")

    st.subheader("Historial de Coherencia")
    st.table(pd.DataFrame(st.session_state.historial))
    
    if st.button("Reiniciar Simulador"):
        st.session_state.clear()
        st.rerun()
