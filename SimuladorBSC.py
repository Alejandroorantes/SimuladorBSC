import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Configuración inicial
st.set_page_config(page_title="Simulador de Estrategia Alex", layout="wide")

# --- ESTILOS PERSONALIZADOS (CSS) ---
st.markdown("""
    <style>
    .main h1 {
        text-align: center;
        color: #1E3A8A;
        font-size: 50px !important;
        font-weight: bold;
    }
    .main h3 {
        color: #1E3A8A;
    }
    .main h2 {
        color: #1E3A8A;
        text-align: center;
    }
    /* Estilo para las tarjetas de diagnóstico */
    .stInfo { background-color: #f0f2f6; border-left: 5px solid #1E3A8A; }
    </style>
    """, unsafe_allow_html=True)

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

# --- NAVEGACIÓN ---

# FASE 1: DIAGNÓSTICO
if st.session_state.paso == 1:
    st.markdown("<h1>Simulador de Estrategia de negocios</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; font-size: 30px;'>Creado por: Dr. Alejandro Orantes Kestler</h3>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: left; color: #1E3A8A; font-size: 20px;'>Objetivo: este simulador fue elaborado para que los estudiantes diseñen una estrategia y luego simular la toma de decisiones y que se comprenda el impacto que tiene cada decisión.</h3>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: left; color: #1E3A8A; font-size: 20px;'>Instrucciones: seleccione una empresa que conozca e intente llenar la mayor cantidad de informacion que conozca sobre la empresa y esto permitirá que el programa le recomiende una estrategia y luego tendrá un presupuesto de 20 millones de los que podrá tomar decisiones y podrá evaluar sus efectos.</h3>", unsafe_allow_html=True)
    
    st.header("Fase 1: Diagnóstico Integral de Negocio")
    with st.form("diagnostico_form"):
        col_id1, col_id2 = st.columns(2)
        with col_id1:
            empresa_input = st.text_input("Nombre de la Organización:")
        with col_id2:
            industria_input = st.selectbox("Industria:", ["Agricultura","Agroindustria","Construcción","Quimicos","Manufactura", "Servicios", "Bancario y serficios financieros","Alimentos y Bebidas","Tecnología", "Retail","Textiles y Vestuario"])
        
        st.subheader("I. Arquitectura de Negocio (Canvas) y Autoevaluación")
        st.caption("Define cada elemento y selecciona si representa actualmente una Fortaleza o una Debilidad.")

        # --- ESQUEMA DETALLADO RESTAURADO ---
        campos_canvas = [
            "Propuesta de Valor", 
            "Procesos/actividades Clave1",
            "Procesos/Actividades Clave2",
            "Procesos/Actividades Clave3", 
            "Procesos/Actividades Clave4", 
            "Recursos Tecnologico Clave",
            "Recursos Humano Clave", 
            "Recursos Informatico clave", 
            "Infraestructura clave", 
            "Socios Clave"
        ]
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
        with f1: opp = st.text_area("Oportunidades (Factores Externos Positivos):")
        with f2: ame = st.text_area("Amenazas (Factores Externos Negativos):")
        
        if st.form_submit_button("Siguiente"):
            if empresa_input:
                st.session_state.empresa = empresa_input
                st.session_state.industria = industria_input
                st.session_state.datos_f1 = {"Canvas": respuestas_canvas, "Oportunidades": opp, "Amenazas": ame}
                st.session_state.diagnostico_texto = " ".join([v["texto"] for v in respuestas_canvas.values()]) + f" {opp} {ame}"
                st.session_state.paso = 2
                st.rerun()
            else: st.error("Por favor ingresa el nombre de la empresa.")

# FASE 2: ESTRATEGIA
elif st.session_state.paso == 2:
    st.markdown("<h1>Fase 2: Estrategia Play to Win</h1>", unsafe_allow_html=True)
    with st.form("estrategia_form"):
        asp = st.text_input("¿Cuál es nuestra aspiración ganadora?")
        don = st.text_input("¿Dónde jugaremos?")
        com = st.text_input("¿Cómo ganaremos?")
        cap = st.text_input("¿Qué capacidades deben estar presentes?")
        if st.form_submit_button("Iniciar Simulador"):
            st.session_state.aspiracion, st.session_state.donde, st.session_state.como, st.session_state.que = asp, don, com, cap
            st.session_state.paso = 3
            st.rerun()

# FASE 3: SIMULADOR
elif st.session_state.paso == 3:
    st.markdown(f"<h1>Tablero de Control: {st.session_state.empresa}</h1>", unsafe_allow_html=True)
    col_vis, col_ctrl = st.columns([2, 1])

    with col_vis:
        t_matriz, t_gap, t_hist = st.tabs(["📋 Matriz BSC", "📊 Análisis Gaps", "📜 Historial"])
        rows = []
        labels, vals, targets = [], [], []
        for p, kpis in st.session_state.kpis.items():
            for k, d in kpis.items():
                labels.append(k); vals.append(d['actual']); targets.append(d['ideal'])
                status = "🟢" if d['actual'] >= d['ideal'] else "🟡" if d['actual'] >= (d['ideal']*0.8) else "🔴"
                rows.append({"Estado": status, "Perspectiva": p, "KPI": k, "Actual": d['actual'], "Meta": d['ideal']})
        
        with t_matriz: st.table(pd.DataFrame(rows))
        with t_gap:
            fig, ax = plt.subplots(figsize=(10, 4))
            x = np.arange(len(labels))
            ax.bar(x - 0.2, vals, 0.4, label='Actual', color='#007bff')
            ax.bar(x + 0.2, targets, 0.4, label='Meta', color='#e9ecef', alpha=0.5)
            ax.set_xticks(x); ax.set_xticklabels(labels, rotation=45); ax.legend(); st.pyplot(fig)
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
                for p, k_imp in info['impacto'].items():
                    for kn, val in k_imp.items():
                        vf = round(val * mod, 2)
                        st.session_state.kpis[p][kn]['actual'] = round(st.session_state.kpis[p][kn]['actual'] + vf, 2)
                        detalles.append({"KPI": kn, "Impacto": f"+{vf}" if vf > 0 else f"{vf}"})
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

# FASE 4: REPORTE FINAL INTEGRADO
elif st.session_state.paso == 4:
    st.markdown("<h1>Reporte Estratégico Final</h1>", unsafe_allow_html=True)
    
    st.subheader("I. Información General")
    st.write(f"**Empresa:** {st.session_state.empresa} | **Industria:** {st.session_state.industria}")
    st.text_input("Nombre del Participante:")
    
    st.markdown("---")
    # INTEGRACIÓN DE MATRIZ DE FORTALEZAS Y DEBILIDADES RESUMIDA
    st.subheader("II. Interpretación del Diagnóstico Interno (Canvas)")
    st.write("A continuación se presentan los elementos clave de la arquitectura de negocio clasificados por su impacto estratégico:")
    
    col_fort, col_deb = st.columns(2)
    with col_fort:
        st.markdown("<h4 style='color: #10B981;'>💪 Capacidades Críticas (Fortalezas)</h4>", unsafe_allow_html=True)
        forts = {k: v for k, v in st.session_state.datos_f1["Canvas"].items() if v['tipo'] == "Fortaleza"}
        for k, v in forts.items(): 
            if v['texto']: st.success(f"**{k}:** {v['texto']}")
            
    with col_deb:
        st.markdown("<h4 style='color: #EF4444;'>⚠️ Brechas Estratégicas (Debilidades)</h4>", unsafe_allow_html=True)
        debs = {k: v for k, v in st.session_state.datos_f1["Canvas"].items() if v['tipo'] == "Debilidad"}
        for k, v in debs.items(): 
            if v['texto']: st.error(f"**{k}:** {v['texto']}")

    st.markdown("---")
    st.subheader("III. Análisis Externo y Estrategia Play to Win")
    c1, c2 = st.columns(2)
    c1.warning(f"**Oportunidades:** {st.session_state.datos_f1['Oportunidades']}")
    c2.error(f"**Amenazas:** {st.session_state.datos_f1['Amenazas']}")
    
    frase_integrada = f"Aspiramos a **{st.session_state.aspiracion}** en **{st.session_state.donde}** mediante **{st.session_state.como}**, apalancado en capacidades de **{st.session_state.que}**."
    st.info(f"**Estrategia Integrada:** {frase_integrada}")

    st.subheader("IV. Resultados de los KPIs")
    res_rows = []
    for p, kpis in st.session_state.kpis.items():
        for k, d in kpis.items():
            res_rows.append({"Perspectiva": p, "KPI": k, "Resultado": d['actual'], "Meta": d['ideal']})
    st.table(pd.DataFrame(res_rows))

    st.subheader("V. Historial de Decisiones")
    if st.session_state.historial: st.table(pd.DataFrame(st.session_state.historial))

    st.subheader("VI. Reflexión de Aprendizaje")
    st.write("Analiza la coherencia de tus decisiones:")
    st.text_area("¿Cómo ayudaron tus inversiones a cerrar las 'Brechas Estratégicas' detectadas arriba?", height=150)
    
    if st.button("Finalizar Actividad"):
        st.balloons()
        st.success("¡Simulación completada con éxito!")
