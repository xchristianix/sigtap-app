# 🏥 Pesquisa SIGTAP / SUS Paulista

App em Python (Streamlit) para pesquisa de procedimentos médicos do SUS,
com valores da tabela SIGTAP e da tabela SUS Paulista (SES-SP).

---

## Como instalar e rodar

### 1. Pré-requisitos
- Python 3.9 ou superior instalado
- Acesso ao terminal (Windows: Prompt de Comando ou PowerShell)

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Rodar o app

```bash
streamlit run app.py
```

O navegador abrirá automaticamente em `http://localhost:8501`.

---

## Como atualizar a base de dados

O app usa dados de exemplo. Para usar os dados reais:

### Opção A — Importar CSV do SIGTAP

1. Acesse: http://sigtap.datasus.gov.br/tabela-unificada/app/sec/inicio.jsp
2. Faça download da tabela na competência desejada (arquivo `.zip`)
3. Extraia o arquivo `tb_procedimento.txt`
4. Substitua o dicionário `PROCEDIMENTOS` em `app.py` pelo código abaixo:

```python
import pandas as pd

# Ajuste os nomes das colunas conforme o layout do SIGTAP
df = pd.read_csv(
    "tb_procedimento.txt",
    sep=";",
    encoding="latin-1",
    dtype=str,
)
# Renomear conforme necessidade:
# df.rename(columns={"CO_PROCEDIMENTO": "codigo", "NO_PROCEDIMENTO": "nome", ...})
```

### Opção B — Manter planilha própria

Crie um arquivo `procedimentos.csv` com as colunas:

```
codigo,nome,grupo,especialidade,sigtap,sus_sp,cid_ref
```

E carregue no `app.py`:

```python
df = pd.read_csv("procedimentos.csv")
```

---

## Estrutura do projeto

```
sigtap_app/
├── app.py              ← código principal do app
├── requirements.txt    ← dependências Python
├── README.md           ← este arquivo
└── procedimentos.csv   ← (opcional) base de dados própria
```

---

## Funcionalidades

- Pesquisa por nome do procedimento, código SIGTAP, especialidade ou CID
- Filtro por grupo (Ambulatorial / Internação / Cirúrgico)
- Comparação dos valores SIGTAP vs SUS Paulista com variação percentual
- Métricas resumidas (quantidade, menor/maior valor, média)
- Exportação dos resultados em `.csv`

---

*Atualizar os valores conforme a competência vigente da tabela SIGTAP.*
