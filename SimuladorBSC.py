import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF # Nueva librería para el PDF

# --- FUNCIÓN PARA GENERAR EL PDF ---
def generar_pdf(nombre, empresa, industria, estrategia, kpis, historial, reflexion):
    pdf = FPDF()
    pdf.add_page()
    
    # Título
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Reporte Estratégico Final - Simulador Alex", ln=True, align='C')
    
    # Datos Generales
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Participante: {nombre}", ln=True)
    pdf.cell(200, 10, txt=f"Organización: {empresa} ({industria})", ln=True)
    pdf.cell(200, 10, txt=f"Estrategia: {estrategia}", ln=True)
    
    # Tabla de KPIs
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Resultados de KPIs:", ln=True)
    pdf.set_font("Arial", size=10)
    for p, ks in kpis.items():
        for k, d in ks.items():
            pdf.cell(200, 8, txt=f"- {k}: {d['actual']} (Meta: {d['ideal']})", ln=True)
    
    # Reflexión
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Reflexión de Aprendizaje:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, txt=reflexion)
    
    return pdf.output(dest='S').encode('latin-1')

# ... (Todo tu código anterior de inicialización y fases 1, 2 y 3 se mantiene igual) ...

# FASE 4: REPORTE FINAL CON PDF
elif st.session_state.paso == 4:
    st.title("Reporte Estratégico Final")
    
    st.subheader("I. Información del Participante")
    nombre_p = st.text_input("Nombre completo:")
    
    # ... (Sección de Resumen, Estrategia e Historial que ya tienes) ...
    
    st.markdown("---")
    st.subheader("V. Análisis de Aprendizaje")
    analisis_aprendizaje = st.text_area("Análisis y Reflexión Estratégica:", height=200)
    
    col_fin1, col_fin2 = st.columns(2)
    with col_fin1:
        if st.button("Volver al Simulador"):
            st.session_state.paso = 3
            st.rerun()
            
    with col_fin2:
        # Validamos que el nombre y el análisis no estén vacíos antes de permitir el PDF
        if nombre_p and analisis_aprendizaje:
            # Preparamos el PDF
            estr_txt = f"{st.session_state.como} en {st.session_state.donde}"
            pdf_bytes = generar_pdf(
                nombre_p, 
                st.session_state.empresa, 
                st.session_state.industria,
                estr_txt,
                st.session_state.kpis,
                st.session_state.historial,
                analisis_aprendizaje
            )
            
            # Botón de descarga
            st.download_button(
                label="📥 DESCARGAR INFORME EN PDF",
                data=pdf_bytes,
                file_name=f"Reporte_Estrategia_{st.session_state.empresa}.pdf",
                mime="application/pdf",
                type="primary"
            )
        else:
            st.warning("Escribe tu nombre y reflexión para habilitar la descarga del PDF.")
