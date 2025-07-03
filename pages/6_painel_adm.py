import streamlit as st
import json
import os

# ---------------- CONFIGURAÇÕES ----------------
st.set_page_config(page_title="🗂️ Painel de Edição de Peças Jurídicas", layout="wide")

DATA_DIR = "prompts/Peças"

# ---------------- FUNÇÕES ----------------
def load_json(area):
    path = f"{DATA_DIR}/{area}.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(area, data):
    with open(f"{DATA_DIR}/{area}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_areas():
    return [f.replace(".json", "") for f in os.listdir(DATA_DIR) if f.endswith(".json")]

# ---------------- APP ----------------
st.sidebar.title("🗂️ Painel de Edição ADMIN")
action = st.sidebar.radio("Ação:", ["Navegar & Editar", "Criar Nova Peça"])

areas = get_areas()
area = st.sidebar.selectbox("Área do Direito:", ["Selecione..."] + areas)

if area and area != "Selecione...":
    data = load_json(area)

    if action == "Navegar & Editar":
        st.header(f"📑 Navegar, Editar ou Apagar em **{area}**")

        caminho = []
        nivel_atual = data
        nivel = 0

        while isinstance(nivel_atual, dict):
            opcoes = list(nivel_atual.keys())
            if not opcoes:
                break

            escolha = st.selectbox(f"Nível {nivel+1}:", opcoes + ["-- NOVO --"], key=f"nivel_{nivel}")

            if escolha == "-- NOVO --":
                nova_cat = st.text_input(f"Novo Nível {nivel+1}", key=f"nova_cat_{nivel}")
                if st.button(f"➕ Criar Categoria Aqui", key=f"btn_criar_{nivel}"):
                    nivel_atual[nova_cat] = {}
                    save_json(area, data)
                    st.success("Nova categoria criada.")
                    st.experimental_rerun()
                break

            else:
                caminho.append(escolha)

                col1, col2 = st.columns(2)
                with col1:
                    novo_nome = st.text_input(f"Renomear '{escolha}' para:", value=escolha, key=f"rename_{nivel}")
                    if novo_nome != escolha and st.button(f"✅ Renomear '{escolha}'", key=f"btn_rename_{nivel}"):
                        nivel_pai = data
                        for c in caminho[:-1]:
                            nivel_pai = nivel_pai[c]
                        nivel_pai[novo_nome] = nivel_pai.pop(escolha)
                        save_json(area, data)
                        st.success("Renomeado com sucesso.")
                        st.experimental_rerun()

                with col2:
                    if st.button(f"❌ Excluir '{escolha}'", key=f"btn_del_{nivel}"):
                        nivel_pai = data
                        for c in caminho[:-1]:
                            nivel_pai = nivel_pai[c]
                        del nivel_pai[escolha]
                        save_json(area, data)
                        st.success(f"Nível '{escolha}' excluído.")
                        st.experimental_rerun()

                nivel_atual = nivel_atual[escolha]
                nivel += 1

        if isinstance(nivel_atual, dict) and "campos" in nivel_atual:
            st.subheader(f"📄 Editar Peça: {' > '.join(caminho)}")

            nome_peca = caminho[-1]
            novo_nome_peca = st.text_input("Renomear Peça:", value=nome_peca, key="rename_peca")
            permite_upload = st.checkbox("Permitir Upload?", value=nivel_atual.get("permite_upload", False))
            prompt = st.text_area("Prompt Base", value=nivel_atual.get("prompt", ""))

            campos = nivel_atual.get("campos", [])
            novos_campos = []
            for i, campo in enumerate(campos):
                st.subheader(f"Campo #{i+1}")
                nome = st.text_input("Nome", value=campo["nome"], key=f"nome_{i}")
                label = st.text_input("Label", value=campo["label"], key=f"label_{i}")
                tipo = st.selectbox("Tipo", ["text", "textarea"], index=["text", "textarea"].index(campo["tipo"]), key=f"tipo_{i}")
                regex = campo.get("validacao", {}).get("regex", "")
                msg = campo.get("validacao", {}).get("mensagem_erro", "")
                regex = st.text_input("Regex (opcional)", value=regex, key=f"regex_{i}")
                msg = st.text_input("Mensagem de Erro", value=msg, key=f"msg_{i}")
                campo_editado = {"nome": nome, "label": label, "tipo": tipo}
                if regex:
                    campo_editado["validacao"] = {"regex": regex, "mensagem_erro": msg}
                novos_campos.append(campo_editado)

            grupos_extras = nivel_atual.get("grupos_extras", [])
            novos_grupos = []
            num_grupos = st.number_input("Número de Grupos Extras", min_value=0, value=len(grupos_extras))
            for g in range(num_grupos):
                st.subheader(f"Grupo Extra #{g+1}")
                if g < len(grupos_extras):
                    grupo = grupos_extras[g]
                else:
                    grupo = {"nome_grupo": "", "label_grupo": "", "campos": []}
                nome_grupo = st.text_input(f"Nome Interno do Grupo #{g+1}", value=grupo.get("nome_grupo", ""), key=f"g_nome_{g}")
                label_grupo = st.text_input(f"Label do Grupo #{g+1}", value=grupo.get("label_grupo", ""), key=f"g_label_{g}")
                campos_grupo = []
                num_campos_grupo = st.number_input(f"Número de Campos no Grupo #{g+1}", min_value=0, value=len(grupo.get("campos", [])), key=f"g_numcampos_{g}")
                for c in range(num_campos_grupo):
                    if c < len(grupo.get("campos", [])):
                        campo_antigo = grupo["campos"][c]
                    else:
                        campo_antigo = {"nome": "", "label": "", "tipo": "text"}
                    nome_campo = st.text_input(f"Nome Campo Grupo #{g+1} Campo #{c+1}", value=campo_antigo.get("nome", ""), key=f"g_{g}_c_nome_{c}")
                    label_campo = st.text_input(f"Label Campo Grupo #{g+1} Campo #{c+1}", value=campo_antigo.get("label", ""), key=f"g_{g}_c_label_{c}")
                    tipo_campo = st.selectbox(f"Tipo Campo Grupo #{g+1} Campo #{c+1}", ["text", "textarea"], index=["text", "textarea"].index(campo_antigo.get("tipo", "text")), key=f"g_{g}_c_tipo_{c}")
                    regex = campo_antigo.get("validacao", {}).get("regex", "")
                    msg = campo_antigo.get("validacao", {}).get("mensagem_erro", "")
                    regex = st.text_input(f"Regex Campo Grupo #{g+1} Campo #{c+1} (opcional)", value=regex, key=f"g_{g}_c_regex_{c}")
                    msg = st.text_input(f"Mensagem de Erro Campo Grupo #{g+1} Campo #{c+1} (opcional)", value=msg, key=f"g_{g}_c_msg_{c}")
                    campo_extra = {"nome": nome_campo, "label": label_campo, "tipo": tipo_campo}
                    if regex:
                        campo_extra["validacao"] = {"regex": regex, "mensagem_erro": msg}
                    campos_grupo.append(campo_extra)
                novos_grupos.append({"nome_grupo": nome_grupo, "label_grupo": label_grupo, "campos": campos_grupo})

            if st.button("💾 Salvar Alterações na Peça"):
                nivel_pai = data
                for c in caminho[:-1]:
                    nivel_pai = nivel_pai[c]
                nivel_pai.pop(nome_peca)
                nivel_pai[novo_nome_peca] = {
                    "permite_upload": permite_upload,
                    "prompt": prompt,
                    "campos": novos_campos,
                    "grupos_extras": novos_grupos
                }
                save_json(area, data)
                st.success("Peça editada com sucesso.")
                st.experimental_rerun()

            if st.button("❌ Excluir Peça"):
                nivel_pai = data
                for c in caminho[:-1]:
                    nivel_pai = nivel_pai[c]
                nivel_pai.pop(nome_peca)
                save_json(area, data)
                st.success("Peça excluída.")
                st.experimental_rerun()

    elif action == "Criar Nova Peça":
        st.header(f"➕ Criar Nova Peça em **{area}**")

        caminho = []
        nivel_atual = data
        nivel = 0
        while isinstance(nivel_atual, dict):
            opcoes = list(nivel_atual.keys())
            escolha = st.selectbox(f"Nível {nivel+1}:", opcoes + ["-- NOVO --"], key=f"new_nivel_{nivel}")

            if escolha == "-- NOVO --":
                nova_cat = st.text_input(f"Novo Nível {nivel+1}", key=f"new_cat_{nivel}")
                if nova_cat:
                    caminho.append(nova_cat)
                    break
                else:
                    break
            else:
                caminho.append(escolha)
                nivel_atual = nivel_atual[escolha]
                nivel += 1

        # ---------------- CRIAÇÃO MANUAL ----------------
        st.subheader("✏️ Criação Manual")
        nome_peca = st.text_input("Nome da Nova Peça")
        permite_upload = st.checkbox("Permitir Upload?")
        prompt = st.text_area("Prompt Base")

        campos = []
        num_campos = st.number_input("Número de Campos Fixos", min_value=0, step=1, value=0)
        for i in range(num_campos):
            st.subheader(f"Campo #{i+1}")
            nome = st.text_input(f"Nome do Campo #{i+1}", key=f"new_nome_{i}")
            label = st.text_input(f"Label do Campo #{i+1}", key=f"new_label_{i}")
            tipo_campo = st.selectbox(f"Tipo do Campo #{i+1}", ["text", "textarea"], key=f"new_tipo_{i}")
            regex = st.text_input(f"Regex (opcional) #{i+1}", key=f"new_regex_{i}")
            regex_msg = st.text_input(f"Mensagem de Erro (opcional) #{i+1}", key=f"new_msg_{i}")
            campo = {"nome": nome, "label": label, "tipo": tipo_campo}
            if regex:
                campo["validacao"] = {"regex": regex, "mensagem_erro": regex_msg}
            campos.append(campo)

        grupos_extras = []
        num_grupos = st.number_input("Número de Grupos Extras", min_value=0, step=1, value=0)
        for g in range(num_grupos):
            st.subheader(f"Grupo Extra #{g+1}")
            nome_grupo = st.text_input(f"Nome Interno do Grupo #{g+1}", key=f"new_g_nome_{g}")
            label_grupo = st.text_input(f"Label do Grupo #{g+1}", key=f"new_g_label_{g}")
            campos_grupo = []
            num_campos_grupo = st.number_input(f"Número de Campos no Grupo #{g+1}", min_value=0, step=1, value=0, key=f"new_g_numcampos_{g}")
            for c in range(num_campos_grupo):
                nome_campo = st.text_input(f"Nome Campo Grupo #{g+1} Campo #{c+1}", key=f"new_g_{g}_c_nome_{c}")
                label_campo = st.text_input(f"Label Campo Grupo #{g+1} Campo #{c+1}", key=f"new_g_{g}_c_label_{c}")
                tipo_campo = st.selectbox(f"Tipo Campo Grupo #{g+1} Campo #{c+1}", ["text", "textarea"], key=f"new_g_{g}_c_tipo_{c}")
                regex = st.text_input(f"Regex Campo Grupo #{g+1} Campo #{c+1} (opcional)", key=f"new_g_{g}_c_regex_{c}")
                regex_msg = st.text_input(f"Mensagem de Erro Campo Grupo #{g+1} Campo #{c+1} (opcional)", key=f"new_g_{g}_c_msg_{c}")
                campo_extra = {"nome": nome_campo, "label": label_campo, "tipo": tipo_campo}
                if regex:
                    campo_extra["validacao"] = {"regex": regex, "mensagem_erro": regex_msg}
                campos_grupo.append(campo_extra)
            grupos_extras.append({"nome_grupo": nome_grupo, "label_grupo": label_grupo, "campos": campos_grupo})

        if st.button("💾 Salvar Nova Peça (Manual)"):
            temp = data
            for cat in caminho:
                if cat not in temp:
                    temp[cat] = {}
                temp = temp[cat]
            temp[nome_peca] = {
                "permite_upload": permite_upload,
                "campos": campos,
                "grupos_extras": grupos_extras,
                "prompt": prompt
            }
            save_json(area, data)
            st.success(f"✅ Peça '{nome_peca}' criada com sucesso!")
            st.experimental_rerun()

        # ---------------- IMPORTAÇÃO JSON ----------------
        st.markdown("---")
        st.subheader("📥 Importar Peça via JSON Completo")
        nome_peca_json = st.text_input("Nome da Peça (para importar JSON)")
        raw_json = st.text_area("Cole aqui o JSON completo da peça")
        if st.button("✅ Importar e Salvar JSON da Peça"):
            try:
                new_piece = json.loads(raw_json)
                temp = data
                for cat in caminho:
                    if cat not in temp:
                        temp[cat] = {}
                    temp = temp[cat]
                temp[nome_peca_json] = new_piece
                save_json(area, data)
                st.success(f"✅ JSON importado e salvo como '{nome_peca_json}'!")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Erro ao importar JSON: {e}")

        # ---------------- NOVA OPÇÃO JSON CAMPOS+BLOCOS (CORRIGIDA) ----------------
        st.markdown("---")
        st.subheader("🆕 Criar Peça com JSON de Campos + Blocos")
        nome_peca_json_blocos = st.text_input("Nome da Peça (JSON Campos + Blocos)")
        permite_upload_blocos = st.checkbox("Permitir Upload? (JSON Campos + Blocos)")
        raw_json_blocos = st.text_area("Cole aqui o JSON do objeto Campos + Blocos Extras")
        prompt_blocos = st.text_area("Prompt Base (JSON Campos + Blocos)")
        if st.button("✅ Criar Peça com JSON Campos + Blocos"):
            try:
                blocos_parsed = json.loads(raw_json_blocos)
                temp = data
                for cat in caminho:
                    if cat not in temp:
                        temp[cat] = {}
                    temp = temp[cat]
                nova_peca = {
                    "permite_upload": permite_upload_blocos,
                    "prompt": prompt_blocos
                }
                nova_peca.update(blocos_parsed)  # Mescla campos e grupos no nível correto
                temp[nome_peca_json_blocos] = nova_peca
                save_json(area, data)
                st.success(f"✅ Peça '{nome_peca_json_blocos}' criada com sucesso com JSON Campos + Blocos!")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Erro ao criar JSON Campos + Blocos: {e}")

else:
    st.warning("⚠️ Nenhuma área selecionada ou JSON encontrado.")
