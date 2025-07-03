import streamlit as st
from streamlit_calendar import calendar
import json
import datetime
import yagmail  # ou use smtplib se preferir

# -------------- CONFIGURAÇÕES INICIAIS ----------------
st.set_page_config(page_title="📆 Agenda & Tarefas", layout="wide")
st.title("📆 Agenda & Tarefas do Advogado")

st.write("Visualize, adicione e gerencie seus compromissos. Configure alertas para receber notificações por e-mail!")

# ------------------------------------------
# LOCAL PARA GUARDAR EVENTOS (exemplo em memória)
# Em produção: salve em um banco de dados ou arquivo
# ------------------------------------------
if 'eventos' not in st.session_state:
    st.session_state['eventos'] = []

# ------------------------------------------
# CONFIGURAÇÃO DO E-MAIL (exemplo usando Gmail)
# ------------------------------------------
st.sidebar.header("⚙️ Configurações de E-mail")
user_email = st.sidebar.text_input("Seu E-mail de Remetente (Gmail)", value="exemplo@gmail.com")
user_password = st.sidebar.text_input("Senha do App Gmail", type="password")
alert_email = st.sidebar.text_input("E-mail para receber alertas", value="destinatario@gmail.com")

# ------------------------------------------
# CRIAÇÃO DE EVENTO
# ------------------------------------------
st.subheader("➕ Adicionar Nova Tarefa/Evento")
with st.form("form_evento"):
    titulo = st.text_input("Título do Evento")
    descricao = st.text_area("Descrição/Notas")
    data_inicio = st.date_input("Data de Início", value=datetime.date.today())
    hora_inicio = st.time_input("Hora de Início", value=datetime.datetime.now().time())
    duracao_horas = st.number_input("Duração (horas)", 1, 12, value=1)
    aviso_antecedencia = st.number_input("Avisar quantos minutos antes?", 5, 1440, 60)
    submit = st.form_submit_button("Adicionar Evento")

    if submit:
        dt_inicio = datetime.datetime.combine(data_inicio, hora_inicio)
        dt_fim = dt_inicio + datetime.timedelta(hours=duracao_horas)
        evento = {
            "title": titulo,
            "start": dt_inicio.isoformat(),
            "end": dt_fim.isoformat(),
            "description": descricao,
            "alert_minutes": aviso_antecedencia
        }
        st.session_state['eventos'].append(evento)
        st.success(f"Evento '{titulo}' adicionado!")

# ------------------------------------------
# CALENDÁRIO INTERATIVO
# ------------------------------------------
st.subheader("📅 Seu Calendário")
calendar_options = {
    "editable": True,
    "selectable": True,
    "initialView": "dayGridMonth",
    "locale": "pt-br"
}

events = st.session_state['eventos']
calendar_component = calendar(events=events, options=calendar_options, custom_css="""
    .fc-event-title {
        font-weight: bold;
    }
""")

# ------------------------------------------
# ENVIO DE ALERTAS POR E-MAIL
# ------------------------------------------
# AVISO: Este é um exemplo que roda só quando o usuário executa o app.
# Em produção: use um scheduler como Celery ou cronjob para rodar automaticamente em background.

now = datetime.datetime.now()
for evento in events:
    evento_time = datetime.datetime.fromisoformat(evento["start"])
    delta = (evento_time - now).total_seconds() / 60  # minutos até o evento
    if 0 < delta <= evento["alert_minutes"]:
        try:
            # Usando yagmail para simplificar
            yag = yagmail.SMTP(user=user_email, password=user_password)
            assunto = f"Lembrete: {evento['title']}"
            corpo = f"""
            Você tem um evento agendado: {evento['title']}
            📅 Início: {evento_time.strftime('%d/%m/%Y %H:%M')}
            📝 Descrição: {evento['description']}
            """
            yag.send(to=alert_email, subject=assunto, contents=corpo)
            st.success(f"Alerta enviado para {alert_email} para o evento '{evento['title']}'")
        except Exception as e:
            st.warning(f"Erro ao enviar e-mail: {e}")
