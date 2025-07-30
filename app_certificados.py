import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
import zipfile
from datetime import datetime
import tempfile

# =============================
# CONFIGURAÇÃO DE SENHA (usando secrets)
# =============================
SENHA_CORRETA = st.secrets["senha_admin"]

st.set_page_config(page_title="Certificados Trilhas", page_icon="📜")

st.title("🔐 Acesso Restrito - Gerador de Certificados")

# Campo de senha
senha = st.text_input("Digite a senha para acessar:", type="password")

if senha != SENHA_CORRETA:
    st.warning("Acesso protegido. Digite a senha correta para continuar.")
    st.stop()

# =============================
# FUNÇÕES AUXILIARES
# =============================

def gerar_certificado(nome, rg, atividade, caminho_saida):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)

    pdf.set_xy(10, 20)
    pdf.multi_cell(0, 10, "CERTIFICADO DE PARTICIPAÇÃO", align='C')

    texto = (
        f"Certificamos que {nome}, portador do RG nº {rg}, participou da atividade "
        f"\"{atividade}\", realizada no âmbito do projeto Trilhas Potiguares."
    )
    pdf.set_xy(20, 50)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, texto, align='J')

    pdf.set_xy(10, 250)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, f"Emitido em {datetime.today().strftime('%d/%m/%Y')}", 0, 1, 'C')

    nome_arquivo = f"{nome.replace(' ', '_')}_{rg}.pdf"
    caminho_completo = os.path.join(caminho_saida, nome_arquivo)
    pdf.output(caminho_completo)

def zipar_pasta(pasta_origem, zip_destino):
    with zipfile.ZipFile(zip_destino, 'w') as zipf:
        for root, _, files in os.walk(pasta_origem):
            for file in files:
                zipf.write(os.path.join(root, file), arcname=file)

# =============================
# INTERFACE APÓS AUTENTICAÇÃO
# =============================

st.success("Acesso autorizado!")

atividade = st.text_input("Digite o nome da Oficina ou Minicurso")

arquivo_excel = st.file_uploader("Anexe a planilha Excel com os nomes e RGs", type=["xlsx"])

if atividade and arquivo_excel:
    df = pd.read_excel(arquivo_excel)

    if "Nome completo" not in df.columns or "RG" not in df.columns:
        st.error("A planilha deve conter as colunas: 'Nome completo' e 'RG'.")
    else:
        if st.button("Gerar Certificados"):
            with st.spinner("Gerando certificados..."):
                with tempfile.TemporaryDirectory() as tmpdir:
                    for _, linha in df.iterrows():
                        nome = linha["Nome completo"]
                        rg = str(linha["RG"])
                        gerar_certificado(nome, rg, atividade, tmpdir)

                    zip_path = os.path.join(tmpdir, "certificados.zip")
                    zipar_pasta(tmpdir, zip_path)

                    with open(zip_path, "rb") as f:
                        st.success("Certificados gerados com sucesso!")
                        st.download_button("📥 Baixar certificados (.zip)", f, file_name="certificados.zip")

else:
    st.info("Preencha o nome da atividade e envie a planilha para continuar.")
