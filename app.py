import streamlit as st
import pandas as pd
import logging
st.set_page_config( layout="wide")

# Configuração inicial do log
logging.basicConfig(
    filename='app_log.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S'
)

def log_message(message, level="info"):
    if level == "info":
        logging.info(message)
    elif level == "warning":
        logging.warning(message)
    elif level == "error":
        logging.error(message)
    elif level == "debug":
        logging.debug(message)

log_message("Iniciando a aplicação.", "info")
# Configuração inicial


def Qnt_convidados():
    try:
        log_message("Carregando arquivo 'qnt.xlsx'.", "info")
        return pd.read_excel("qnt.xlsx")
    except FileNotFoundError:
        log_message("Arquivo 'qnt.xlsx' não encontrado. Criando DataFrame vazio.", "warning")
        return pd.DataFrame({"Produtor Associado": [], "E-mail": [], "Confirmação": []})

# Função para carregar os dados dos convidados
@st.cache_data
def load_convidados():
    try:
        log_message("Carregando arquivo 'lista.xlsx'.", "info")
        return pd.read_excel("lista.xlsx")
    except FileNotFoundError:
        log_message("Arquivo 'lista.xlsx' não encontrado. Criando DataFrame vazio.", "warning")
        return pd.DataFrame({"Produtor Associado": [], "E-mail": [], "Confirmação": []})

def Confimacao():
    try:
        log_message("Carregando arquivo 'convidados.csv'.", "info")
        return pd.read_csv("convidados.csv")
    except FileNotFoundError:
        log_message("Arquivo 'convidados.csv' não encontrado. Criando DataFrame vazio.", "warning")
        return pd.DataFrame({"Produtor Associado": [], "E-mail": [], "Confirmação": []})

# Função para salvar os dados
def save_convidados(df):
    try:
        log_message("Salvando arquivo 'convidados.csv'.", "info")
        df.to_csv("convidados.csv", index=False)
    except Exception as e:
        log_message(f"Erro ao salvar 'convidados.csv': {e}", "error")


# Carregando os dados
convidados = load_convidados()

# Garantir que a coluna "Confirmação" seja booleana
if not convidados.empty:
    if convidados["conf"].dtype != bool:
        # Converte valores para booleanos, caso estejam como string ou outro formato
        convidados["conf"] = convidados["conf"].map(lambda x: str(x).lower() == "true")



# Página inicial
st.title("Controle de lista de Convidados")

quant= Qnt_convidados()
soma_quantidade = quant['CONVIDADOS '].sum()
soma_quantidade1 = quant['CONFIRMADOS '].sum()
soma_quantidade2 = quant['NÃO '].sum()
soma_quantidade3 = quant['PENDENTES '].sum()

col1,col2,col3,col4 = st.columns(4)
with col1:
    st.metric(label="Convidados", value=f"{soma_quantidade}")
with col2:
    st.metric(label="Confirmados", value=f"{soma_quantidade1}")
with col3:
    st.metric(label="Não Confirmados", value=f"{soma_quantidade2}")
with col4:
    st.metric(label="Pendentes", value=f"{soma_quantidade3}")

st.write("Por favor, selecione seu nome para confirmar sua presença.")
# Lista de nomes disponíveis
nomes_disponiveis = convidados.loc[~convidados["conf"], "Produtor Associado"].tolist()

# Exibir mensagem caso todos os convidados já tenham confirmado
if not nomes_disponiveis:
    st.success("Todos os convidados já confirmaram presença!")
else:
    # Selectbox para escolher o nome
        nome_selecionado = st.selectbox("Selecione seu nome:", [""] + nomes_disponiveis)

        if nome_selecionado:
            # Encontrar o convidado selecionado
            convidado_1 = convidados[convidados["Produtor Associado"] == nome_selecionado].iloc[0]

            st.write(f"**Nome:** {convidado_1['Produtor Associado']}")
            st.write(f"**Email:** {convidado_1['E-mail']}")
            st.write(f"**Quantidade de Convidados:** {convidado_1['Convite']}")
            convidados["Confirmação"] = convidados["Confirmação"].astype(str)
            st.write(f"**Confirmação de presença:** {convidado_1['Confirmação']}")
            st.write(f"**Grupo:** {convidado_1['local_id']}")

            st.write(f"**Confirme a quantidade de Convidados**")
            Qnt = pd.read_csv("cv.csv")
            qnt_sel = st.selectbox("Quantidade de Convidados", Qnt)

            confimacao_conv = Confimacao()

            if not confimacao_conv.empty:
                conf = confimacao_conv[confimacao_conv["Produtor Associado"] == nome_selecionado]
                conf_1 = conf.iloc[0]["Confirmação"] if not conf.empty else "não"
                st.write(f"**Confirmação:** {conf_1}")
            else:
                conf_1 = "não"

            if st.button("Confirmar Presença"):
                # Verificar se o convidado já está salvo no arquivo
                try:
                    convidados_existentes = pd.read_csv("convidados.csv")
                except FileNotFoundError:
                    convidados_existentes = pd.DataFrame(columns=convidados.columns)

                # Checar se o "Produtor Associado" já está na lista
                if nome_selecionado in convidados_existentes["Produtor Associado"].values:
                    st.warning(f"{nome_selecionado} já está registrado como confirmado!")
                else:
                    # Atualizar a confirmação de convidado_1
                    convidado_1["Confirmação"] = "confirmado"

                    # Adicionar a quantidade selecionada ao convidado
                    convidado_1["Quantidade Selecionada"] = qnt_sel

                    # Converter para DataFrame antes de salvar
                    convidado_df = convidado_1.to_frame().T  # Transforma em DataFrame com uma linha

                    # Salvar no arquivo CSV (modo append para não sobrescrever tudo)
                    convidado_df.to_csv("convidados.csv", mode='a', index=False, header=False)

                    st.success(f"Presença de {nome_selecionado} confirmada com sucesso!")

st.divider()  # Insere o separador

# Suponha que 'convidados.csv' seja o arquivo com as informações dos convidados
convidados = pd.read_csv("convidados.csv")

# Agrupar por 'Grupo' e 'Confirmação', somando a quantidade de convidados
tabela_quantificada = convidados.groupby(['local_id', 'Confirmação']).agg(
    qnt_convidados=('Convite', 'sum'),
    qnt_Confirmação=('qnt_confer', 'sum'),
).reset_index()

# Exibir a tabela quantificada no Streamlit
st.write("Tabela Quantificada de Convidados:")
st.dataframe(tabela_quantificada)

# Somar a quantidade de convidados
soma_quantidade5 = tabela_quantificada['qnt_convidados'].sum()+54

# Exibir o valor da soma em uma coluna
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Convidados Presentes", value=f"{soma_quantidade5}")

with col2:
    st.metric(label="Convidados Ausente", value=f"{soma_quantidade - soma_quantidade5}")


st.write("-----------------------------------")
st.write("Confirmados")

colunas_selecionadas = convidados[["Produtor Associado", "Confirmação", "qnt_confer"]]
st.dataframe(colunas_selecionadas)
