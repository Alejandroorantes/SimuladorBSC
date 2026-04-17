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
        
        st.subheader("I. Arquitectura de Negocio (Canvas) y Autoevaluación")
        st.caption("Define cada elemento y selecciona si representa actualmente una Fortaleza o una Debilidad.")

        campos_canvas = ["Propuesta de Valor", "Procesos Clave", "Recursos Clave", "Socios Clave"]
        respuestas_canvas = {}

        for campo in campos_canvas:
            c_txt, c_tipo = st.columns([3, 1])
            with c_txt:
                txt = st.text_area(f"{campo}:", height=68, placeholder=f"Describe aquí tu {campo.lower()}...")
            with c_tipo:
                tipo = st.selectbox(f"Situación:", ["Fortaleza", "Debilidad"], key=f"tipo_{campo}")
            respuestas_canvas[campo] = {"texto": txt, "tipo": tipo}
            
        st.divider()
        st.subheader("II. Análisis del Entorno (FODA Externo)")
        f1, f2 = st.columns(2)
        with f1:
            opp = st.text_area("Oportunidades (Factores Externos Positivos):")
        with f2:
            ame = st.text_area("Amenazas (Factores Externos Negativos):")
        
        if st.form_submit_button("Siguiente"):
            if empresa_input:
                st.session_state.empresa = empresa_input
                st.session_state.industria = industria_input
                st.session_state.datos_f1 = {
                    "Canvas": respuestas_canvas,
                    "Oportunidades": opp,
                    "Amenazas": ame
                }
                # Consolidar texto para motor de coherencia
                st.session_state.diagnostico_texto = " ".join([v["texto"] for v in respuestas_canvas.values()]) + f" {opp} {ame}"
                st.session_state.paso = 2
                st.rerun()
            else:
                st.error("Por favor ingresa el nombre de la empresa.")

# FASE 2: ESTRATEGIA
elif st.session_state.paso == 2:
    st.title("Fase 2: Estrategia Play to Win")
    with st.form("estrategia_form"):
        aspiracion = st.text_input("¿Cuál es nuestra aspiración ganadora?") 
        donde = st.text_input("¿Dónde jugaremos?")
        como = st.text_input("¿Cómo ganaremos?")
        que = st.text_input("¿Qué capacidades deben estar presentes?")
        if st.form_submit_button("Iniciar Simulador"):
            st.session_state.aspiracion = aspiracion
            st.session_state.donde = donde
            st.session_state.como = como
            st.session_state.que = que
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
    
    st.subheader("I. Información del Participante")
    nombre_participante = st.text_input("Nombre completo de quien completó la simulación:")
    
    st.header(f"Organización: {st.session_state.empresa} | Industria: {st.session_state.industria}")
    
    st.markdown("---")
    st.subheader("II. Resumen del Diagnóstico (Canvas + Autoevaluación)")
    col_rep_a, col_rep_b = st.columns(2)
    with col_rep_a:
        st.markdown("**Arquitectura Interna**")
        for campo, info in st.session_state.datos_f1["Canvas"].items():
            icon = "💪" if info['tipo'] == "Fortaleza" else "⚠️"
            st.info(f"**{campo} ({icon} {info['tipo']}):** {info['texto']}")
    with col_rep_b:
        st.markdown("**Análisis Externo**")
        st.warning(f"**Oportunidades:** {st.session_state.datos_f1['Oportunidades']}")
        st.error(f"**Amenazas:** {st.session_state.datos_f1['Amenazas']}")

    st.markdown("---")
    st.subheader("III. Estrategia y Resultados Obtenidos")
    frase_integrada = (
        f"Nuestra aspiración es **{st.session_state.aspiracion}**, "
        f"enfocándonos en **{st.session_state.donde}** "
        f"mediante **{st.session_state.como}**, "
        f"apalancado en **{st.session_state.que}**."
    )
    st.success(f"**Estrategia Integrada:** {frase_integrada}")
    
    final_rows = []
    for p, kpis in st.session_state.kpis.items():
        for k, d in kpis.items():
            final_rows.append({"Perspectiva": p, "KPI": k, "Resultado": d['actual'], "Meta": d['ideal']})
    st.table(pd.DataFrame(final_rows))
    
    st.subheader("IV. Historial de Decisiones")
    if st.session_state.historial: st.table(pd.DataFrame(st.session_state.historial))
    
    st.markdown("---")
    st.subheader("V. Análisis de Aprendizaje y Reflexión Estratégica")
    st.write("Reflexiona sobre la coherencia entre tu autoevaluación inicial (Canvas) y las decisiones tomadas:")
    analisis_aprendizaje = st.text_area(
        "¿Cómo influyeron tus debilidades identificadas en tu plan de inversión? ¿Los resultados finales validan tu estrategia?",
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
