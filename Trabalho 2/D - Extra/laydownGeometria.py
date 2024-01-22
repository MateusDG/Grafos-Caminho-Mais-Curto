import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from collections import deque

class Teste:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Seletor de Ponto de Imagem com Laydown")
        self.root.geometry("600x500")

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.ponto_inicio = None
        self.caminho_imagem = None
        self.imagem_atual = None
        self.fator_escala = 8

        self._setup_ui()

    def _setup_ui(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.pack(expand=True, fill=tk.BOTH)

        self.btn_carregar = ttk.Button(frame, text="Carregar Imagem", command=self.escolher_imagem)
        self.btn_carregar.pack(expand=True, pady=5)

        self.btn_buscar_caminho = ttk.Button(frame, text="Encontrar Caminho", command=self.executar_busca_caminho)
        self.btn_buscar_caminho.pack(expand=True, pady=5)

        self.btn_resetar = ttk.Button(frame, text="Resetar Imagem", command=self.resetar_imagem)
        self.btn_resetar.pack_forget()

        self.btn_salvar = ttk.Button(frame, text="Salvar Imagem", command=self.salvar_imagem)
        self.btn_salvar.pack_forget()
        
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
            caminho_imagem = filedialog.askopenfilename()
            if caminho_imagem:
                self.caminho_imagem = caminho_imagem
                self.carregar_imagem(caminho_imagem)
        except Exception as e:
            messagebox.showerror("Erro ao Carregar Imagem", str(e))

    def carregar_imagem(self, caminho_imagem):
        imagem = Image.open(caminho_imagem)
        tamanho_novo = (imagem.width * self.fator_escala, imagem.height * self.fator_escala)
        imagem = imagem.resize(tamanho_novo, Image.NEAREST)
        foto = ImageTk.PhotoImage(imagem)
        self.label_imagem.config(image=foto)
        self.label_imagem.image = foto
        self.imagem_atual = imagem
            
    def encontrar_melhor_caminho(self, grafo, destinos):
        menor_caminho = None
        menor_distancia = float('inf')

        for destino in destinos:
            caminho = self.bfs(grafo, self.ponto_inicio, destino)
            if caminho:
                distancia = len(caminho)
                if distancia < menor_distancia:
                    menor_caminho = caminho
                    menor_distancia = distancia

        return menor_caminho

    def bfs(self, grafo, inicio, destino):
        fila = deque([inicio])
        visitados = {inicio: None}

        while fila:
            atual = fila.popleft()
            
            if atual == destino:
                break

            # Verificar se 'atual' é um ponto válido no grafo
            if atual not in grafo:
                continue

            for vizinho in grafo[atual]:
                if vizinho not in visitados:
                    fila.append(vizinho)
                    visitados[vizinho] = atual

        if destino not in visitados:
            return None

        percurso = []
        while destino is not None:
            percurso.append(destino)
            destino = visitados[destino]
        return percurso[::-1]

    
    def desenhar_caminho(self, caminho, objeto_inicio):
        x_min, y_min, x_max, y_max, tipo_forma = objeto_inicio
        tamanho_objeto = (x_max - x_min + 1, y_max - y_min + 1)

        with Image.open(self.caminho_imagem) as img:
            img = img.convert('RGB')
            pixels = img.load()
            for pos in caminho:
                x, y = pos
                for dy in range(tamanho_objeto[1]):
                    for dx in range(tamanho_objeto[0]):
                        if 0 <= x + dx < img.width and 0 <= y + dy < img.height:
                            pixels[x + dx, y + dy] = (0, 0, 255)  # Desenha o caminho de azul.

            tamanho_novo = (img.width * self.fator_escala, img.height * self.fator_escala)
            img = img.resize(tamanho_novo, Image.NEAREST)
            self.imagem_atual = img
            foto_atualizada = ImageTk.PhotoImage(img)
            self.label_imagem.config(image=foto_atualizada)
            self.label_imagem.image = foto_atualizada


    def executar_busca_caminho(self):
        if self.caminho_imagem:
            pixels, largura, altura = self.ler_bitmap(self.caminho_imagem)
            matriz, objeto_inicio, destinos = self.encontrar_pontos(pixels, largura, altura)

            if objeto_inicio and destinos:
                grafo = self.construir_grafo(matriz, objeto_inicio)
                x_min, y_min = objeto_inicio[:2]  # Coordenadas do ponto de início

                self.ponto_inicio = (x_min, y_min)

                if (x_min, y_min) in grafo:  # Verificar se o ponto de início é válido no grafo
                    melhor_caminho = self.encontrar_melhor_caminho(grafo, destinos)

                    if melhor_caminho:
                        self.desenhar_caminho(melhor_caminho, objeto_inicio)
                        self.caminho_label.config(text="Caminho mais curto encontrado.")
                        self.btn_resetar.pack(expand=True, pady=5)
                        self.btn_salvar.pack(expand=True, pady=5)
                    else:
                        messagebox.showerror("Erro", "Caminho não encontrado para nenhum destino.")
                else:
                    messagebox.showerror("Erro", "Ponto de início não é válido.")
            else:
                messagebox.showwarning("Aviso", "Ponto de início ou destinos não identificados.")


    def ler_bitmap(self, caminho_arquivo):
        # Abre a imagem e transforma em uma lista de pixels.
        with Image.open(caminho_arquivo) as img:
            img = img.convert('RGB')
            largura, altura = img.size
            return list(img.getdata()), largura, altura

    def encontrar_pontos(self, pixels, largura, altura):
        cor_inicio = (255, 0, 0)  # Vermelho
        cor_destino = (0, 255, 0)  # Verde
        pontos_inicio = []
        destinos = []

        matriz = [pixels[i * largura:(i + 1) * largura] for i in range(altura)]
        for y in range(altura):
            for x in range(largura):
                if matriz[y][x] == cor_inicio:
                    pontos_inicio.append((x, y))
                elif matriz[y][x] == cor_destino:
                    destinos.append((x, y))

        objeto_inicio = self.identificar_geometria_objeto(pontos_inicio)

        return matriz, objeto_inicio, destinos

    def identificar_geometria_objeto(self, pontos):
        if not pontos:
            return None

        x_min = min(pontos, key=lambda p: p[0])[0]
        x_max = max(pontos, key=lambda p: p[0])[0]
        y_min = min(pontos, key=lambda p: p[1])[1]
        y_max = max(pontos, key=lambda p: p[1])[1]

        largura = x_max - x_min + 1
        altura = y_max - y_min + 1

        if largura == altura:
            tipo_forma = "quadrado"
        else:
            tipo_forma = "retângulo"

        return (x_min, y_min, x_max, y_max, tipo_forma)  # Coordenadas e tipo da forma


    def construir_grafo(self, matriz, objeto_inicio):
        altura = len(matriz)
        largura = len(matriz[0])
        x_min, y_min, x_max, y_max, tipo_forma = objeto_inicio  # Adicionando tipo_forma
        tamanho_objeto = (x_max - x_min + 1, y_max - y_min + 1)

        grafo = {}
        for y in range(altura - tamanho_objeto[1] + 1):
            for x in range(largura - tamanho_objeto[0] + 1):
                # Verificar se o objeto cabe nesta posição sem colidir com obstáculos
                if self.espaco_livre_para_objeto(matriz, x, y, tamanho_objeto):
                    grafo[(x, y)] = self.vizinhos_para_objeto(x, y, largura, altura, tamanho_objeto)

        return grafo

    def espaco_livre_para_objeto(self, matriz, x, y, tamanho_objeto):
        for dy in range(tamanho_objeto[1]):
            for dx in range(tamanho_objeto[0]):
                if matriz[y + dy][x + dx] == (0, 0, 0):  # Obstáculo encontrado
                    return False
        return True

    def vizinhos_para_objeto(self, x, y, largura, altura, tamanho_objeto):
        vizinhos = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < largura - tamanho_objeto[0] + 1 and 0 <= ny < altura - tamanho_objeto[1] + 1:
                vizinhos.append((nx, ny))
        return vizinhos

    def resetar_imagem(self):
        if self.caminho_imagem:
            self.carregar_imagem(self.caminho_imagem)  # Recarrega a imagem para remover o caminho
            self.ponto_inicio = None
            self.caminho_label.config(text="Caminho desmarcado.")

    def salvar_imagem(self):
        if self.imagem_atual:
            caminho_salvar = filedialog.asksaveasfilename(defaultextension=".bmp")
            if caminho_salvar:
                self.imagem_atual.save(caminho_salvar)
                messagebox.showinfo("Salvar Imagem", "Imagem salva com sucesso.")
    
def main():
    app = Teste()
    app.root.mainloop()

if __name__ == "__main__":
    main()
