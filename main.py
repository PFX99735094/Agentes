import customtkinter as ctk
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# --- 1. Configuração do CustomTkinter e Variáveis de Ambiente ---
load_dotenv()
ctk.set_appearance_mode("System")  # Ou "Dark" ou "Light"
ctk.set_default_color_theme("blue")

# Inicializar LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

class AplicativoTesteProfissional(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Configurar a janela ---
        self.title("Teste de Afinidade Profissional")
        self.geometry("800x600")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- Widgets ---
        self.frame_top = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_top.grid(row=0, column=0, pady=(20, 10), sticky="ew")
        self.frame_top.grid_columnconfigure(0, weight=1)
        
        self.label_titulo = ctk.CTkLabel(self.frame_top, text="Teste de Afinidade Profissional", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_titulo.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        self.label_profissao = ctk.CTkLabel(self.frame_top, text="Digite a profissão que você deseja seguir:", font=ctk.CTkFont(size=16))
        self.label_profissao.grid(row=1, column=0, sticky="w", padx=(20, 0))
        
        self.entry_profissao = ctk.CTkEntry(self.frame_top, placeholder_text="Ex: Engenheiro de Software", width=300)
        self.entry_profissao.grid(row=1, column=1, padx=(10, 20), sticky="ew")
        
        self.btn_gerar_perguntas = ctk.CTkButton(self, text="Gerar Perguntas", command=self.gerar_perguntas)
        self.btn_gerar_perguntas.grid(row=1, column=0, pady=10, padx=20)
        
        self.label_status = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=14))
        self.label_status.grid(row=2, column=0, pady=10)
        
        self.scrollable_frame_perguntas = ctk.CTkScrollableFrame(self, label_text="Responda cada pergunta com uma nota de 1 a 10:")
        self.scrollable_frame_perguntas.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        self.scrollable_frame_perguntas.grid_columnconfigure(0, weight=1)

        self.btn_calcular = ctk.CTkButton(self, text="Calcular Resultado", command=self.calcular_resultado)
        self.btn_calcular.grid(row=4, column=0, pady=20)

        # --- Variáveis de estado ---
        self.perguntas = []
        self.sliders = []
        
    def criar_agentes_e_crew(self):
        pesquisador_agente = Agent(
            role="Pesquisador de Profissões",
            goal="Coletar informações essenciais sobre uma profissão, incluindo habilidades, rotina e desafios.",
            backstory="Um analista de carreiras dedicado a encontrar dados precisos sobre diferentes profissões.",
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
        return [pesquisador_agente, gerador_perguntas_agente]

    def criar_tarefas(self, profissao, agentes):
        tarefa_pesquisa = Task(
            description=f"Pesquisar sobre a profissão de {profissao}, focando em 'habilidades necessárias', 'rotina de trabalho', 'desafios' e 'perspectivas futuras'.",
            expected_output="Um relatório detalhado e bem estruturado com os principais pontos da profissão.",
            agent=agentes[0]
        )

        tarefa_gerar_perguntas = Task(
            description=f"Com base na pesquisa sobre a profissão de {profissao}, crie uma lista de 10 perguntas. As perguntas devem ser do tipo 'Você se sentiria confortável...' ou 'Você se adaptaria a...' para testar a afinidade pessoal com a profissão. A saída deve ser apenas a lista numerada.",
            expected_output="Uma lista numerada de 10 perguntas sobre a profissão.",
            agent=agentes[1],
            context=[tarefa_pesquisa]
        )
        return [tarefa_pesquisa, tarefa_gerar_perguntas]

    def gerar_perguntas(self):
        profissao = self.entry_profissao.get()
        if not profissao:
            self.label_status.configure(text="Digite uma profissão antes de continuar.", text_color="orange")
            return
        
        self.label_status.configure(text=f"🔎 Procurando informações sobre {profissao}... Aguarde, por favor.", text_color="blue")
        self.update_idletasks() # Força a atualização da interface

        try:
            agentes = self.criar_agentes_e_crew()
            tarefas = self.criar_tarefas(profissao, agentes)
            
            crew = Crew(
                agents=agentes,
                tasks=tarefas,
                process=Process.sequential,
                verbose=False
            )

            # Executa a Crew
            resultado = crew.kickoff()
            
            # Processa as perguntas
            self.perguntas = [p.strip() for p in str(resultado).split("\n") if p.strip()]
            self.mostrar_perguntas()
            self.label_status.configure(text="", text_color="green")

        except Exception as e:
            self.label_status.configure(text=f"Erro ao gerar perguntas: {e}", text_color="red")
            
    def mostrar_perguntas(self):
        # Limpa widgets antigos
        for widget in self.scrollable_frame_perguntas.winfo_children():
            widget.destroy()

        self.sliders = []
        for i, pergunta in enumerate(self.perguntas):
            label_pergunta = ctk.CTkLabel(self.scrollable_frame_perguntas, text=f"**{i+1}.** {pergunta}", 
                                          wraplength=700, justify="left")
            label_pergunta.grid(row=i*2, column=0, pady=(10, 0), padx=10, sticky="w")
            
            slider = ctk.CTkSlider(self.scrollable_frame_perguntas, from_=1, to=10)
            slider.grid(row=i*2+1, column=0, pady=(0, 10), padx=20, sticky="ew")
            slider.set(5) # Valor inicial
            self.sliders.append(slider)

    def calcular_resultado(self):
        if not self.sliders:
            self.label_status.configure(text="Gere as perguntas antes de calcular o resultado.", text_color="orange")
            return

        notas = [int(slider.get()) for slider in self.sliders]
        media_score = sum(notas) / len(notas)
        
        self.label_status.configure(text=f"Sua nota média foi: {round(media_score, 2)}", font=ctk.CTkFont(size=16, weight="bold"))
        
        if media_score >= 5:
            self.label_status.configure(text_color="green")
            ctk.CTkMessagebox(title="Resultado Final", message=f"🎉 Parabéns!\nSua nota média foi: {round(media_score, 2)}\nEssa profissão parece ter muita afinidade com você.", icon="check")
        else:
            self.label_status.configure(text_color="red")
            ctk.CTkMessagebox(title="Resultado Final", message=f"🤔 Atenção!\nSua nota média foi: {round(media_score, 2)}\nTalvez essa profissão não se alinhe totalmente com seus interesses.", icon="warning")

if __name__ == "__main__":
    app = AplicativoTesteProfissional()
    app.mainloop()