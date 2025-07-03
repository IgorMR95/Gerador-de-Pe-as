import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from streamlit_drawable_canvas import st_canvas
import graphviz

# Para usar o vis-timeline via Streamlit Components
import streamlit.components.v1 as components
import json

st.set_page_config(page_title="Design para Petições", layout="wide")
st.title("🎨 Gerador de Elementos Visuais para Petições")

st.write("Monte facilmente elementos visuais explicativos para incluir em suas peças jurídicas. Basta preencher os campos e baixar como imagem!")

# ------------------------------
# Escolha principal
# ------------------------------
opcao = st.selectbox(
    "Escolha o que deseja criar:",
    ["Selecione", "Linha do Tempo", "Gráfico", "Fluxograma", "Mapa Mental", "Desenho Livre"]
)

# ------------------------------
# Função auxiliar para exportar figuras matplotlib
# ------------------------------
def baixar_figura(fig, nome):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight')
    st.download_button(f"📥 Baixar como PNG", buf.getvalue(), f"{nome}.png", "image/png")

# ------------------------------
# LINHA DO TEMPO usando vis-timeline
# ------------------------------
if opcao == "Linha do Tempo":
    st.header("🕰️ Linha do Tempo (vis-timeline)")
    st.write("Adicione eventos com nome e descrição para gerar uma linha do tempo interativa.")

    eventos = []
    n_eventos = st.number_input("Número de Eventos", min_value=1, max_value=20, value=3)

    for i in range(int(n_eventos)):
        data = st.date_input(f"Data do Evento {i+1}", key=f"data_{i}")
        nome_evento = st.text_input(f"Nome do Evento {i+1}", key=f"nome_{i}")
        descricao_evento = st.text_area(f"Descrição do Evento {i+1}", key=f"desc_{i}")
        eventos.append({
            "start": str(data),
            "content": f"<b>{nome_evento}</b><br><small>{descricao_evento}</small>",
            "title": descricao_evento
        })

    # Opções de customização
    st.subheader("⚙️ Opções de Customização")
    height = st.slider("Altura da Timeline (px)", 200, 1000, 400)
    selectable = st.checkbox("Permitir Seleção", value=True)
    editable = st.checkbox("Permitir Arrastar Eventos", value=False)
    stack_events = st.checkbox("Empilhar Eventos Sobrepostos", value=True)

    if st.button("Gerar Linha do Tempo"):
        st.write("✅ **Linha do Tempo Interativa:**")

        # Criar container HTML + JS usando vis-timeline via CDN
        html_timeline = f"""
        <div id="visualization"></div>
        <script type="text/javascript" src="https://unpkg.com/vis-timeline@latest/standalone/umd/vis-timeline-graph2d.min.js"></script>
        <script type="text/javascript">
            var container = document.getElementById('visualization');
            var items = {json.dumps(eventos)};
            var options = {{
                height: '{height}px',
                selectable: {str(selectable).lower()},
                editable: {str(editable).lower()},
                stack: {str(stack_events).lower()}
            }};
            var timeline = new vis.Timeline(container, items, options);
        </script>
        """

        components.html(html_timeline, height=height + 50)

        st.info("Para salvar a timeline, clique com botão direito ou use uma captura de tela. (Atualmente o download direto via vis-timeline não é suportado nativamente pelo Streamlit).")

# ------------------------------
# GRÁFICOS usando Charts nativos
# ------------------------------
elif opcao == "Gráfico":
    st.header("📊 Gráfico")
    tipo = st.radio("Escolha o tipo de Gráfico", ["Barras", "Linha", "Área"])

    st.write("Adicione seus dados:")
    n_itens = st.number_input("Número de Itens", min_value=1, max_value=20, value=3)
    labels = []
    valores = []

    for i in range(int(n_itens)):
        labels.append(st.text_input(f"Rótulo {i+1}", key=f"label_{i}"))
        valores.append(st.number_input(f"Valor {i+1}", key=f"valor_{i}"))

    if st.button("Gerar Gráfico"):
        df = pd.DataFrame(valores, index=labels, columns=["Valor"])

        st.write("📈 **Visualização (Streamlit Nativo)**")
        if tipo == "Barras":
            st.bar_chart(df)
        elif tipo == "Linha":
            st.line_chart(df)
        elif tipo == "Área":
            st.area_chart(df)

        # Matplotlib para exportar
        fig, ax = plt.subplots()
        if tipo == "Barras":
            ax.bar(labels, valores)
        elif tipo == "Linha":
            ax.plot(labels, valores, marker="o")
        elif tipo == "Área":
            ax.fill_between(labels, valores, step="mid", alpha=0.4)
            ax.plot(labels, valores, marker="o")
        ax.set_title(f"Gráfico de {tipo}")
        st.pyplot(fig)
        baixar_figura(fig, f"grafico_{tipo.lower()}")

# ------------------------------
# FLUXOGRAMA usando Graphviz
# ------------------------------
elif opcao == "Fluxograma":
    st.header("📐 Fluxograma")
    st.write("Adicione os passos do fluxo na ordem desejada.")
    n_passos = st.number_input("Número de Passos", min_value=1, max_value=20, value=4)
    passos = []

    for i in range(int(n_passos)):
        passo = st.text_input(f"Passo {i+1}", key=f"passo_{i}")
        passos.append(passo)

    if st.button("Gerar Fluxograma"):
        dot = "digraph fluxo {\n"
        for i in range(len(passos) - 1):
            dot += f'"{passos[i]}" -> "{passos[i+1]}";\n'
        dot += "}"
        st.graphviz_chart(dot)
        st.info("Para salvar: clique com botão direito ou use captura de tela.")

# ------------------------------
# MAPA MENTAL usando Graphviz
# ------------------------------
elif opcao == "Mapa Mental":
    st.header("🧠 Mapa Mental")
    conceito_principal = st.text_input("Conceito Central", "Assunto Principal")
    n_ramos = st.number_input("Número de Ramificações", min_value=1, max_value=20, value=5)
    ramos = []

    for i in range(int(n_ramos)):
        ramo = st.text_input(f"Ramificação {i+1}", key=f"ramo_{i}")
        ramos.append(ramo)

    if st.button("Gerar Mapa Mental"):
        dot = f'graph mapa {{\n"{conceito_principal}";\n'
        for filho in ramos:
            dot += f'"{conceito_principal}" -- "{filho}";\n'
        dot += "}"
        st.graphviz_chart(dot)
        st.info("Para salvar: clique com botão direito ou use print de tela.")

# ------------------------------
# DESENHO LIVRE usando Canvas
# ------------------------------
elif opcao == "Desenho Livre":
    st.header("✏️ Desenho Livre")
    st.write("Desenhe livremente ou faça rascunhos para suas petições.")

    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=3,
        stroke_color="#000000",
        background_color="#FFFFFF",
        update_streamlit=True,
        height=400,
        width=800,
        drawing_mode="freedraw",
        key="canvas"
    )

    if canvas_result.image_data is not None:
        buf = io.BytesIO()
        plt.imsave(buf, canvas_result.image_data)
        st.download_button("📥 Baixar Desenho", buf.getvalue(), "desenho_livre.png", "image/png")
