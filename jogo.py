import pygame
import random
import sys

# Inicialização
pygame.init()

# Tela e constantes
LARGURA = 400
ALTURA = 600
FPS = 60

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERDE = (0, 200, 0)

# Física
GRAVIDADE = 0.5
FORCA_PULO = -12

# Tela e fonte
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo da Raposa Infinita")
clock = pygame.time.Clock()
fonte = pygame.font.SysFont("Arial", 28)

# Jogador
class Jogador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.sprite = pygame.image.load("raposa.png").convert_alpha()
        self.image = pygame.transform.scale(self.sprite, (50, 50))  # Ajuste de tamanho
        self.rect = self.image.get_rect()
        self.resetar()

    def resetar(self):
        self.rect.center = (LARGURA // 2, ALTURA - 100)
        self.vel_y = 0
        self.score_altura = self.rect.y

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

# Plataforma
class Plataforma(pygame.sprite.Sprite):
    def __init__(self, x, y, largura=80, altura=10):
        super().__init__()
        self.image = pygame.Surface((largura, altura))
        self.image.fill(VERDE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Funções auxiliares
def gerar_plataforma_aleatoria(y_base):
    x = random.randint(50, LARGURA - 100)
    y = y_base - random.randint(80, 120)
    return Plataforma(x, y)

def tela_inicial():
    tela.fill(BRANCO)
    msg = fonte.render("Pressione qualquer tecla para começar", True, PRETO)
    tela.blit(msg, (LARGURA // 2 - msg.get_width() // 2, ALTURA // 2))
    pygame.display.flip()
    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                esperando = False

# Inicializações
jogador = Jogador()
grupo_sprites = pygame.sprite.Group()
grupo_plataformas = pygame.sprite.Group()
grupo_sprites.add(jogador)

plataformas_puladas = set()
pontuacao = 0
ultima_y = ALTURA - 40

# Plataformas iniciais
for _ in range(8):
    p = gerar_plataforma_aleatoria(ultima_y)
    ultima_y = p.rect.y
    grupo_plataformas.add(p)
    grupo_sprites.add(p)

tela_inicial()

# Loop principal
rodando = True
while rodando:
    clock.tick(FPS)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    vivo = jogador.update()
    if not vivo or jogador.rect.top > ALTURA:
        pontuacao = 0
        plataformas_puladas.clear()
        grupo_plataformas.empty()
        grupo_sprites.empty()
        grupo_sprites.add(jogador)
        jogador.resetar()
        ultima_y = ALTURA - 40
        for _ in range(8):
            p = gerar_plataforma_aleatoria(ultima_y)
            ultima_y = p.rect.y
            grupo_plataformas.add(p)
            grupo_sprites.add(p)
        tela_inicial()
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

    tela.fill(BRANCO)
    grupo_sprites.draw(tela)
    texto = fonte.render(f"Pontos: {pontuacao}", True, PRETO)
    tela.blit(texto, (10, 10))
    pygame.display.flip()

pygame.quit()
sys.exit()





