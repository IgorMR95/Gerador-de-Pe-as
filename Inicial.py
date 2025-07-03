import streamlit as st

# Definir o título da página
st.set_page_config(
    page_title="Ferramentas com IA para Advogados",
    page_icon="⚖️",
    layout="centered",
)

# Título principal
st.title("Ferramentas com IA para Advogados")

# Subtítulo / slogan
st.subheader("Automatize tarefas repetitivas e potencialize sua atuação no Direito")

# Texto de boas-vindas / introdução
st.write("""
Bem-vindo ao **Ferramentas com IA para Advogados **!

Este aplicativo foi desenvolvido para oferecer soluções práticas e inteligentes, 
auxiliando profissionais do Direito Tributário a economizar tempo, reduzir erros 
e focar no que realmente importa: estratégia jurídica e atendimento ao cliente.

Navegue pelo menu lateral para explorar as funcionalidades disponíveis.
""")


# Chamada para ação
st.info("👉 Use o menu lateral para começar a explorar nossas ferramentas!")

# Rodapé
st.markdown("---")
st.caption("Desenvolvido por Igor M. Rocha")

