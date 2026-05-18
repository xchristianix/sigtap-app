import streamlit as st
import pandas as pd
import unicodedata

# ─── Configuração da página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Pesquisa SIGTAP / SUS Paulista",
    page_icon="🏥",
    layout="wide",
)

# ─── CSS personalizado ────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stTextInput > div > div > input {
        font-size: 16px;
        border-radius: 8px;
        border: 1.5px solid #dee2e6;
        padding: 10px 14px;
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 16px 20px;
        border: 1px solid #e9ecef;
        text-align: center;
    }
    .proc-code {
        font-family: monospace;
        background: #f1f3f5;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 13px;
    }
    .tag-amb  { background:#e1f5ee; color:#0f6e56; padding:2px 10px; border-radius:99px; font-size:12px; font-weight:600; }
    .tag-int  { background:#e6f1fb; color:#185fa5; padding:2px 10px; border-radius:99px; font-size:12px; font-weight:600; }
    .tag-cir  { background:#faeeda; color:#854f0b; padding:2px 10px; border-radius:99px; font-size:12px; font-weight:600; }
    div[data-testid="stExpander"] {
        border: 1px solid #e9ecef;
        border-radius: 10px;
        margin-bottom: 8px;
        background: white;
    }
</style>
""", unsafe_allow_html=True)


# ─── Base de dados de procedimentos ──────────────────────────────────────────
# ATENÇÃO: substitua pelos dados reais da tabela SIGTAP (arquivo .csv exportado
# do DATASUS ou tabela fornecida pela SES-SP).
PROCEDIMENTOS = [
    # Consultas
    {"codigo": "0301010072", "nome": "Consulta médica em atenção básica",             "grupo": "Ambulatorial", "especialidade": "Clínica Médica",                "sigtap": 10.00, "sus_sp": 11.00, "cid_ref": "Z00"},
    {"codigo": "0301010145", "nome": "Consulta médica em atenção especializada",       "grupo": "Ambulatorial", "especialidade": "Clínica Médica",                "sigtap": 10.00, "sus_sp": 14.00, "cid_ref": "Z01"},
    {"codigo": "0301060118", "nome": "Consulta em cardiologia",                        "grupo": "Ambulatorial", "especialidade": "Cardiologia",                   "sigtap": 10.00, "sus_sp": 14.00, "cid_ref": "I51"},
    {"codigo": "0301060053", "nome": "Consulta em dermatologia",                       "grupo": "Ambulatorial", "especialidade": "Dermatologia",                  "sigtap": 10.00, "sus_sp": 14.00, "cid_ref": "L98"},
    {"codigo": "0301060088", "nome": "Consulta em ortopedia",                          "grupo": "Ambulatorial", "especialidade": "Ortopedia e Traumatologia",     "sigtap": 10.00, "sus_sp": 14.00, "cid_ref": "M79"},
    {"codigo": "0303010010", "nome": "Consulta de nutrição",                           "grupo": "Ambulatorial", "especialidade": "Nutrição",                      "sigtap": 10.00, "sus_sp": 10.00, "cid_ref": "Z71.3"},
    # Exames laboratoriais
    {"codigo": "0205020097", "nome": "Hemograma completo",                             "grupo": "Ambulatorial", "especialidade": "Patologia Clínica",             "sigtap": 4.26,  "sus_sp": 5.00,  "cid_ref": "Z01.7"},
    {"codigo": "0205010059", "nome": "Glicemia de jejum",                              "grupo": "Ambulatorial", "especialidade": "Patologia Clínica",             "sigtap": 1.63,  "sus_sp": 2.00,  "cid_ref": "R73"},
    {"codigo": "0205020054", "nome": "Dosagem de creatinina",                          "grupo": "Ambulatorial", "especialidade": "Patologia Clínica",             "sigtap": 1.63,  "sus_sp": 2.00,  "cid_ref": "R94.4"},
    # Imagem
    {"codigo": "0402050027", "nome": "Ressonância magnética de crânio",                "grupo": "Ambulatorial", "especialidade": "Neurorradiologia",              "sigtap": 199.20,"sus_sp": 250.00,"cid_ref": "G93"},
    {"codigo": "0402040169", "nome": "Tomografia computadorizada de abdome",           "grupo": "Ambulatorial", "especialidade": "Radiologia",                   "sigtap": 88.75, "sus_sp": 115.00,"cid_ref": "R19"},
    {"codigo": "0402010034", "nome": "Radiografia de tórax",                           "grupo": "Ambulatorial", "especialidade": "Radiologia",                   "sigtap": 5.48,  "sus_sp": 7.00,  "cid_ref": "R91"},
    {"codigo": "0213010011", "nome": "Eletrocardiograma",                              "grupo": "Ambulatorial", "especialidade": "Cardiologia",                   "sigtap": 5.58,  "sus_sp": 7.50,  "cid_ref": "Z03.5"},
    # Endoscopia
    {"codigo": "0411020036", "nome": "Colonoscopia",                                   "grupo": "Ambulatorial", "especialidade": "Gastroenterologia",             "sigtap": 66.99, "sus_sp": 89.50, "cid_ref": "Z12.1"},
    {"codigo": "0407010064", "nome": "Colonoscopia com polipectomia",                  "grupo": "Cirúrgico",    "especialidade": "Gastroenterologia",             "sigtap": 95.50, "sus_sp": 130.00,"cid_ref": "K63.5"},
    {"codigo": "0411010043", "nome": "Endoscopia digestiva alta",                      "grupo": "Ambulatorial", "especialidade": "Gastroenterologia",             "sigtap": 30.50, "sus_sp": 42.00, "cid_ref": "Z13.8"},
    {"codigo": "0411010051", "nome": "Endoscopia digestiva alta com biópsia",          "grupo": "Cirúrgico",    "especialidade": "Gastroenterologia",             "sigtap": 38.00, "sus_sp": 55.00, "cid_ref": "K29"},
    # Obstetrícia / Ginecologia
    {"codigo": "0301070059", "nome": "Parto normal",                                   "grupo": "Internação",   "especialidade": "Ginecologia e Obstetrícia",     "sigtap": 248.50,"sus_sp": 350.00,"cid_ref": "Z37"},
    {"codigo": "0301070067", "nome": "Parto cesáreo",                                  "grupo": "Internação",   "especialidade": "Ginecologia e Obstetrícia",     "sigtap": 412.00,"sus_sp": 520.00,"cid_ref": "Z38"},
    {"codigo": "0301070105", "nome": "Curetagem uterina",                              "grupo": "Cirúrgico",    "especialidade": "Ginecologia e Obstetrícia",     "sigtap": 77.85, "sus_sp": 105.00,"cid_ref": "N85"},
    # Cirurgia
    {"codigo": "0409060020", "nome": "Apendicectomia",                                 "grupo": "Cirúrgico",    "especialidade": "Cirurgia Geral",                "sigtap": 428.00,"sus_sp": 580.00,"cid_ref": "K37"},
    {"codigo": "0409030036", "nome": "Herniorrafia inguinal",                          "grupo": "Cirúrgico",    "especialidade": "Cirurgia Geral",                "sigtap": 380.00,"sus_sp": 480.00,"cid_ref": "K40"},
    # Reabilitação
    {"codigo": "0303100039", "nome": "Fisioterapia respiratória",                      "grupo": "Ambulatorial", "especialidade": "Fisioterapia",                  "sigtap": 8.93,  "sus_sp": 12.00, "cid_ref": "J98"},
    {"codigo": "0303100012", "nome": "Fisioterapia motora",                            "grupo": "Ambulatorial", "especialidade": "Fisioterapia",                  "sigtap": 8.93,  "sus_sp": 12.00, "cid_ref": "M62"},
    {"codigo": "0303010029", "nome": "Avaliação nutricional",                          "grupo": "Ambulatorial", "especialidade": "Nutrição",                      "sigtap": 10.00, "sus_sp": 10.00, "cid_ref": "Z13.2"},
]

df = pd.DataFrame(PROCEDIMENTOS)


# ─── Funções auxiliares ───────────────────────────────────────────────────────
def badge_grupo(grupo: str) -> str:
    classes = {
        "Ambulatorial": "tag-amb",
        "Internação":   "tag-int",
        "Cirúrgico":    "tag-cir",
    }
    css = classes.get(grupo, "tag-amb")
    return f'<span class="{css}">{grupo}</span>'


def fmt_brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def variacao(sigtap: float, sp: float) -> str:
    if sigtap == 0:
        return "—"
    pct = (sp - sigtap) / sigtap * 100
    sinal = "+" if pct >= 0 else ""
    cor = "green" if pct > 0 else ("red" if pct < 0 else "gray")
    return f"<span style='color:{cor};font-weight:600'>{sinal}{pct:.1f}%</span>"


def normalizar(texto: str) -> str:
    """Remove acentos e converte para minúsculas."""
    return unicodedata.normalize("NFD", texto).encode("ascii", "ignore").decode("ascii").lower()


def pesquisar(query: str, grupo_filtro: str) -> pd.DataFrame:
    resultado = df.copy()
    if grupo_filtro != "Todos":
        resultado = resultado[resultado["grupo"] == grupo_filtro]
    if query.strip():
        # Normaliza cada coluna para busca sem acento
        nome_norm       = resultado["nome"].apply(normalizar)
        espec_norm      = resultado["especialidade"].apply(normalizar)
        cid_norm        = resultado["cid_ref"].apply(normalizar)

        # Divide a query em palavras — todas devem aparecer no resultado
        palavras = [normalizar(p) for p in query.strip().split()]

        mask = pd.Series([True] * len(resultado), index=resultado.index)
        for palavra in palavras:
            mask &= (
                nome_norm.str.contains(palavra, na=False) |
                resultado["codigo"].str.contains(palavra, na=False) |
                espec_norm.str.contains(palavra, na=False) |
                cid_norm.str.contains(palavra, na=False)
            )
        resultado = resultado[mask]
    return resultado


# ─── Interface ────────────────────────────────────────────────────────────────
st.title("🏥 Pesquisa de Procedimentos SUS")
st.caption("Tabela SIGTAP · Tabela SUS Paulista (SES-SP)  |  Dados de referência — atualize com a tabela vigente")

st.divider()

col_busca, col_filtro = st.columns([3, 1])
with col_busca:
    query = st.text_input(
        "Pesquisar procedimento",
        placeholder="Ex: colonoscopia, hemograma, parto...",
        label_visibility="collapsed",
    )
with col_filtro:
    grupo_filtro = st.selectbox(
        "Grupo",
        ["Todos", "Ambulatorial", "Internação", "Cirúrgico"],
        label_visibility="collapsed",
    )

resultados = pesquisar(query, grupo_filtro)

# Métricas rápidas
if not resultados.empty:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Procedimentos encontrados", len(resultados))
    c2.metric("Menor valor SIGTAP",  fmt_brl(resultados["sigtap"].min()))
    c3.metric("Maior valor SIGTAP",  fmt_brl(resultados["sigtap"].max()))
    c4.metric("Média SUS Paulista",  fmt_brl(resultados["sus_sp"].mean()))

st.divider()

# Lista de resultados
if not query and grupo_filtro == "Todos":
    st.info("👆 Digite o nome ou código do procedimento para iniciar a pesquisa.")

elif resultados.empty:
    st.warning("Nenhum procedimento encontrado. Tente outros termos.")

else:
    st.caption(f"{len(resultados)} resultado(s)")

    for _, row in resultados.iterrows():
        label = f"**{row['nome']}** — `{row['codigo']}`"
        with st.expander(label, expanded=False):
            col_info, col_vals = st.columns([1.2, 1])

            with col_info:
                st.markdown(badge_grupo(row["grupo"]), unsafe_allow_html=True)
                st.markdown(f"**Especialidade:** {row['especialidade']}")
                st.markdown(f"**CID de referência:** `{row['cid_ref']}`")
                st.markdown(f"**Código SIGTAP:** `{row['codigo']}`")

            with col_vals:
                v1, v2 = st.columns(2)
                v1.metric("SIGTAP",        fmt_brl(row["sigtap"]))
                v2.metric(
                    "SUS Paulista",
                    fmt_brl(row["sus_sp"]),
                    delta=f"{((row['sus_sp']-row['sigtap'])/row['sigtap']*100):+.1f}% vs SIGTAP"
                    if row["sigtap"] > 0 else None,
                )

st.divider()

# Exportar tabela
if not resultados.empty and (query or grupo_filtro != "Todos"):
    export_df = resultados.rename(columns={
        "codigo": "Código SIGTAP",
        "nome": "Procedimento",
        "grupo": "Grupo",
        "especialidade": "Especialidade",
        "sigtap": "Valor SIGTAP (R$)",
        "sus_sp": "Valor SUS-SP (R$)",
        "cid_ref": "CID Referência",
    })
    csv = export_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇ Exportar resultados (.csv)",
        data=csv,
        file_name="procedimentos_sus.csv",
        mime="text/csv",
    )

st.markdown(
    "<p style='text-align:center;color:#adb5bd;font-size:12px;margin-top:2rem'>"
    "Fonte: DATASUS / SIGTAP · SES-SP — Atualizar conforme competência vigente</p>",
    unsafe_allow_html=True,
)
