import streamlit as st
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# --- 1. Carregar variáveis de ambiente ---
load_dotenv()

# Inicializar LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# --- 2. Criar os Agentes ---
pesquisador_agente = Agent(
    role="Pesquisador de Profissões",
    goal="Coletar informações essenciais sobre uma profissão, incluindo habilidades necessárias, rotina diária e desafios.",
    backstory="Um analista de carreiras dedicado a encontrar dados precisos e relevantes sobre diferentes profissões.",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

gerador_perguntas_agente = Agent(
    role="Gerador de Perguntas",
    goal="Elaborar 10 perguntas profundas e reflexivas para testar se uma pessoa se encaixa em uma profissão.",
    backstory="Um especialista em coaching de carreira, capaz de criar perguntas que revelam a verdadeira aptidão e interesse de uma pessoa.",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# --- 3. Criar tarefas ---
def criar_tarefas(profissao):
    tarefa_pesquisa = Task(
        description=f"Pesquisar sobre a profissão de {profissao}, focando em 'habilidades necessárias', 'rotina de trabalho', 'desafios' e 'perspectivas futuras'.",
        expected_output="Um relatório detalhado e bem estruturado com os principais pontos da profissão.",
        agent=pesquisador_agente
    )

    tarefa_gerar_perguntas = Task(
        description=f"Com base na pesquisa sobre a profissão de {profissao}, crie uma lista de 10 perguntas. "
                    f"As perguntas devem ser do tipo 'Você se sentiria confortável...' ou 'Você se adaptaria a...' "
                    f"para testar a afinidade pessoal com a profissão. A saída deve ser apenas a lista numerada.",
        expected_output="Uma lista numerada de 10 perguntas sobre a profissão.",
        agent=gerador_perguntas_agente,
        context=[tarefa_pesquisa]
    )
    
    return [tarefa_pesquisa, tarefa_gerar_perguntas]

# --- 4. Streamlit Interface ---
st.title("Teste de Afinidade Profissional")
profissao_escolhida = st.text_input("Digite a profissão que você deseja seguir:")

# Inicializa session_state
if "perguntas" not in st.session_state:
    st.session_state.perguntas = []
if "notas" not in st.session_state:
    st.session_state.notas = []

# Gerar perguntas
if st.button("Gerar Perguntas"):
    if not profissao_escolhida:
        st.warning("Digite uma profissão antes de continuar.")
    else:
        st.info(f"🔎 Procurando informações e gerando perguntas sobre {profissao_escolhida}...")
        
        crew = Crew(
            agents=[pesquisador_agente, gerador_perguntas_agente],
            tasks=criar_tarefas(profissao_escolhida),
            process=Process.sequential,
            verbose=True
        )

        resultado = crew.kickoff()
        st.session_state.perguntas = [p.strip() for p in str(resultado).split("\n") if p.strip()]
        st.session_state.notas = [5] * len(st.session_state.perguntas)  # inicializa com nota 5

# Mostrar perguntas e sliders
if st.session_state.perguntas:
    st.subheader("Responda cada pergunta com uma nota de 1 a 10:")
    for i, pergunta in enumerate(st.session_state.perguntas):
        st.session_state.notas[i] = st.slider(pergunta, min_value=1, max_value=10, value=st.session_state.notas[i])

    # Calcular resultado
    if st.button("Calcular Resultado"):
        media_score = sum(st.session_state.notas) / len(st.session_state.notas)
        st.subheader("Resultados Finais")
        st.write(f"Sua nota média foi: **{round(media_score,2)}**")

        if media_score >= 5:
            st.success("🎉 Parabéns! Essa profissão parece ter muita afinidade com você.")
        else:
            st.warning("🤔 Talvez essa profissão não se alinhe totalmente com seus interesses.")
