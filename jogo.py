import pygame
import sys
import os
import json
import random

pygame.init()

# Constantes
LARGURA, ALTURA = 800, 600
FPS = 60
COR_BG = (243, 233, 215)
COR_HOVER = (200, 180, 150)
COR_TEXTO = (0, 0, 0)
GRAVIDADE = 0.5
FORCA_PULO = -12

# Inicializa tela
screen = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo da Raposa")
clock = pygame.time.Clock()
fonte = pygame.font.SysFont("Arial", 28)

# Caminho para salvar dados
dados_path = "dados_jogador.json"

# Carrega dados se existirem
def carregar_dados():
    if os.path.exists(dados_path):
        with open(dados_path, 'r') as f:
            return json.load(f)
    return {}

def salvar_dados(dados):
    with open(dados_path, 'w') as f:
        json.dump(dados, f)

def desenhar_texto(texto, x, y, hover=False):
    cor = COR_HOVER if hover else COR_TEXTO
    texto_surface = fonte.render(texto, True, cor)
    screen.blit(texto_surface, (x, y))
    return texto_surface.get_rect(topleft=(x, y))

def obter_nickname():
    nickname = ""
    digitando = True
    while digitando:
        screen.fill(COR_BG)
        texto = fonte.render("Digite seu nome e pressione ENTER:", True, COR_TEXTO)
        screen.blit(texto, (LARGURA // 2 - texto.get_width() // 2, 200))

        nickname_surface = fonte.render(nickname + "|", True, COR_TEXTO)
        screen.blit(nickname_surface, (LARGURA // 2 - nickname_surface.get_width() // 2, 300))

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    digitando = False
                elif evento.key == pygame.K_BACKSPACE:
                    nickname = nickname[:-1]
                else:
                    nickname += evento.unicode
    return nickname

def mostrar_ranking(dados):
    screen.fill(COR_BG)
    ranking = sorted(dados.items(), key=lambda x: x[1], reverse=True)
    titulo = fonte.render("Ranking dos Jogadores:", True, COR_TEXTO)
    screen.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 50))
    for i, (nome, pontos) in enumerate(ranking[:5]):
        texto = fonte.render(f"{i+1}º {nome} - {pontos} pts", True, COR_TEXTO)
        screen.blit(texto, (LARGURA // 2 - texto.get_width() // 2, 100 + i*40))
    pygame.display.flip()
    pygame.time.wait(3000)

def menu():
    dados = carregar_dados()
    while True:
        screen.fill(COR_BG)
        mouse_pos = pygame.mouse.get_pos()
        jogar_rect = desenhar_texto("JOGAR", 350, 200, 350 <= mouse_pos[0] <= 450 and 200 <= mouse_pos[1] <= 240)
        skins_rect = desenhar_texto("SKINS", 350, 270, 350 <= mouse_pos[0] <= 450 and 270 <= mouse_pos[1] <= 310)
        sair_rect = desenhar_texto("SAIR", 350, 340, 350 <= mouse_pos[0] <= 450 and 340 <= mouse_pos[1] <= 380)
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if jogar_rect.collidepoint(mouse_pos):
                    nickname = obter_nickname()
                    dados = carregar_dados()
                    if nickname not in dados:
                        dados[nickname] = 0
                    salvar_dados(dados)
                    return nickname, dados
                elif skins_rect.collidepoint(mouse_pos):
                    mostrar_ranking(carregar_dados())
                elif sair_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

def atualizar_pontuacao(nickname, dados, nova_pontuacao):
    if nova_pontuacao > dados.get(nickname, 0):
        dados[nickname] = nova_pontuacao
        salvar_dados(dados)

# Classes do jogo
class Jogador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("raposa_idle.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.vel_y = 0
        self.resetar()

    def resetar(self):
        self.rect.center = (LARGURA // 2, ALTURA - 100)
        self.vel_y = 0

    def update(self):
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT]:
            self.rect.x -= 5
        if teclas[pygame.K_RIGHT]:
            self.rect.x += 5
        self.vel_y += GRAVIDADE
        self.rect.y += self.vel_y
        if self.rect.left < 0:
            self.rect.right = LARGURA
        elif self.rect.right > LARGURA:
            self.rect.left = 0
        return self.rect.top <= ALTURA

    def pular(self):
        self.vel_y = FORCA_PULO

class Plataforma(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((80, 10))
        self.image.fill((0, 200, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

def gerar_plataforma_aleatoria(y_base):
    x = random.randint(50, LARGURA - 100)
    y = y_base - random.randint(80, 120)
    return Plataforma(x, y)

# Menu inicial
nickname, dados_salvos = menu()

# Jogo principal
jogador = Jogador()
grupo_sprites = pygame.sprite.Group()
grupo_plataformas = pygame.sprite.Group()
grupo_sprites.add(jogador)
plataformas_puladas = set()
pontuacao = 0
ultima_y = ALTURA - 40

for _ in range(8):
    p = gerar_plataforma_aleatoria(ultima_y)
    ultima_y = p.rect.y
    grupo_plataformas.add(p)
    grupo_sprites.add(p)

rodando = True
while rodando:
    clock.tick(FPS)
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    vivo = jogador.update()
    if not vivo or jogador.rect.top > ALTURA:
        atualizar_pontuacao(nickname, dados_salvos, pontuacao)
        mostrar_ranking(dados_salvos)
        nickname, dados_salvos = menu()
        jogador.resetar()
        grupo_plataformas.empty()
        grupo_sprites.empty()
        grupo_sprites.add(jogador)
        pontuacao = 0
        plataformas_puladas.clear()
        ultima_y = ALTURA - 40
        for _ in range(8):
            p = gerar_plataforma_aleatoria(ultima_y)
            ultima_y = p.rect.y
            grupo_plataformas.add(p)
            grupo_sprites.add(p)
        continue

    jogador.no_chao = False
    for plataforma in grupo_plataformas:
        if jogador.rect.colliderect(plataforma.rect) and jogador.vel_y > 0:
            jogador.rect.bottom = plataforma.rect.top
            jogador.pular()
            jogador.no_chao = True
            if plataforma not in plataformas_puladas:
                plataformas_puladas.add(plataforma)
                pontuacao += 10

    if jogador.rect.top <= ALTURA // 3:
        deslocamento = ALTURA // 3 - jogador.rect.top
        jogador.rect.top = ALTURA // 3
        for plataforma in grupo_plataformas:
            plataforma.rect.y += deslocamento
        ultima_y += deslocamento

    for plataforma in grupo_plataformas.copy():
        if plataforma.rect.top > ALTURA:
            grupo_plataformas.remove(plataforma)
            grupo_sprites.remove(plataforma)
            nova_plat = gerar_plataforma_aleatoria(ultima_y)
            ultima_y = nova_plat.rect.y
            grupo_plataformas.add(nova_plat)
            grupo_sprites.add(nova_plat)

    screen.fill(COR_BG)
    grupo_sprites.draw(screen)
    texto = fonte.render(f"Pontos: {pontuacao}", True, COR_TEXTO)
    screen.blit(texto, (10, 10))
    pygame.display.flip()

pygame.quit()
sys.exit()