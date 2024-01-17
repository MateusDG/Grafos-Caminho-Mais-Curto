import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import heapq

class Teste:
    def __init__(self):
        # Aqui a gente começa configurando a janela principal.
        self.root = tk.Tk()
        self.root.title("Seletor de Ponto de Imagem")
        self.root.geometry("600x500")

        # Agora, vamos mexer no visual dos botões e outros elementos.
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Essas variáveis vão guardar informações importantes mais pra frente.
        self.ponto_inicio = None
        self.ponto_destino = None
        self.imagem_atual = None
        self.caminho_imagem = None
        self.fator_escala = 8

        # Chama a função que monta a interface do usuário.
        self._setup_ui()

    def _setup_ui(self):
        # Criando o layout, colocando uns botões, labels e tal.
        frame = ttk.Frame(self.root, padding="10")
        frame.pack(expand=True, fill=tk.BOTH)

        # Botão para carregar a imagem.
        self.btn_carregar = ttk.Button(frame, text="Carregar Imagem", command=self.escolher_imagem)
        self.btn_carregar.pack(expand=True, pady=5)

        # Botão que vai procurar o caminho na imagem.
        self.btn_buscar_caminho = ttk.Button(frame, text="Encontrar Caminho", command=self.executar_busca_caminho)
        self.btn_buscar_caminho.pack(expand=True, pady=5)

        # Mais alguns botões que a gente vai usar depois.
        self.btn_resetar = ttk.Button(frame, text="Resetar Imagem", command=self.resetar_imagem)
        self.btn_resetar.pack_forget()

        self.btn_salvar = ttk.Button(frame, text="Salvar Imagem", command=self.salvar_imagem)
        self.btn_salvar.pack_forget()
        
        # Uns labels pra mostrar informações.
        self.caminho_label = ttk.Label(frame, text="")
        self.caminho_label.pack(pady=5)

        self.label_imagem = ttk.Label(frame)
        self.label_imagem.pack(expand=True, pady=10)
        
        self.inicio_label = ttk.Label(frame, text="")
        self.inicio_label.pack(pady=5)

        self.destino_label = ttk.Label(frame, text="")
        self.destino_label.pack(pady=5)

        self.status_label = ttk.Label(frame, text="")
        self.status_label.pack()
        

    def escolher_imagem(self):
        try:
            # Aqui a gente abre uma janela pra escolher um arquivo de imagem.
            caminho_imagem = filedialog.askopenfilename()
            if caminho_imagem:
                # Legal, escolheu a imagem. Agora vamos carregá-la.
                self.caminho_imagem = caminho_imagem
                imagem = Image.open(caminho_imagem)
                # Dá um zoom na imagem pra ver melhor.
                tamanho_novo = (imagem.width * self.fator_escala, imagem.height * self.fator_escala)
                imagem = imagem.resize(tamanho_novo, Image.NEAREST)
                # Converte a imagem pra um formato que dá pra mostrar na interface.
                foto = ImageTk.PhotoImage(imagem)
                # Atualiza o label pra mostrar a imagem.
                self.label_imagem.config(image=foto)
                self.label_imagem.image = foto
                # Guarda a imagem pra usar depois.
                self.imagem_atual = imagem
                # Reseta os pontos de início e destino, porque são pra essa imagem nova.
                self.ponto_inicio = None
                self.ponto_destino = None
        except Exception as e:
            # Ops, deu ruim. Melhor avisar o usuário.
            messagebox.showerror("Erro ao Carregar Imagem", str(e))
            
            
    def ler_bitmap(self, caminho_arquivo):
        # Abre a imagem e transforma em uma lista de pixels.
        with Image.open(caminho_arquivo) as img:
            img = img.convert('RGB')
            largura, altura = img.size
            return list(img.getdata()), largura, altura


    def encontrar_pontos(self, pixels, largura, altura):
        # Define as cores que representam o início e o destino.
        cor_inicio = (255, 0, 0)  # Vermelho
        cor_destino = (0, 255, 0)  # Verde
        ponto_inicio = ponto_destino = None

        # Cria uma matriz com os pixels da imagem.
        matriz = [pixels[i * largura:(i + 1) * largura] for i in range(altura)]
        for y in range(altura):
            for x in range(largura):
                # Procura pelos pixels que têm as cores de início e destino.
                if matriz[y][x] == cor_inicio:
                    ponto_inicio = (x, y)
                elif matriz[y][x] == cor_destino:
                    ponto_destino = (x, y)

        return matriz, ponto_inicio, ponto_destino

    
    def construir_grafo(self, matriz):
        altura = len(matriz)
        largura = len(matriz[0])
        grafo = {}
        for y in range(altura):
            for x in range(largura):
                if matriz[y][x] != (0, 0, 0):  # Se não é pixel preto
                    grafo[(x, y)] = []
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < largura and 0 <= ny < altura and matriz[ny][nx] != (0, 0, 0):
                            # Atribuir peso com base na cor do pixel
                            if matriz[ny][nx] == (128, 128, 128):  # Cinza escuro
                                peso = 2
                            elif matriz[ny][nx] == (196, 196, 196):  # Cinza claro
                                peso = 1.5
                            else:  # Branco ou outro
                                peso = 1
                            grafo[(x, y)].append((nx, ny, peso))
        return grafo

    def dijkstra(self, grafo, inicio, destino):
        dist = {v: float('inf') for v in grafo}
        dist[inicio] = 0
        pq = [(0, inicio)]
        anterior = {inicio: None}

        while pq:
            distancia_atual, vertice_atual = heapq.heappop(pq)
            
            if vertice_atual == destino:
                break

            for vizinho in grafo[vertice_atual]:
                nx, ny, peso = vizinho
                distancia = distancia_atual + peso
                if distancia < dist[(nx, ny)]:
                    dist[(nx, ny)] = distancia
                    anterior[(nx, ny)] = vertice_atual
                    heapq.heappush(pq, (distancia, (nx, ny)))
        
        # Reconstituir o caminho
        caminho = []
        atual = destino
        while atual is not None:
            caminho.append(atual)
            atual = anterior[atual]
        return caminho[::-1]


    def desenhar_caminho(self, caminho):
        # Abre a imagem original e desenha o caminho encontrado nela.
        with Image.open(self.caminho_imagem) as img:
            img = img.convert('RGB')
            pixels = img.load()
            for x, y in caminho:
                pixels[x, y] = (0, 0, 255)  # Desenha o caminho de azul.
            # Ajusta o tamanho da imagem e atualiza na interface.
            tamanho_novo = (img.width * self.fator_escala, img.height * self.fator_escala)
            img = img.resize(tamanho_novo, Image.NEAREST)
            self.imagem_atual = img
            foto_atualizada = ImageTk.PhotoImage(img)
            self.label_imagem.config(image=foto_atualizada)
            self.label_imagem.image = foto_atualizada


    def executar_busca_caminho(self):
        # Primeiro passo, ler a imagem e encontrar os pontos de início e destino.
        if self.caminho_imagem:
            pixels, largura, altura = self.ler_bitmap(self.caminho_imagem)
            matriz, self.ponto_inicio, self.ponto_destino = self.encontrar_pontos(pixels, largura, altura)

            if self.ponto_inicio and self.ponto_destino:
                # Monta o grafo e faz a busca pelo menor caminho.
                grafo = self.construir_grafo(matriz)
                caminho_encontrado = self.dijkstra(grafo, self.ponto_inicio, self.ponto_destino)
                if caminho_encontrado:
                    # Desenha o caminho na imagem e atualiza na interface.
                    self.desenhar_caminho(caminho_encontrado)
                    self.caminho_label.config(text="Caminho mais curto encontrado.")
                    self.btn_resetar.pack()
                    self.btn_salvar.pack()
                else:
                    messagebox.showerror("Erro", "Caminho não encontrado.")
            else:
                messagebox.showwarning("Aviso", "Pontos de início e destino não identificados na imagem.")


    def resetar_imagem(self):
        self.carregar_imagem(self.caminho_imagem)
        self.ponto_inicio = None
        self.ponto_destino = None
        self.inicio_label.config(text="Ponto de início desmarcado.")
        self.destino_label.config(text="Ponto de destino desmarcado.")
        self.caminho_label.config(text="Caminho desmarcado.")
        self.btn_resetar.pack_forget()
        self.btn_salvar.pack_forget()


    def salvar_imagem(self):
        if self.imagem_atual:
            caminho_salvar = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All Files", "*.*")])
            if caminho_salvar:
                tamanho_original = (self.imagem_atual.width // self.fator_escala, self.imagem_atual.height // self.fator_escala)
                imagem_para_salvar = self.imagem_atual.resize(tamanho_original)
                imagem_para_salvar.save(caminho_salvar)
                messagebox.showinfo("Salvar Imagem", "Imagem salva com sucesso.")

    def carregar_imagem(self, caminho_imagem):
        try:
            imagem = Image.open(caminho_imagem)
            tamanho_novo = (imagem.width * self.fator_escala, imagem.height * self.fator_escala)
            imagem = imagem.resize(tamanho_novo, Image.NEAREST)
            foto = ImageTk.PhotoImage(imagem)
            self.label_imagem.config(image=foto)
            self.label_imagem.image = foto
            self.imagem_atual = imagem
        except Exception as e:
            messagebox.showerror("Erro ao Carregar Imagem", str(e))

def main():
    app = Teste()
    app.root.mainloop()

if __name__ == "__main__":
    main()

