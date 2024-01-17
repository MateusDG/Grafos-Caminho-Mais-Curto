import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import heapq

class Teste3D:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Seletor de Ponto de Imagem 3D")
        self.root.geometry("600x600")  # Aumentei um pouco o tamanho para acomodar os controles extras

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.ponto_inicio = None
        self.ponto_destino = None
        self.imagens_atuais = []  # Lista para armazenar as imagens dos diferentes andares
        self.caminhos_imagem = []  # Lista para armazenar os caminhos dos arquivos de imagem
        self.fator_escala = 3

        self._setup_ui()

    def _setup_ui(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.pack(expand=True, fill=tk.BOTH)

        # Botão para carregar múltiplas imagens (andares).
        self.btn_carregar = ttk.Button(frame, text="Carregar Imagens", command=self.escolher_imagens)
        self.btn_carregar.pack(expand=True, pady=5)
        
        # Novos controles para navegar entre andares
        self.andar_atual = 0
        self.andar_label = ttk.Label(frame, text=f"Andar Atual: {self.andar_atual}")
        self.andar_label.pack(pady=5)
        self.btn_andar_acima = ttk.Button(frame, text="Subir Andar", command=self.subir_andar)
        self.btn_andar_acima.pack(pady=5)
        self.btn_andar_abaixo = ttk.Button(frame, text="Descer Andar", command=self.descer_andar)
        self.btn_andar_abaixo.pack(pady=5)

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

    def escolher_imagens(self):
        caminhos_imagens = filedialog.askopenfilenames()
        if caminhos_imagens:
            self.caminhos_imagem = caminhos_imagens
            print("Caminhos das imagens carregadas:", self.caminhos_imagem)  # Debug: Verificar os caminhos das imagens carregadas
            self.imagens_atuais = [Image.open(caminho) for caminho in caminhos_imagens]
            self.matrizes = [self.ler_bitmap(caminho) for caminho in self.caminhos_imagem]
            self.ponto_inicio, self.ponto_destino = self.encontrar_pontos()
            self.atualizar_exibicao_imagem(0)  # Exibe a primeira imagem
            print("Imagens carregadas:", self.imagens_atuais)
            print("Imagens redimensionadas:", self.imagens_redimensionadas)

    
    def subir_andar(self):
        if self.andar_atual < len(self.imagens_atuais) - 1:
            self.andar_atual += 1
            self.atualizar_exibicao_imagem(self.andar_atual)  # Passa o andar atual como argumento

    def descer_andar(self):
        if self.andar_atual > 0:
            self.andar_atual -= 1
            self.atualizar_exibicao_imagem(self.andar_atual)  # Passa o andar atual como argumento

    def atualizar_exibicao_imagem(self, andar):
        if 0 <= andar < len(self.imagens_atuais):
            self.andar_atual = andar
            imagem = self.imagens_atuais[andar]
            tamanho_novo = (imagem.width * self.fator_escala, imagem.height * self.fator_escala)
            imagem = imagem.resize(tamanho_novo, Image.NEAREST)
            foto = ImageTk.PhotoImage(imagem)
            self.label_imagem.config(image=foto)
            self.label_imagem.image = foto
            self.andar_label.config(text=f"Andar Atual: {self.andar_atual}")
            print("Atualizando imagem do andar:", andar)
            print("Tamanho da imagem redimensionada:", imagem.size)
            
    def ler_bitmap(self, caminho_arquivo):
        with Image.open(caminho_arquivo) as img:
            img = img.convert('RGB')
            largura, altura = img.size
            pixels = list(img.getdata())
            matriz_pixels = [pixels[i * largura:(i + 1) * largura] for i in range(altura)]
            return matriz_pixels  # Retornar apenas a matriz de pixels


    def encontrar_pontos(self):
        cor_inicio = (237, 28, 36)  # Nova cor de início
        cor_destino = (0, 255, 0)  # Verde
        ponto_inicio = None
        pontos_destino = []

        for andar, caminho_imagem in enumerate(self.caminhos_imagem):
            imagem = Image.open(caminho_imagem)
            imagem = imagem.convert('RGB')
            pixels = list(imagem.getdata())
            largura, altura = imagem.size
            matriz = [pixels[i * largura:(i + 1) * largura] for i in range(altura)]

            ponto_inicio_andar = None
            pontos_destino_andar = []

            for y in range(altura):
                for x in range(largura):
                    if matriz[y][x] == cor_inicio and andar == 0:
                        ponto_inicio_andar = (x, y, andar)
                        print(f"Ponto de início encontrado no andar {andar}: {ponto_inicio_andar}")
                    elif matriz[y][x] == cor_destino and andar == 2:
                        pontos_destino_andar.append((x, y, andar))
                        print(f"Ponto de destino encontrado no andar {andar}: {x, y, andar}")

            if ponto_inicio_andar:
                ponto_inicio = ponto_inicio_andar
            pontos_destino.extend(pontos_destino_andar)

        return ponto_inicio, pontos_destino


    def construir_grafo(self):
        altura = len(self.matrizes[0])
        largura = len(self.matrizes[0][0])
        num_andares = len(self.matrizes)
        grafo = {}

        for andar in range(num_andares):
            for y in range(altura):
                for x in range(largura):
                    if self.matrizes[andar][y][x] != (0, 0, 0):  # Se não é pixel preto
                        if (x, y, andar) not in grafo:
                            grafo[(x, y, andar)] = []
                        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < largura and 0 <= ny < altura and self.matrizes[andar][ny][nx] != (0, 0, 0):
                                # Atribuir peso com base na cor do pixel
                                cor_pixel = self.matrizes[andar][ny][nx]
                                if cor_pixel == (128, 128, 128):  # Cinza escuro
                                    peso = 2
                                elif cor_pixel == (196, 196, 196):  # Cinza claro
                                    peso = 1.5
                                else:  # Branco ou outro
                                    peso = 1
                                grafo[(x, y, andar)].append((nx, ny, andar, peso))
        
        # Conexões entre andares
        for andar in range(num_andares - 1):
            for y in range(altura):
                for x in range(largura):
                    # Verifica se o ponto está livre em ambos os andares
                    if self.matrizes[andar][y][x] != (0, 0, 0) and self.matrizes[andar + 1][y][x] != (0, 0, 0):
                        # Conexão para subir um andar
                        if (x, y, andar + 1) not in grafo:
                            grafo[(x, y, andar + 1)] = []
                        grafo[(x, y, andar)].append((x, y, andar + 1, 5))

                        # Conexão para descer um andar
                        if (x, y, andar) not in grafo:
                            grafo[(x, y, andar)] = []
                        grafo[(x, y, andar + 1)].append((x, y, andar, 5))

        return grafo

    def dijkstra_para_mais_proximo(self, grafo, inicio, destinos):
        dist = {v: float('inf') for v in grafo}
        dist[inicio] = 0
        pq = [(0, inicio)]
        anterior = {inicio: None}

        while pq:
            distancia_atual, vertice_atual = heapq.heappop(pq)

            if vertice_atual in destinos:
                # Reconstruir o caminho
                caminho = []
                atual = vertice_atual
                while atual is not None:
                    caminho.append(atual)
                    atual = anterior[atual]
                return caminho[::-1]

            for vizinho in grafo[vertice_atual]:
                nx, ny, nandar, peso = vizinho
                distancia = distancia_atual + peso
                if distancia < dist[(nx, ny, nandar)]:
                    dist[(nx, ny, nandar)] = distancia
                    anterior[(nx, ny, nandar)] = vertice_atual
                    heapq.heappush(pq, (distancia, (nx, ny, nandar)))

        return None  # Retorna None se nenhum caminho for encontrado

    def desenhar_caminho(self, caminho):
        imagens_atualizadas = []
        for andar in range(len(self.imagens_atuais)):
            img = self.imagens_atuais[andar].copy()
            img = img.convert('RGB')
            pixels = img.load()

            # Desenha o caminho nesse andar
            for indice_atual in range(len(caminho)):
                x, y, a = caminho[indice_atual]
                if a == andar:
                    cor = (0, 0, 255)  # Azul para o caminho
                    if indice_atual < len(caminho) - 1:
                        proximo_ponto = caminho[indice_atual + 1]
                        if proximo_ponto[2] != a:
                            cor = (255, 0, 0)  # Vermelho para transições de andar
                    pixels[x, y] = cor

            # Redimensiona e salva a imagem atualizada
            tamanho_novo = (img.width * self.fator_escala, img.height * self.fator_escala)
            img = img.resize(tamanho_novo, Image.NEAREST)
            imagens_atualizadas.append(img)

        # Atualiza a visualização na interface
        self.exibir_imagem_atualizada(imagens_atualizadas)

    def exibir_imagem_atualizada(self, imagens_atualizadas):
        # Exibe a primeira imagem do caminho
        if imagens_atualizadas:
            imagem_inicial = imagens_atualizadas[0]
            foto = ImageTk.PhotoImage(imagem_inicial)
            self.label_imagem.config(image=foto)
            self.label_imagem.image = foto
            # Salva as imagens atualizadas para navegação
            self.imagens_atuais = imagens_atualizadas


    def executar_busca_caminho(self):
        self.ponto_inicio, pontos_destino = self.encontrar_pontos()
        if not self.ponto_inicio or not pontos_destino:
            messagebox.showwarning("Aviso", "Pontos de início e/ou destino não identificados.")
            return

        grafo = self.construir_grafo()
        caminho_encontrado = self.dijkstra_para_mais_proximo(grafo, self.ponto_inicio, set(pontos_destino))
        if caminho_encontrado:
            self.desenhar_caminho(caminho_encontrado)
            self.caminho_label.config(text="Caminho mais curto encontrado.")
            self.btn_resetar.pack()
            self.btn_salvar.pack()
        else:
            messagebox.showerror("Erro", "Caminho não encontrado.")

    def resetar_imagem(self):
        # Resetar todas as imagens para o estado original
        self.imagens_atuais = [Image.open(caminho) for caminho in self.caminhos_imagem]
        self.atualizar_exibicao_imagem(self.andar_atual)

        # Resetar os pontos de início e destino
        self.ponto_inicio = None
        self.ponto_destino = None
        self.inicio_label.config(text="Ponto de início desmarcado.")
        self.destino_label.config(text="Ponto de destino desmarcado.")
        self.caminho_label.config(text="Caminho desmarcado.")
        self.btn_resetar.pack_forget()
        self.btn_salvar.pack_forget()


    def salvar_imagem(self):
        for i, imagem in enumerate(self.imagens_atuais):
            # Solicitar ao usuário um local e nome de arquivo para salvar cada imagem
            caminho_salvar = filedialog.asksaveasfilename(
                initialfile=f"andar_{i}.png",
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All Files", "*.*")]
            )
            if caminho_salvar:
                # Salvar a imagem no caminho especificado
                tamanho_original = (imagem.width // self.fator_escala, imagem.height // self.fator_escala)
                imagem_para_salvar = imagem.resize(tamanho_original)
                imagem_para_salvar.save(caminho_salvar)
        
        if len(self.imagens_atuais) > 0:
            messagebox.showinfo("Salvar Imagens", "Imagens salvas com sucesso.")

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
    app = Teste3D()
    app.root.mainloop()

if __name__ == "__main__":
    main()

