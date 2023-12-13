import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import heapq

class ImagePathFinder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Seletor de Ponto de Imagem")

        self.ponto_inicio = None
        self.ponto_destino = None
        self.imagem_atual = None
        self.caminho_imagem = None
        self.fator_escala = 20

        self._setup_ui()

    def _setup_ui(self):
        self.btn_carregar = tk.Button(self.root, text="Carregar Imagem", command=self.escolher_imagem)
        self.btn_carregar.pack()

        self.btn_buscar_caminho = tk.Button(self.root, text="Encontrar Caminho", command=self.executar_busca_caminho)
        self.btn_buscar_caminho.pack()

        self.btn_resetar = tk.Button(self.root, text="Resetar Imagem", command=self.resetar_imagem)
        self.btn_salvar = tk.Button(self.root, text="Salvar Imagem", command=self.salvar_imagem)
        
        self.inicio_label = tk.Label(self.root, text="")
        self.inicio_label.pack()

        self.destino_label = tk.Label(self.root, text="")
        self.destino_label.pack()

        self.caminho_label = tk.Label(self.root, text="")
        self.caminho_label.pack()


        self.label_imagem = tk.Label(self.root)
        self.label_imagem.pack()
        self.label_imagem.bind("<Button-1>", self.on_click)

    def escolher_imagem(self):
        try:
            caminho_imagem = filedialog.askopenfilename()
            if caminho_imagem:
                self.caminho_imagem = caminho_imagem
                imagem = Image.open(caminho_imagem)
                tamanho_novo = (imagem.width * self.fator_escala, imagem.height * self.fator_escala)
                imagem = imagem.resize(tamanho_novo, Image.NEAREST)
                foto = ImageTk.PhotoImage(imagem)
                self.label_imagem.config(image=foto)
                self.label_imagem.image = foto
                self.imagem_atual = imagem
                self.ponto_inicio = None
                self.ponto_destino = None
        except Exception as e:
            messagebox.showerror("Erro ao Carregar Imagem", str(e))

    def on_click(self, event):
        x, y = event.x // self.fator_escala, event.y // self.fator_escala
        if self.ponto_inicio == (x, y):
            self.ponto_inicio = None
            self.inicio_label.config(text="Ponto de início desmarcado.")
        elif self.ponto_destino == (x, y):
            self.ponto_destino = None
            self.destino_label.config(text="Ponto de destino desmarcado.")
        elif not self.ponto_inicio:
            self.ponto_inicio = (x, y)
            self.inicio_label.config(text=f"Ponto de início definido: {self.ponto_inicio}")
        elif not self.ponto_destino:
            self.ponto_destino = (x, y)
            self.destino_label.config(text=f"Ponto de destino definido: {self.ponto_destino}")
        else:
            messagebox.showinfo("Informação", "Ponto de início e destino já definidos!")
            
    def ler_bitmap(self, caminho_arquivo):
        with Image.open(caminho_arquivo) as img:
            img = img.convert('RGB')
            largura, altura = img.size
            return list(img.getdata()), largura, altura

    def encontrar_pontos(self, pixels, largura, altura):
        cor_inicio = (255, 0, 0)  # Vermelho
        cor_destino = (0, 255, 0)  # Verde
        ponto_inicio = ponto_destino = None

        matriz = [pixels[i * largura:(i + 1) * largura] for i in range(altura)]
        for y in range(altura):
            for x in range(largura):
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
                if matriz[y][x] != (0, 0, 0):
                    grafo[(x, y)] = []
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < largura and 0 <= ny < altura and matriz[ny][nx] != (0, 0, 0):
                            grafo[(x, y)].append((nx, ny))
        return grafo

    def dijkstra(self, grafo, inicio, destino):
        fila_prioridade = [(0, inicio)]
        visitados = set()
        caminho = {inicio: None}

        while fila_prioridade:
            dist_atual, atual = heapq.heappop(fila_prioridade)
            if atual in visitados:
                continue
            visitados.add(atual)

            if atual == destino:
                break

            for vizinho in grafo[atual]:
                if vizinho not in visitados:
                    dist_vizinho = dist_atual + 1
                    heapq.heappush(fila_prioridade, (dist_vizinho, vizinho))
                    caminho[vizinho] = atual

        if destino not in caminho:
            return None

        percurso = []
        while destino is not None:
            percurso.append(destino)
            destino = caminho[destino]
        return percurso[::-1]

    def desenhar_caminho(self, caminho):
        with Image.open(self.caminho_imagem) as img:
            img = img.convert('RGB')
            pixels = img.load()
            for x, y in caminho:
                pixels[x, y] = (0, 0, 255)
            tamanho_novo = (img.width * self.fator_escala, img.height * self.fator_escala)
            img = img.resize(tamanho_novo, Image.NEAREST)
            self.imagem_atual = img
            foto_atualizada = ImageTk.PhotoImage(img)
            self.label_imagem.config(image=foto_atualizada)
            self.label_imagem.image = foto_atualizada

    def executar_busca_caminho(self):
        if self.caminho_imagem:
            pixels, largura, altura = self.ler_bitmap(self.caminho_imagem)
            matriz, self.ponto_inicio, self.ponto_destino = self.encontrar_pontos(pixels, largura, altura)

            if self.ponto_inicio and self.ponto_destino:
                grafo = self.construir_grafo(matriz)
                caminho_encontrado = self.dijkstra(grafo, self.ponto_inicio, self.ponto_destino)
                if caminho_encontrado:
                    self.desenhar_caminho(caminho_encontrado)
                    self.caminho_label.config(text="Caminho mais curto encontrado.")

                    # Mostrar os botões de resetar e salvar após encontrar o caminho
                    self.btn_resetar.pack()
                    self.btn_salvar.pack()
                else:
                    messagebox.showerror("Erro", "Caminho não encontrado.")
            else:
                messagebox.showwarning("Aviso", "Pontos de início e destino não identificados na imagem.")


    def resetar_imagem(self):
        if self.caminho_imagem:
            self.carregar_imagem(self.caminho_imagem)
            self.ponto_inicio = None
            self.ponto_destino = None
            self.inicio_label.config(text="Ponto de início desmarcado.")
            self.destino_label.config(text="Ponto de destino desmarcado.")
            self.caminho_label.config(text="Caminho desmarcado.")


    def salvar_imagem(self):
        if self.imagem_atual:
            caminho_salvar = filedialog.asksaveasfilename(defaultextension=".bmp")
            if caminho_salvar:
                self.imagem_atual.save(caminho_salvar)
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
    app = ImagePathFinder()
    app.root.mainloop()

if __name__ == "__main__":
    main()
