import os
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# --- 1. Carregar variáveis de ambiente ---
load_dotenv()  # precisa ter OPENAI_API_KEY=xxxxxx no .env

# Inicializar LLM (pega chave do ambiente)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# --- 2. Criar os Agentes ---
pesquisador_agente = Agent(
    role="Pesquisador de Profissões",
    goal="Coletar informações essenciais sobre uma profissão, incluindo habilidades necessárias, rotina diária e desafios.",
    backstory="Um analista de carreiras dedicado a encontrar dados precisos e relevantes sobre diferentes profissões.",
    verbose=True,
    allow_delegation=False,
    llm=llm  # sem tools
)

gerador_perguntas_agente = Agent(
    role="Gerador de Perguntas",
    goal="Elaborar 10 perguntas profundas e reflexivas para testar se uma pessoa se encaixa em uma profissão.",
    backstory="Um especialista em coaching de carreira, capaz de criar perguntas que revelam a verdadeira aptidão e interesse de uma pessoa.",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# --- 3. Criar as Tarefas ---
def criar_tarefas(profissao):
    tarefa_pesquisa = Task(
        description=f"Pesquisar sobre a profissão de {profissao}, focando em 'habilidades necessárias', 'rotina de trabalho', 'desafios' e 'perspectivas futuras'.",
        expected_output="Um relatório detalhado e bem estruturado com os principais pontos da profissão.",
        agent=pesquisador_agente
    )

    tarefa_gerar_perguntas = Task(
        description=f"Com base na pesquisa sobre a profissão de {profissao}, crie uma lista de 10 perguntas. "
                    f"As perguntas devem ser do tipo 'Você se sentiria confortável...' ou 'Você se adaptaria a...' "
                    f"para testar a afinidade pessoal com a profissão. A saída deve ser apenas a lista de perguntas numeradas.",
        expected_output="Uma lista numerada de 10 perguntas sobre a profissão.",
        agent=gerador_perguntas_agente,
        context=[tarefa_pesquisa]
    )
    
    return [tarefa_pesquisa, tarefa_gerar_perguntas]

# --- 4. Iniciar o Projeto ---
def iniciar_projeto():
    profissao_escolhida = input("Digite a profissão que você deseja seguir: ")
    print(f"\n🔎 Procurando informações e gerando perguntas sobre a profissão de {profissao_escolhida}...\n")
    
    crew = Crew(
    agents=[pesquisador_agente, gerador_perguntas_agente],
    tasks=criar_tarefas(profissao_escolhida),
    process=Process.sequential,
    verbose=True  # ✅ deve ser boolean
)


    resultado = crew.kickoff()
    
    # Converte saída em string (para garantir compatibilidade)
    perguntas_texto = str(resultado)

    # --- 5. Interação com o usuário e avaliação ---
    print("\n" + "="*50)
    print(f"Teste de Afinidade com a Profissão de {profissao_escolhida}")
    print("Responda cada pergunta com uma nota de 1 (Nada a ver) a 10 (Totalmente a ver).")
    print("="*50 + "\n")
    
    score_total = 0
    perguntas_lista = [p.strip() for p in perguntas_texto.split("\n") if p.strip()]

    if not perguntas_lista:
        print("⚠️ Nenhuma pergunta foi gerada. Ocorreu um problema com a IA.")
        return

    for pergunta in perguntas_lista:
        while True:
            try:
                nota = int(input(f"\n{pergunta}\nSua nota (1-10): "))
                if 1 <= nota <= 10:
                    score_total += nota
                    break
                else:
                    print("Por favor, digite uma nota entre 1 e 10.")
            except ValueError:
                print("Entrada inválida. Por favor, digite um número.")

    # --- 6. Avaliação final ---
    media_score = score_total / len(perguntas_lista)
    nota_final = round(media_score, 2)
    
    print("\n" + "="*50)
    print("Resultados Finais")
    print("="*50)
    print(f"Sua nota média foi: {nota_final}")
    
    if nota_final >= 5:
        print("\n🎉 Parabéns! Com base em suas respostas, essa profissão parece ter muita afinidade com você.")
    else:
        print("\n🤔 Atenção: Sua nota sugere que talvez essa profissão não se alinhe totalmente com seus interesses.")
        print("Considere pesquisar outras áreas ou refletir mais sobre o que realmente te motiva.")

# Iniciar o programa
if __name__ == "__main__":
    iniciar_projeto()
