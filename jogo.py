import pygame
import sys
import os
import json
import random

pygame.init()

# Constantes
LARGURA, ALTURA = 400, 800
FPS = 60
COR_BG = (243, 233, 215)
COR_HOVER = (200, 180, 150)
COR_TEXTO = (0, 0, 0)
GRAVIDADE = 0.2
FORCA_PULO = -8
VELOCIDADE_MOVIMENTO = 6
ESPACO_PLATAFORMAS = 100
NUM_PLATAFORMAS = 8
VELOCIDADE_METEORO = 2
PONTUACAO_METEOROS = 100
INTERVALO_METEOROS = 5000

# Inicializa tela
screen = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Escape bombarilo GVzilo")
clock = pygame.time.Clock()
fonte = pygame.font.SysFont("Arial", 24)
fonte_grande = pygame.font.SysFont("Arial", 36)

background = pygame.image.load("1.png").convert()
background = pygame.transform.scale(background, (LARGURA, ALTURA))

platimage = pygame.image.load("plataforma_1.png").convert_alpha()
dados_path = "dados_jogador.json"

def carregar_dados():
    if os.path.exists(dados_path):
        with open(dados_path, 'r') as f:
            return json.load(f)
    return {}

def salvar_dados(dados):
    with open(dados_path, 'w') as f:
        json.dump(dados, f)

texto_cache = {}

def renderizar_texto_cached(texto, fonte, cor):
    chave = (texto, fonte, cor)
    if chave not in texto_cache:
        texto_cache[chave] = fonte.render(texto, True, cor)
    return texto_cache[chave]

def desenhar_texto(texto, x, y, hover=False):
    cor = COR_HOVER if hover else COR_TEXTO
    texto_surface = fonte.render(texto, True, cor)
    rect = texto_surface.get_rect(center=(x + 50, y + 15))  
    screen.blit(texto_surface, rect)

    if hover:
        pygame.draw.rect(screen, (255, 255, 255, 50), rect.inflate(20, 10), 2, border_radius=5)
    
    return rect

def obter_nickname():
    nickname = ""
    digitando = True
    while digitando:
        if background:
            screen.blit(background, (0, 0))
        else:
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
        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill(COR_BG)
        mouse_pos = pygame.mouse.get_pos()
        
        centro_x = LARGURA // 2
        
        jogar_rect = desenhar_texto("JOGAR", centro_x - 50, 200, 
                                  centro_x - 50 <= mouse_pos[0] <= centro_x + 50 and 200 <= mouse_pos[1] <= 240)
        skins_rect = desenhar_texto("HIGHSCORES", centro_x - 50, 270,
                                  centro_x - 50 <= mouse_pos[0] <= centro_x + 50 and 270 <= mouse_pos[1] <= 310)
        reset_rect = desenhar_texto("RESETAR SCORES", centro_x - 50, 340,
                                  centro_x - 50 <= mouse_pos[0] <= centro_x + 50 and 340 <= mouse_pos[1] <= 380)
        sair_rect = desenhar_texto("SAIR", centro_x - 50, 410,
                                  centro_x - 50 <= mouse_pos[0] <= centro_x + 50 and 410 <= mouse_pos[1] <= 450)
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
                elif reset_rect.collidepoint(mouse_pos):
                    if os.path.exists(dados_path):
                        os.remove(dados_path)
                    dados = {}
                    screen.fill(COR_BG)
                    msg = fonte.render("Scores resetados com sucesso!", True, COR_TEXTO)
                    screen.blit(msg, (LARGURA//2 - msg.get_width()//2, ALTURA//2))
                    pygame.display.flip()
                    pygame.time.wait(2000)
                elif sair_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

def atualizar_pontuacao(nickname, dados, nova_pontuacao):
    if nova_pontuacao > dados.get(nickname, 0):
        dados[nickname] = nova_pontuacao
        salvar_dados(dados)

class Jogador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.imagem_pulando_direita = pygame.image.load("Jump.png").convert_alpha()
        self.imagem_pulando_direita = pygame.transform.scale(self.imagem_pulando_direita, (50, 50))
        self.imagem_pulando_esquerda = pygame.transform.flip(self.imagem_pulando_direita, True, False)
        
        self.imagem_aterrissando_direita = pygame.image.load("Fall.png").convert_alpha()
        self.imagem_aterrissando_direita = pygame.transform.scale(self.imagem_aterrissando_direita, (50, 50))
        self.imagem_aterrissando_esquerda = pygame.transform.flip(self.imagem_aterrissando_direita, True, False)
        
        self.olhando_direita = True
        self.image = self.imagem_aterrissando_direita
        self.rect = self.image.get_rect()
        
        self.collision_rect = pygame.Rect(0, 0, 30, 40)
        
        self.vel_y = 0
        self.vel_x = 0
        self.no_chao = False
        self.resetar()

    def resetar(self):
        self.rect.center = (LARGURA // 2, ALTURA - 50)
        self.collision_rect.center = self.rect.center
        self.vel_y = 0
        self.vel_x = 0
        self.no_chao = False
        self.olhando_direita = True
        self.image = self.imagem_aterrissando_direita

    def update(self):
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT]:
            self.vel_x = max(self.vel_x - 1, -VELOCIDADE_MOVIMENTO)
            self.olhando_direita = False
        elif teclas[pygame.K_RIGHT]:
            self.vel_x = min(self.vel_x + 1, VELOCIDADE_MOVIMENTO)
            self.olhando_direita = True
        else:
            self.vel_x = self.vel_x * 0.9

        if teclas[pygame.K_SPACE] and self.no_chao:
            self.pular()

        self.rect.x += self.vel_x
        self.vel_y += GRAVIDADE
        self.rect.y += self.vel_y
        
        self.collision_rect.center = self.rect.center

        if self.vel_y < 0:  
            self.image = self.imagem_pulando_direita if self.olhando_direita else self.imagem_pulando_esquerda
        else:  
            self.image = self.imagem_aterrissando_direita if self.olhando_direita else self.imagem_aterrissando_esquerda

        if self.rect.left < 0:
            self.rect.right = LARGURA
            self.collision_rect.center = self.rect.center
        elif self.rect.right > LARGURA:
            self.rect.left = 0
            self.collision_rect.center = self.rect.center

        return self.rect.top <= ALTURA

    def pular(self):
        self.vel_y = FORCA_PULO
        self.no_chao = False
        self.image = self.imagem_pulando_direita if self.olhando_direita else self.imagem_pulando_esquerda

class Plataforma(pygame.sprite.Sprite):
    def __init__(self, x, y, tipo="normal", largura=None):
        super().__init__()
        self.tipo = tipo

        if largura is None:
            if tipo == "normal":
                tamanho = (80, 20)  
            elif tipo == "pequena":
                tamanho = (60, 20) 
            else:  
                tamanho = (120, 20)  
        else:
            tamanho = (largura, 20) 
         
        self.image = platimage
        self.image = pygame.transform.scale(self.image, tamanho)
            
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

def gerar_plataforma_aleatoria(y_base):
    x = random.randint(50, LARGURA - 100)
    y = y_base - random.randint(50, ESPACO_PLATAFORMAS)  
    tipo = random.choices(["normal", "pequena", "grande"], weights=[0.7, 0.2, 0.1])[0]
    return Plataforma(x, y, tipo)

def desenhar_texto_com_outline(superficie, texto, fonte, cor_texto, cor_outline, x, y, espessura=4):
    chave_texto = (texto, fonte, cor_texto)
    chave_outline = (texto, fonte, cor_outline)
    
    if chave_texto not in texto_cache:
        texto_cache[chave_texto] = fonte.render(texto, True, cor_texto)
    if chave_outline not in texto_cache:
        texto_cache[chave_outline] = fonte.render(texto, True, cor_outline)
    
    texto_surface = texto_cache[chave_texto]
    texto_outline = texto_cache[chave_outline]
    texto_rect = texto_surface.get_rect(center=(x, y))
    
    for dx in range(-espessura, espessura + 1, 2):
        for dy in range(-espessura, espessura + 1, 2):
            outline_rect = texto_rect.copy()
            outline_rect.x += dx
            outline_rect.y += dy
            superficie.blit(texto_outline, outline_rect)
    
    superficie.blit(texto_surface, texto_rect)

def mostrar_game_over(pontuacao, melhor_pontuacao):
    if 'game_over_img' not in texto_cache:
        imagem_game_over = pygame.image.load("bombaraposa.png").convert_alpha()
        texto_cache['game_over_img'] = pygame.transform.scale(imagem_game_over, (LARGURA, ALTURA))
    imagem_game_over = texto_cache['game_over_img']

    fade = pygame.Surface((LARGURA, ALTURA))
    fade.fill((0, 0, 0))
    fade.set_alpha(128)

    game_over = True
    texto_reiniciar = renderizar_texto_cached("Pressione SPACE para recomeçar", fonte, (255, 255, 255))
    texto_pontuacao = renderizar_texto_cached(f"Pontuação: {pontuacao}", fonte, (255, 255, 255))
    texto_melhor = renderizar_texto_cached(f"Melhor: {melhor_pontuacao}", fonte, (255, 255, 255))

    while game_over:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    return True

        screen.fill((0, 0, 0))
        
        if imagem_game_over:
            screen.blit(imagem_game_over, (0, 0))
        
        screen.blit(fade, (0, 0))
        
        desenhar_texto_com_outline(screen, "GAME OVER", fonte_grande, (255, 0, 0), (0, 0, 0), LARGURA//2, ALTURA//2 - 80, espessura=4)
        
        screen.blit(texto_pontuacao, (LARGURA//2 - texto_pontuacao.get_width()//2, ALTURA//2))
        screen.blit(texto_melhor, (LARGURA//2 - texto_melhor.get_width()//2, ALTURA//2 + 30))
        screen.blit(texto_reiniciar, (LARGURA//2 - texto_reiniciar.get_width()//2, ALTURA//2 + 80))
        
        pygame.display.flip()
        clock.tick(60)  

def mostrar_vitoria(pontuacao):
    if 'vitoria_img' not in texto_cache:
        imagem_vitoria = pygame.image.load("vitoria.png").convert_alpha()
        texto_cache['vitoria_img'] = pygame.transform.scale(imagem_vitoria, (LARGURA, ALTURA))
    imagem_vitoria = texto_cache['vitoria_img']

    fade = pygame.Surface((LARGURA, ALTURA))
    fade.fill((0, 0, 0))
    fade.set_alpha(128)

    vitoria = True
    texto_reiniciar = renderizar_texto_cached("Pressione SPACE para recomeçar", fonte, (255, 255, 255))
    texto_pontuacao = renderizar_texto_cached(f"Pontuação Final: {pontuacao}", fonte, (255, 255, 255))

    while vitoria:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    return True

        screen.fill((0, 0, 0))
        
        if imagem_vitoria:
            screen.blit(imagem_vitoria, (0, 0))
        
        screen.blit(fade, (0, 0))
        
        desenhar_texto_com_outline(screen, "Você salvou o INSPER!", fonte_grande, (0, 255, 0), (0, 0, 0), LARGURA//2, ALTURA//2 - 80, espessura=4)
        
        screen.blit(texto_pontuacao, (LARGURA//2 - texto_pontuacao.get_width()//2, ALTURA//2))
        screen.blit(texto_reiniciar, (LARGURA//2 - texto_reiniciar.get_width()//2, ALTURA//2 + 80))
        
        pygame.display.flip()
        clock.tick(60)  

class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
    
        self.imagem_original = pygame.image.load("bombardilo crocodilo.png").convert_alpha()
        self.imagem_original = pygame.transform.scale(self.imagem_original, (80, 80))
        self.imagem_direita = self.imagem_original
        self.imagem_esquerda = pygame.transform.flip(self.imagem_original, True, False)
        
        self.olhando_direita = True
        self.image = self.imagem_direita
        self.rect = self.image.get_rect()
        self.rect.centerx = LARGURA // 2
        self.rect.top = 20  
        self.alvo_x = self.rect.centerx
        self.velocidade = 3
        self.tempo_espera = 0
        self.estado = "movendo"  
        
        self.tempo_espera_inicial = 2000 
        self.tempo_espera_minimo = 500    
        self.pontuacao_maxima = 1000      
        
    def calcular_tempo_espera(self, pontuacao):
        if pontuacao <= PONTUACAO_METEOROS:
            return self.tempo_espera_inicial
        elif pontuacao >= self.pontuacao_maxima:
            return self.tempo_espera_minimo
        else:
            progresso = (pontuacao - PONTUACAO_METEOROS) / (self.pontuacao_maxima - PONTUACAO_METEOROS)
            return self.tempo_espera_inicial - (self.tempo_espera_inicial - self.tempo_espera_minimo) * progresso
        
    def update(self, pontuacao):
        tempo_atual = pygame.time.get_ticks()
        
        if self.estado == "movendo":
            if abs(self.rect.centerx - self.alvo_x) < self.velocidade:
                self.rect.centerx = self.alvo_x
                self.estado = "esperando"
                self.tempo_espera = tempo_atual
            elif self.rect.centerx < self.alvo_x:
                self.rect.x += self.velocidade
                if not self.olhando_direita:
                    self.olhando_direita = True
                    self.image = self.imagem_direita
            else:
                self.rect.x -= self.velocidade
                if self.olhando_direita:
                    self.olhando_direita = False
                    self.image = self.imagem_esquerda
                
        elif self.estado == "esperando":
            tempo_espera_atual = self.calcular_tempo_espera(pontuacao)
            if tempo_atual - self.tempo_espera >= tempo_espera_atual:
                self.estado = "atirando"
                
        elif self.estado == "atirando":
            self.estado = "movendo"
            self.alvo_x = random.randint(80, LARGURA - 80)
            if self.alvo_x > self.rect.centerx and not self.olhando_direita:
                self.olhando_direita = True
                self.image = self.imagem_direita
            elif self.alvo_x < self.rect.centerx and self.olhando_direita:
                self.olhando_direita = False
                self.image = self.imagem_esquerda
            return True  
            
        return False
        
    def resetar(self):
        self.rect.centerx = LARGURA // 2
        self.alvo_x = self.rect.centerx
        self.estado = "movendo"
        self.tempo_espera = 0
        self.olhando_direita = True
        self.image = self.imagem_direita

class Meteoro(pygame.sprite.Sprite):
    def __init__(self, x=None):
        super().__init__()
        self.image = pygame.image.load("bomba.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (30, 45))
        
        self.rect = self.image.get_rect()
        
        if x is None:
            self.rect.x = random.randint(0, LARGURA - self.rect.width)
        else:
            self.rect.centerx = x
        self.rect.bottom = 0
        
        self.collision_rect = pygame.Rect(0, 0, self.rect.width - 10, self.rect.height - 15)
        self.collision_rect.center = self.rect.center
        
    def update(self):
        self.rect.y += VELOCIDADE_METEORO
        self.collision_rect.center = self.rect.center
        if self.rect.top > ALTURA:
            self.kill()  

nickname, dados_salvos = menu()

jogador = Jogador()
grupo_sprites = pygame.sprite.Group()
grupo_plataformas = pygame.sprite.Group()
grupo_meteoros = pygame.sprite.Group()  
plataformas_puladas = set()
pontuacao = 0
melhor_pontuacao = dados_salvos.get(nickname, 0)
ultima_y = ALTURA - 40
tempo_ultimo_meteoro = 0

boss = Boss()
grupo_sprites.add(boss)

def iniciar_jogo():
    global ultima_y
    grupo_sprites.empty()
    grupo_plataformas.empty()
    grupo_meteoros.empty()

    jogador.resetar()
    grupo_sprites.add(jogador)
    
    boss.resetar()
    grupo_sprites.add(boss)
    
    plataforma_inicial = Plataforma(LARGURA//2 - 100, ALTURA - 50, "normal", largura=200)
    grupo_plataformas.add(plataforma_inicial)
    grupo_sprites.add(plataforma_inicial)
    ultima_y = plataforma_inicial.rect.y
    
    for _ in range(NUM_PLATAFORMAS):
        p = gerar_plataforma_aleatoria(ultima_y)
        ultima_y = p.rect.y
        grupo_plataformas.add(p)
        grupo_sprites.add(p)

iniciar_jogo()

rodando = True
while rodando:
    clock.tick(60)  
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    vivo = jogador.update()
    
    if pontuacao >= PONTUACAO_METEOROS:
        if boss.update(pontuacao):  
            meteoro = Meteoro(boss.rect.centerx)  
            grupo_meteoros.add(meteoro)
            grupo_sprites.add(meteoro)
            
        grupo_meteoros.update()
        
        for meteoro in grupo_meteoros:
            if meteoro.collision_rect.colliderect(jogador.collision_rect):
                vivo = False
                break

    if pontuacao >= 1500:
        atualizar_pontuacao(nickname, dados_salvos, pontuacao)
        if not mostrar_vitoria(pontuacao):
            rodando = False
            break
            
        jogador.resetar()
        pontuacao = 0
        plataformas_puladas.clear()
        melhor_pontuacao = dados_salvos.get(nickname, 0)
        iniciar_jogo()
        tempo_ultimo_meteoro = pygame.time.get_ticks()
        continue

    if not vivo or jogador.rect.top > ALTURA:
        atualizar_pontuacao(nickname, dados_salvos, pontuacao)
        if not mostrar_game_over(pontuacao, melhor_pontuacao):
            rodando = False
            break
            
        jogador.resetar()
        pontuacao = 0
        plataformas_puladas.clear()
        melhor_pontuacao = dados_salvos.get(nickname, 0)
        iniciar_jogo()
        tempo_ultimo_meteoro = pygame.time.get_ticks()  
        continue

    jogador.no_chao = False
    for plataforma in grupo_plataformas:
        if jogador.collision_rect.colliderect(plataforma.rect) and jogador.vel_y > 0:
            jogador.rect.bottom = plataforma.rect.top + (jogador.rect.height - jogador.collision_rect.height) // 2
            jogador.no_chao = True
            jogador.vel_y = 0
            
            if plataforma.tipo == "pequena":
                jogador.pular()
            elif plataforma.tipo == "grande":
                jogador.vel_y = FORCA_PULO * 1.5
            else:
                jogador.pular()
            
            if plataforma not in plataformas_puladas:
                plataformas_puladas.add(plataforma)
                pontuacao += 10  

    if jogador.rect.top <= ALTURA // 3:
        deslocamento = ALTURA // 3 - jogador.rect.top
        jogador.rect.top = ALTURA // 3
        for plataforma in grupo_plataformas:
            plataforma.rect.y += deslocamento
        for meteoro in grupo_meteoros:  
            meteoro.rect.y += deslocamento
        ultima_y += deslocamento

    for plataforma in grupo_plataformas.copy():
        if plataforma.rect.top > ALTURA:
            grupo_plataformas.remove(plataforma)
            grupo_sprites.remove(plataforma)
            nova_plat = gerar_plataforma_aleatoria(ultima_y)
            ultima_y = nova_plat.rect.y
            grupo_plataformas.add(nova_plat)
            grupo_sprites.add(nova_plat)

    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill(COR_BG)
    grupo_sprites.draw(screen)
    
    texto_pontos = fonte.render(f"Pontos: {pontuacao}", True, COR_TEXTO)
    texto_melhor = fonte.render(f"Melhor: {melhor_pontuacao}", True, COR_TEXTO)
    screen.blit(texto_pontos, (10, 10))
    screen.blit(texto_melhor, (10, 40))
    
    if pontuacao >= PONTUACAO_METEOROS:
        texto_aviso = fonte.render("CUIDADO! Bombas da GV!", True, (200, 0, 0))
        screen.blit(texto_aviso, (LARGURA - texto_aviso.get_width() - 10, 10))  
    pygame.display.flip()

pygame.quit()
sys.exit()