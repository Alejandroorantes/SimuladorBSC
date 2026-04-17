import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Configuración inicial
st.set_page_config(page_title="Simulador de Estrategia Alex", layout="wide")

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
    st.session_state.diagnostico_texto = ""
    st.session_state.empresa = ""
    st.session_state.industria = ""
    st.session_state.datos_f1 = {} 
    st.session_state.kpis = {
        "Financiera": {
            "ROI": {"actual": 8.0, "ideal": 15.0},
            "Margen EBITDA": {"actual": 12.0, "ideal": 18.0}
        },
        "Clientes": {
            "Satisfacción (NPS)": {"actual": 65.0, "ideal": 90.0},
            "Cuota Mercado": {"actual": 15.0, "ideal": 25.0}
        },
        "Procesos": {
            "Eficiencia OEE": {"actual": 70.0, "ideal": 90.0},
            "Tiempo Ciclo": {"actual": 15.0, "ideal": 8.0}
        },
        "Aprendizaje": {
            "Índice Innovación": {"actual": 3.0, "ideal": 9.0},
            "Capacitación": {"actual": 20.0, "ideal": 55.0}
        }
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

# --- NAVEGACIÓN ---

# FASE 1: DIAGNÓSTICO
if st.session_state.paso == 1:
    st.title("Fase 1: Diagnóstico Integral de Negocio")
    with st.form("diagnostico_form"):
        col_id1, col_id2 = st.columns(2)
        with col_id1:
            empresa_input = st.text_input("Nombre de la Organización:")
        with col_id2:
            industria_input = st.selectbox("Industria:", ["Manufactura", "Servicios", "Bancario","Agroindustria","Alimentos y Bebidas","Tecnología", "Retail"])
        
        st.subheader("I. Arquitectura de Negocio (Canvas)")
        c1, c2 = st.columns(2)
        with c1:
            vp = st.text_area("Propuesta de Valor:")
            proc = st.text_area("Procesos Clave:")
        with c2:
            recursos = st.text_area("Recursos Clave:")
            socios = st.text_area("Socios Clave:")
            
        st.subheader("II. Análisis FODA Estructurado")
        f1, f2 = st.columns(2)
        with f1:
            fort = st.text_area("Fortalezas:")
            opp = st.text_area("Oportunidades:")
        with f2:
            deb = st.text_area("Debilidades:")
            ame = st.text_area("Amenazas:")
        
        if st.form_submit_button("Siguiente"):
            if empresa_input:
                st.session_state.empresa = empresa_input
                st.session_state.industria = industria_input
                st.session_state.datos_f1 = {
                    "Propuesta de Valor": vp, "Procesos Clave": proc, 
                    "Recursos Clave": recursos, "Socios Clave": socios,
                    "Fortalezas": fort, "Oportunidades": opp, 
                    "Debilidades": deb, "Amenazas": ame
                }
                st.session_state.diagnostico_texto = f"{vp} {proc} {recursos} {socios} {fort} {opp} {deb} {ame}"
                st.session_state.paso = 2
                st.rerun()
            else:
                st.error("Por favor ingresa el nombre de la empresa.")

# FASE 2: ESTRATEGIA
elif st.session_state.paso == 2:
    st.title("Fase 2: Estrategia Play to Win")
    with st.form("estrategia_form"):
        donde = st.text_input("¿Dónde jugar?")
        como = st.text_input("¿Cómo ganar?")
        que = st.text_input("¿Qué capacidades deben estar presentes?")
        if st.form_submit_button("Iniciar Simulador"):
            st.session_state.donde = donde
            st.session_state.como = como
            st.session_state.como = que
            st.session_state.paso = 3
            st.rerun()

# FASE 3: SIMULADOR
elif st.session_state.paso == 3:
    st.title(f"Tablero de Control: {st.session_state.empresa}")
    col_vis, col_ctrl = st.columns([2, 1])

    with col_vis:
        t_matriz, t_gap, t_hist = st.tabs(["📋 Matriz BSC", "📊 Análisis Gaps", "📜 Historial"])
        
        rows = []
        labels, vals, targets = [], [], []
        for p, kpis in st.session_state.kpis.items():
            for k, d in kpis.items():
                labels.append(k)
                vals.append(d['actual'])
                targets.append(d['ideal'])
                status = "🟢" if d['actual'] >= d['ideal'] else "🟡" if d['actual'] >= (d['ideal']*0.8) else "🔴"
                rows.append({"Estado": status, "Perspectiva": p, "KPI": k, "Actual": d['actual'], "Meta": d['ideal']})
        
        with t_matriz: st.table(pd.DataFrame(rows))
        with t_gap:
            fig, ax = plt.subplots(figsize=(10, 4))
            x = np.arange(len(labels))
            ax.bar(x - 0.2, vals, 0.4, label='Actual', color='#007bff')
            ax.bar(x + 0.2, targets, 0.4, label='Meta', color='#e9ecef', alpha=0.5)
            ax.set_xticks(x); ax.set_xticklabels(labels, rotation=45); ax.legend()
            st.pyplot(fig)
        with t_hist: 
            if st.session_state.historial: st.table(pd.DataFrame(st.session_state.historial))
            else: st.info("No hay inversiones registradas.")

    with col_ctrl:
        st.subheader("Simulación")
        st.metric("Presupuesto Disponible", f"${round(st.session_state.presupuesto, 2)}M")
        seleccion = st.selectbox("Elegir Iniciativa:", list(DECISIONES.keys()))
        
        if st.button("Ejecutar Inversión", use_container_width=True):
            info = DECISIONES[seleccion]
            if st.session_state.presupuesto >= info['costo']:
                mod = calcular_modificador(st.session_state.diagnostico_texto, seleccion)
                st.session_state.presupuesto -= info['costo']
                
                detalles = []
                for p, k_impacts in info['impacto'].items():
                    for kpi_nom, val in k_impacts.items():
                        v_final = round(val * mod, 2)
                        st.session_state.kpis[p][kpi_nom]['actual'] = round(st.session_state.kpis[p][kpi_nom]['actual'] + v_final, 2)
                        detalles.append({"KPI": kpi_nom, "Impacto": f"+{v_final}" if v_final > 0 else f"{v_final}"})
                
                st.session_state.ultimo_impacto = detalles
                st.session_state.historial.append({"Iniciativa": seleccion, "Costo": f"${info['costo']}M", "Coherencia": "Alta (Bono)" if mod > 1 else "Normal"})
                st.rerun()
            else: st.error("Presupuesto insuficiente")

        if st.session_state.ultimo_impacto:
            st.write("**Impacto de la última decisión:**")
            st.dataframe(pd.DataFrame(st.session_state.ultimo_impacto), hide_index=True)

        st.divider()
        if st.button("📊 GENERAR REPORTE FINAL", type="primary", use_container_width=True):
            st.session_state.paso = 4
            st.rerun()
        if st.button("🔄 Reiniciar"):
            st.session_state.clear()
            st.rerun()

# FASE 4: REPORTE FINAL ACTUALIZADA
elif st.session_state.paso == 4:
    st.title("Reporte Estratégico Final")
    
    # 1. Nombre de la persona
    st.subheader("I. Información del Participante")
    nombre_participante = st.text_input("Nombre completo de quien completó la simulación:")
    
    st.header(f"Organización: {st.session_state.empresa} | Industria: {st.session_state.industria}")
    
    # SECCIÓN DE RESUMEN
    st.markdown("---")
    st.subheader("II. Resumen del Diagnóstico")
    col_rep_a, col_rep_b = st.columns(2)
    with col_rep_a:
        st.markdown("**Arquitectura de Negocio (Canvas)**")
        for key in ["Propuesta de Valor", "Procesos Clave", "Recursos Clave", "Socios Clave"]:
            st.info(f"**{key}:** {st.session_state.datos_f1.get(key, 'N/A')}")
    with col_rep_b:
        st.markdown("**Análisis FODA**")
        for key in ["Fortalezas", "Oportunidades", "Debilidades", "Amenazas"]:
            st.warning(f"**{key}:** {st.session_state.datos_f1.get(key, 'N/A')}")

    st.markdown("---")
    st.subheader("III. Estrategia y Resultados Obtenidos")
    st.success(f"**Estrategia:** {st.session_state.como} en {st.session_state.donde}")
    
    # KPIs Finales
    final_rows = []
    for p, kpis in st.session_state.kpis.items():
        for k, d in kpis.items():
            final_rows.append({"Perspectiva": p, "KPI": k, "Resultado": d['actual'], "Meta": d['ideal']})
    st.table(pd.DataFrame(final_rows))
    
    # Inversiones
    st.subheader("IV. Historial de Decisiones")
    if st.session_state.historial: st.table(pd.DataFrame(st.session_state.historial))
    
    # 2. Análisis de Aprendizaje
    st.markdown("---")
    st.subheader("V. Análisis de Aprendizaje y Reflexión Estratégica")
    st.write("Con base en la mezcla de tu estrategia inicial, las decisiones de inversión tomadas y los resultados en los KPIs:")
    analisis_aprendizaje = st.text_area(
        "Describe tu análisis: ¿Qué relación observas entre tus inversiones y los resultados? ¿Qué harías diferente a futuro para mejorar el desempeño?",
        height=200,
        placeholder="Escribe aquí tu reflexión..."
    )
    
    col_fin1, col_fin2 = st.columns(2)
    with col_fin1:
        if st.button("Volver al Simulador"):
            st.session_state.paso = 3
            st.rerun()
    with col_fin2:
        if st.button("Finalizar Actividad"):
            st.balloons()
            st.success("¡Simulación y Reporte Completados con Éxito!")
