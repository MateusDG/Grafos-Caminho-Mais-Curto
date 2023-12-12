import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps
import heapq

# Variáveis Globais
ponto_inicio = None
ponto_destino = None
imagem_atual = None
caminho_imagem = None
fator_escala = 20  # Define o fator de escala para redimensionamento

def ler_bitmap_e_encontrar_pontos(caminho_arquivo):
    cor_inicio = (255, 0, 0)  # Vermelho
    cor_destino = (0, 255, 0)  # Verde

    ponto_inicio = None
    ponto_destino = None

    with Image.open(caminho_arquivo) as img:
        img = img.convert('RGB')
        largura, altura = img.size
        pixels = list(img.getdata())
        
        matriz = [pixels[i * largura:(i + 1) * largura] for i in range(altura)]

        for y in range(altura):
            for x in range(largura):
                if matriz[y][x] == cor_inicio:
                    ponto_inicio = (x, y)
                elif matriz[y][x] == cor_destino:
                    ponto_destino = (x, y)

    return matriz, ponto_inicio, ponto_destino


def construir_grafo(matriz):
    altura = len(matriz)
    largura = len(matriz[0])
    grafo = {}
    for y in range(altura):
        for x in range(largura):
            if matriz[y][x] != (0, 0, 0):  # Ignora pixels pretos
                grafo[(x, y)] = []
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Vizinhos
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < largura and 0 <= ny < altura and matriz[ny][nx] != (0, 0, 0):
                        grafo[(x, y)].append((nx, ny))
    return grafo

def dijkstra(grafo, inicio, destino):
    fila_prioridade = [(0, inicio)]
    distancias = {inicio: 0}
    caminho = {inicio: None}

    while fila_prioridade:
        dist_atual, atual = heapq.heappop(fila_prioridade)

        if atual == destino:
            break

        for vizinho in grafo[atual]:
            dist_vizinho = dist_atual + 1  # Todos os movimentos têm peso 1
            if vizinho not in distancias or dist_vizinho < distancias[vizinho]:
                distancias[vizinho] = dist_vizinho
                heapq.heappush(fila_prioridade, (dist_vizinho, vizinho))
                caminho[vizinho] = atual

    if destino not in caminho:
        return None

    percurso = []
    while destino is not None:
        percurso.append(destino)
        destino = caminho[destino]
    return percurso[::-1]

def escolher_imagem():
    global imagem_atual, caminho_imagem, ponto_inicio, ponto_destino
    caminho_imagem = filedialog.askopenfilename()
    if caminho_imagem:
        imagem = Image.open(caminho_imagem)
        # Redimensionar a imagem - ajuste o fator de escala conforme necessário
        tamanho_novo = (imagem.width * fator_escala, imagem.height * fator_escala)
        imagem = imagem.resize(tamanho_novo, Image.NEAREST)

        foto = ImageTk.PhotoImage(imagem)

        label_imagem.config(image=foto)
        label_imagem.image = foto  # Mantém a referência
        imagem_atual = imagem
        ponto_inicio = None
        ponto_destino = None

def on_click(event):
    global ponto_inicio, ponto_destino
    x, y = event.x // fator_escala, event.y // fator_escala  # Ajusta as coordenadas de acordo com o redimensionamento

    # Lógica para desmarcar ou marcar pontos
    if ponto_inicio == (x, y):
        ponto_inicio = None
        print("Ponto de início desmarcado.")
    elif ponto_destino == (x, y):
        ponto_destino = None
        print("Ponto de destino desmarcado.")
    elif not ponto_inicio:
        ponto_inicio = (x, y)
        print(f"Ponto de início definido: {ponto_inicio}")
    elif not ponto_destino:
        ponto_destino = (x, y)
        print(f"Ponto de destino definido: {ponto_destino}")    
    else:
        messagebox.showinfo("Informação", "Ponto de início e destino já definidos!")

def desenhar_caminho(caminho, caminho_arquivo, caminho_saida):

    with Image.open(caminho_arquivo) as img:
        img = img.convert('RGB')
        pixels = img.load()

        # Desenha o caminho na escala original
        for x, y in caminho:
            pixels[x, y] = (0, 0, 255)  # Azul para o caminho

        # Redimensiona a imagem para a escala de visualização
        tamanho_novo = (img.width * fator_escala, img.height * fator_escala)
        img = img.resize(tamanho_novo, Image.NEAREST)

        img.save(caminho_saida)

def executar_busca_caminho():
    global ponto_inicio, ponto_destino, caminho_imagem

    if ponto_inicio and ponto_destino:
        matriz, _, _ = ler_bitmap_e_encontrar_pontos(caminho_imagem)
        grafo = construir_grafo(matriz)
        caminho_encontrado = dijkstra(grafo, ponto_inicio, ponto_destino)

        if caminho_encontrado:
            caminho_salvar = "C:\\Users\\mateu\\Desktop\\UFOP\\3º período\\AEDS 3\\Trabalho 1\\Datasets\\toy-tk.bmp"
            desenhar_caminho(caminho_encontrado, caminho_imagem, caminho_salvar)

            imagem_atualizada = Image.open(caminho_salvar)
            foto_atualizada = ImageTk.PhotoImage(imagem_atualizada)
            label_imagem.config(image=foto_atualizada)
            label_imagem.image = foto_atualizada
        else:
            messagebox.showerror("Erro", "Caminho não encontrado.")
    else:
        messagebox.showwarning("Aviso", "Defina os pontos de início e destino primeiro.")

def resetar_imagem():
    global ponto_inicio, ponto_destino
    ponto_inicio = None
    ponto_destino = None
    if caminho_imagem:
        escolher_imagem()  # Recarrega a imagem original

def salvar_imagem():
    if imagem_atual:
        caminho_salvar = filedialog.asksaveasfilename(defaultextension=".bmp")
        if caminho_salvar:
            imagem_atual.save(caminho_salvar)
            messagebox.showinfo("Salvar Imagem", "Imagem salva com sucesso.")

root = tk.Tk()
root.title("Seletor de Ponto de Imagem")

btn_carregar = tk.Button(root, text="Carregar Imagem", command=escolher_imagem)
btn_carregar.pack()

btn_buscar_caminho = tk.Button(root, text="Encontrar Caminho", command=executar_busca_caminho)
btn_buscar_caminho.pack()

btn_resetar = tk.Button(root, text="Resetar Imagem", command=resetar_imagem)
btn_resetar.pack()

btn_salvar = tk.Button(root, text="Salvar Imagem", command=salvar_imagem)
btn_salvar.pack()

label_imagem = tk.Label(root)
label_imagem.pack()
label_imagem.bind("<Button-1>", on_click)

root.mainloop()