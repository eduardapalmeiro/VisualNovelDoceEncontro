import pygame
import math
import random
from dataclasses import dataclass, field

# ─── Inicialização ─────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1024, 768
FPS = 60
pygame.display.set_caption("Doce Encontro")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# ─── Cores ─────────────────────────────────────────────────────────────────────
ROSA_ESCURO  = (180,  60, 100)
ROSA         = (230, 100, 140)
ROSA_CLARO   = (255, 182, 210)
CREME        = (255, 245, 235)
DOURADO      = (220, 170,  80)
BRANCO       = (255, 255, 255)
PRETO        = (  0,   0,   0)
CINZA_MEDIO  = ( 80,  60,  70)
LILAS        = (200, 160, 220)

# ─── Fontes ────────────────────────────────────────────────────────────────────
def carregar_fontes():
    base = pygame.font.get_default_font()
    configs = {
        "titulo":    ("Georgia", 52, True, False),
        "subtitulo": ("Georgia", 28, False, True),
        "nome":      ("Georgia", 26, True, False),
        "texto":     ("Palatino Linotype", 22, False, False),
        "escolha":   ("Georgia", 20, False, False),
        "ui":        ("Georgia", 18, False, False),
        "coracao":   ("Segoe UI Symbol", 22, False, False),
    }
    fontes = {}
    for chave, (nome, tam, bold, italic) in configs.items():
        try:
            fontes[chave] = pygame.font.SysFont(nome, tam, bold=bold, italic=italic)
        except:
            fontes[chave] = pygame.font.Font(base, tam)
    return fontes

FONTES = carregar_fontes()

# ─── Assets ────────────────────────────────────────────────────────────────────
ASSETS_CAMINHOS = {
    "salaaula":  "./src/fundos/Classroom_Day.png",
    "cafeteria": "./src/fundos/Cafeteria_Day.png",
    "patio":     "./src/fundos/School_Hallway_Day.png",
    **{f"{p}{e}": f"./src/personagens/{p}{e}.png" 
       for p in ["talita", "victoria", "victor", "talisson", "fabiano", "catarina"] 
       for e in ["normal", "feliz", "triste"]}
}

def _carregar_imagens():
    cache = {}
    for chave, caminho in ASSETS_CAMINHOS.items():
        try:
            cache[chave] = pygame.image.load(caminho).convert_alpha()
        except:
            cache[chave] = None
    return cache

IMGS = _carregar_imagens()

# ─── Utilitários ───────────────────────────────────────────────────────────────
def desenhar_retangulo_arredondado(surf, cor, rect, raio=20, alpha=255):
    shape = pygame.Surface(rect[2:], pygame.SRCALPHA)
    pygame.draw.rect(shape, (*cor, alpha), (0, 0, *rect[2:]), border_radius=raio)
    surf.blit(shape, rect[:2])

def quebrar_texto(texto, fonte, largura_max):
    linhas, linha_atual = [], ""
    for palavra in texto.split():
        teste = f"{linha_atual} {palavra}".strip()
        if fonte.size(teste)[0] <= largura_max:
            linha_atual = teste
        else:
            if linha_atual: linhas.append(linha_atual)
            linha_atual = palavra
    if linha_atual: linhas.append(linha_atual)
    return linhas

def gradiente_vertical(surf, cor1, cor2, rect):
    for i in range(rect[3]):
        t = i / max(rect[3] - 1, 1)
        cor = [int(c1 + (c2 - c1) * t) for c1, c2 in zip(cor1, cor2)]
        pygame.draw.line(surf, cor, (rect[0], rect[1]+i), (rect[0]+rect[2]-1, rect[1]+i))

# ─── Partículas ────────────────────────────────────────────────────────────────
class Particula:
    def __init__(self): self.resetar()
    def resetar(self):
        self.x, self.y = random.randint(0, WIDTH), HEIGHT + 20
        self.vel_x, self.vel_y = random.uniform(-0.5, 0.5), random.uniform(-1.5, -0.5)
        self.alpha, self.timer = random.randint(80, 180), 0
        self.cor = random.choice([ROSA, ROSA_CLARO, LILAS, DOURADO])
        self.simbolo, self.drift = random.choice(["♥", "♡", "★", "★"]), random.uniform(-0.3, 0.3)
    def atualizar(self):
        self.x += self.vel_x + math.sin(self.timer * 0.05) * self.drift
        self.y += self.vel_y
        self.alpha -= 0.5
        self.timer += 1
        if self.y < -30 or self.alpha <= 0: self.resetar()
    def desenhar(self, surf):
        render = FONTES["coracao"].render(self.simbolo, True, self.cor)
        render.set_alpha(int(self.alpha))
        surf.blit(render, (int(self.x), int(self.y)))

PARTICULAS = [Particula() for _ in range(25)]

# ─── Classes do jogo ───────────────────────────────────────────────────────────
@dataclass
class Personagem:
    id: int
    nome: str
    expressao: str = "normal"
    _afinidade: int = 0

    @property
    def afinidade(self): return self._afinidade
    def alterar_afinidade(self, valor): self._afinidade = max(0, min(100, self._afinidade + valor))

    def desenhar_sprite(self, surf, x, y, largura=240, altura=480):
        chave = self.nome.lower() + self.expressao
        imagem = IMGS.get(chave, IMGS.get(self.nome.lower() + "normal"))

        if imagem:
            iw, ih = imagem.get_size()
            novo_w, novo_h = int(iw * min(largura/iw, altura/ih)), int(ih * min(largura/iw, altura/ih))
            blit_x, blit_y = x + (largura - novo_w) // 2, y + (altura - novo_h)
            sombra = pygame.Surface((novo_w, 18), pygame.SRCALPHA)
            pygame.draw.ellipse(sombra, (0, 0, 0, 45), (0, 0, novo_w, 18))
            surf.blit(sombra, (blit_x, blit_y + novo_h - 8))
            surf.blit(pygame.transform.smoothscale(imagem, (novo_w, novo_h)), (blit_x, blit_y))
        else:
            silhueta = pygame.Surface((largura, altura), pygame.SRCALPHA)
            pygame.draw.rect(silhueta, (200, 180, 200, 60), (0, 0, largura, altura), border_radius=20)
            pygame.draw.rect(silhueta, (*ROSA_ESCURO, 100), (0, 0, largura, altura), 2, border_radius=20)
            surf.blit(silhueta, (x, y))
            aviso = FONTES["ui"].render(f"[{self.nome}]", True, ROSA_CLARO)
            surf.blit(aviso, (x + (largura - aviso.get_width()) // 2, y + altura // 2 - 10))

        nome_surf = FONTES["ui"].render(self.nome, True, BRANCO)
        nome_bg = pygame.Surface((nome_surf.get_width()+20, nome_surf.get_height()+8), pygame.SRCALPHA)
        pygame.draw.rect(nome_bg, (*ROSA_ESCURO, 180), nome_bg.get_rect(), border_radius=10)
        cx = x + largura // 2
        surf.blit(nome_bg, (cx - nome_surf.get_width()//2 - 10, y + altura - 32))
        surf.blit(nome_surf, (cx - nome_surf.get_width()//2, y + altura - 28))

@dataclass
class Cena:
    personagem: Personagem | None
    texto: str
    escolhas: list = field(default_factory=list)
    fundo: str = "salaaula"
    musica: str | None = None

@dataclass
class Jogador:
    nomej: str = "Você"

# ─── Objetos globais ───────────────────────────────────────────────────────────
jogador = Jogador()
ta = Personagem(1, "Talita")
va = Personagem(2, "Victoria")
vr = Personagem(3, "Victor")
ts = Personagem(4, "Talisson")
pfsr = Personagem(5, "Fabiano")
bff  = Personagem(6, "Catarina")
PAQUERAS = [ta, va, vr, ts]

# ─── Cenas ─────────────────────────────────────────────────────────────────────
CENAS = {
    0: Cena(None, "Primeiro dia no novo colégio. O coração acelera enquanto você empurra o portão...",
            [("Entrar com confiança", 1, 0), ("Hesitar na entrada", 2, 0)], "patio"),
    1: Cena(None, f"{jogador.nomej} respira fundo e entra com um sorriso. Imediatamente esbarra em alguém.",
            [("Continuar...", 3, 0)], "patio"),
    2: Cena(None, f"Enquanto {jogador.nomej} observa o pátio nervosa, uma voz animada soa atrás dela.",
            [("Continuar...", 3, 0)], "patio"),
    3: Cena(bff, "Ei! Você é nova aqui, né? Eu sou a Catarina! Bem-vinda ao colégio! Posso te mostrar o caminho?",
            [("Aceitar animadamente", 4, 0), ("Agradecer timidamente", 4, 0)], "patio"),
    4: Cena(None, "Catarina te guia pelos corredores até a sala de aula. Você logo percebe alguns rostos que chamam atenção.",
            [("Continuar...", 5, 0)], "salaaula"),
    5: Cena(ta, "Oi! Você deve ser a nova aluna. Eu sou a Talita! Se precisar de qualquer coisa, pode me chamar.",
            [("'Que gentil, obrigada!'", 6, 3), ("'Oi Talita, prazer!'", 6, 2), ("Sorrir sem responder", 6, 0)], "salaaula"),
    6: Cena(ta, "Talita sorri de volta e te aponta o lugar vago ao lado dela. 'Pode sentar aqui se quiser!'",
            [("Sentar do lado dela", 7, 4), ("Agradecer e sentar", 7, 2)], "salaaula"),
    7: Cena(pfsr, "Bom dia, turma! Sou o professor Fabiano. Hoje temos uma nova aluna. Por favor, se apresente.",
            [("Me apresentar com entusiasmo", 8, 0), ("Me apresentar de forma simples", 9, 0)], "salaaula"),
    8: Cena(ta, "Talita te aplaude discretamente com um sorriso genuíno. 'Gostei de você, é muito espontânea!'",
            [("Sorrir de volta", 10, 3), ("Agradecer levemente", 10, 1)], "salaaula"),
    9: Cena(ta, "Talita te olha com uma expressão gentil e acena com a cabeça, aprovando.",
            [("Continuar...", 10, 2)], "salaaula"),
    10: Cena(None, "Toca o sinal para o intervalo. A Catarina aparece correndo.",
            [("Continuar...", 11, 0)], "salaaula"),
    11: Cena(bff, "'Vamos pra cafeteria? Dizem que o crepe de chocolate aqui é incrível!'",
            [("'Adoro chocolate, vamos!'", 12, 0), ("'Prefiro ir ao pátio.'", 13, 0)], "salaaula"),
    12: Cena(ta, "Na cafeteria, você encontra a Talita sentada sozinha. Ela acena e chama você para sentar junto.",
            [("Sentar com a Talita", 14, 4), ("Sentar com a Catarina", 15, 0)], "cafeteria"),
    13: Cena(None, "No pátio, você avista a Talita conversando com a Victoria perto de um banco.",
            [("Aproximar delas", 16, 2), ("Ficar de longe", 10, 0)], "patio"),
    14: Cena(ta, "'Sabia que você ia ser legal quando te vi entrar na sala. Me conta de você!'",
            [("Contar sobre seus hobbies", 17, 4), ("Perguntar sobre ela antes", 18, 5)], "cafeteria"),
    15: Cena(bff, "Catarina te conta todas as fofocas do colégio com uma energia contagiante.",
            [("Continuar...", 19, 0)], "cafeteria"),
    16: Cena(va, "Victoria te olha de cima a baixo. 'Ah, a novata. Talita já me falou de você.'",
            [("'Só coisas boas, espero!'", 17, 2), ("Ficar em silêncio", 19, 0)], "patio"),
    17: Cena(ta, "Talita ri e os olhos dela brilham. 'Você é incrível! Vamos ser grandes amigas, eu sei!'",
            [("'Tomara que sim!'", 19, 5), ("Sorrir de coração", 19, 4)], "cafeteria"),
    18: Cena(ta, "Talita fica surpresa e feliz que você perguntou. Ela começa a falar animada sobre música e livros.",
            [("Continuar...", 17, 3)], "cafeteria"),
    19: Cena(None, "O sinal toca marcando o fim das aulas. Você sai pensando nos novos rostos... especialmente em um deles.",
            [("Continuar...", 20, 0)], "patio"),
    20: Cena(None, "Fim do Capítulo 1 ♥\n\nFoi um primeiro dia cheio de surpresas.\nSua história está apenas começando...", [], "patio"),
}

# ─── Motor do jogo ──────────────────────────────────────────────────────────────
class GerenciadorDeJogo:
    def __init__(self):
        self.velocidade_texto = 2
        self.reiniciar_jogo()

    def reiniciar_jogo(self):
        self.estado = "menu"
        self.menu_hover, self.escolha_hover = -1, -1
        for p in PAQUERAS: p._afinidade = 0
        self._iniciar_cena(0)

    def _cena(self): return CENAS.get(self.cena_atual_id)
    
    def get_menu_rects(self):
        return [pygame.Rect(WIDTH//2-180, 340 + i*80, 360, 52) for i in range(2)]

    def get_escolha_rects(self):
        c = self._cena()
        if not (self.texto_pronto and c.escolhas): return []
        start_y = HEIGHT - 220 - len(c.escolhas) * 52 - 15
        return [pygame.Rect(WIDTH//2-310, start_y + i * 52, 620, 44) for i in range(len(c.escolhas))]

    def _iniciar_cena(self, id_cena):
        self.cena_atual_id = id_cena
        self.texto_completo, self.texto_exibido = self._cena().texto, ""
        self.indice_texto, self.timer_texto = 0, 0
        self.texto_pronto, self.fade_in, self.fade_alpha = False, True, 255

    def _completar_texto(self):
        self.texto_exibido, self.indice_texto, self.texto_pronto = self.texto_completo, len(self.texto_completo), True

    def _atualizar_texto(self):
        if not self.texto_pronto:
            self.timer_texto += 1
            if self.timer_texto >= self.velocidade_texto:
                self.timer_texto = 0
                self.indice_texto += 1
                self.texto_exibido = self.texto_completo[:self.indice_texto]
                if self.indice_texto >= len(self.texto_completo): self.texto_pronto = True

    # ── Renderização ─────────────────────────────────────────────────────────
    def _desenhar_fundo(self, surf):
        img = IMGS.get(self._cena().fundo)
        if img: surf.blit(pygame.transform.smoothscale(img, (WIDTH, HEIGHT)), (0, 0))
        else: gradiente_vertical(surf, (60, 40, 70), (120, 80, 100), (0, 0, WIDTH, HEIGHT))

    def _desenhar_caixa(self, surf):
        c, box_y, box_h = self._cena(), HEIGHT - 220, 215
        caixa = pygame.Surface((WIDTH, box_h), pygame.SRCALPHA)
        pygame.draw.rect(caixa, (15, 8, 12, 215), (0, 0, WIDTH, box_h))
        pygame.draw.line(caixa, (*ROSA, 100), (0, 0), (WIDTH, 0), 2)
        surf.blit(caixa, (0, box_y))

        for px in [20, WIDTH - 35]:
            o = FONTES["coracao"].render("♥", True, ROSA); o.set_alpha(110)
            surf.blit(o, (px, box_y + 8))

        if c.personagem:
            desenhar_retangulo_arredondado(surf, ROSA_ESCURO, (40, box_y - 22, 190, 36), 8, 220)
            surf.blit(FONTES["nome"].render(c.personagem.nome, True, BRANCO), (50, box_y - 18))

        for i, linha in enumerate(quebrar_texto(self.texto_exibido, FONTES["texto"], WIDTH - 110)[:5]):
            surf.blit(FONTES["texto"].render(linha, True, CREME), (55, box_y + 25 + i * 30))

        if self.texto_pronto and not c.escolhas:
            seta = FONTES["ui"].render("▼ clique para continuar", True, ROSA_CLARO)
            seta.set_alpha(int(180 + 75 * math.sin(pygame.time.get_ticks() / 400)))
            surf.blit(seta, (WIDTH - seta.get_width() - 30, box_y + box_h - 28))

    def _desenhar_escolhas(self, surf):
        for i, (rect, (texto, _, delta)) in enumerate(zip(self.get_escolha_rects(), self._cena().escolhas)):
            hover = (i == self.escolha_hover)
            desenhar_retangulo_arredondado(surf, ROSA_ESCURO if hover else (40, 20, 30), rect, 14, 225)
            if hover: pygame.draw.rect(surf, DOURADO, rect, 2, border_radius=14)
            
            t_render = FONTES["escolha"].render(texto, True, ROSA_CLARO if hover else BRANCO)
            surf.blit(t_render, (rect.centerx - t_render.get_width()//2, rect.y + 13))
            
            if delta != 0:
                ic = FONTES["coracao"].render(f"♥{'+' if delta>0 else ''}{delta}", True, ROSA_CLARO if delta>0 else (200,150,150))
                surf.blit(ic, (rect.right - 40, rect.y + 13))

    def _desenhar_hud(self, surf):
        desenhar_retangulo_arredondado(surf, (10, 5, 10), (0, 0, WIDTH, 50), 0, 180)
        surf.blit(FONTES["ui"].render("✿ Doce Encontro ✿", True, ROSA_CLARO), (10, 15))
        x = 220
        for p in [p for p in PAQUERAS if p.afinidade > 0]:
            surf.blit(FONTES["ui"].render(f"♥ {p.nome}", True, ROSA_CLARO), (x, 6))
            desenhar_retangulo_arredondado(surf, CINZA_MEDIO, (x, 28, 130, 10), 5, 180)
            desenhar_retangulo_arredondado(surf, ROSA, (x, 28, int(130*(p.afinidade/100)), 10), 5, 230)
            surf.blit(FONTES["ui"].render(f"{p.afinidade}%", True, ROSA_CLARO), (x + 135, 24))
            x += 200

    def desenhar_menu(self, surf):
        gradiente_vertical(surf, (30, 15, 25), (80, 30, 50), (0, 0, WIDTH, HEIGHT))
        for p in PARTICULAS: p.atualizar(); p.desenhar(surf)
        titulo = FONTES["titulo"].render("Doce Encontro", True, ROSA_CLARO)
        surf.blit(titulo, (WIDTH//2 - titulo.get_width()//2, 150))
        sub = FONTES["subtitulo"].render("~ Uma história de amor no colégio ~", True, CREME)
        surf.blit(sub, (WIDTH//2 - sub.get_width()//2, 220))

        for i, (op, rect) in enumerate(zip(["♥  Começar História", "✿  Sair"], self.get_menu_rects())):
            hover = (i == self.menu_hover)
            desenhar_retangulo_arredondado(surf, ROSA_ESCURO if hover else (50, 25, 40), rect, 16, 220)
            if hover: pygame.draw.rect(surf, DOURADO, rect, 2, border_radius=16)
            render = FONTES["escolha"].render(op, True, ROSA_CLARO if hover else BRANCO)
            surf.blit(render, (rect.centerx - render.get_width()//2, rect.y + 15))

        versao = FONTES["ui"].render("v1.0", True, (100, 70, 80))
        surf.blit(versao, (WIDTH - versao.get_width() - 10, HEIGHT - 25))

    def _desenhar_fim(self, surf):
        gradiente_vertical(surf, (20, 10, 30), (60, 20, 50), (0, 0, WIDTH, HEIGHT))
        for p in PARTICULAS: p.atualizar(); p.desenhar(surf)
        titulo = FONTES["titulo"].render("✿ Fim do Capítulo 1 ✿", True, ROSA_CLARO)
        titulo.set_alpha(int(200 + 55 * math.sin(pygame.time.get_ticks() / 800)))
        surf.blit(titulo, (WIDTH//2 - titulo.get_width()//2, 180))
        sub = FONTES["subtitulo"].render("Sua história de amor está apenas começando...", True, CREME)
        surf.blit(sub, (WIDTH//2 - sub.get_width()//2, 260))

        for y, p in enumerate([p for p in PAQUERAS if p.afinidade > 0]):
            label = FONTES["escolha"].render(f"♥ {p.nome}: {p.afinidade}%", True, ROSA_CLARO)
            surf.blit(label, (WIDTH//2 - label.get_width()//2, 330 + y*40))

        reiniciar = FONTES["ui"].render("[ Clique para voltar ao menu ]", True, DOURADO)
        surf.blit(reiniciar, (WIDTH//2 - reiniciar.get_width()//2, HEIGHT - 80))

    # ── Loop principal e Eventos ──────────────────────────────────────────────
    def executar(self):
        rodando = True
        while rodando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT: rodando = False
                elif evento.type == pygame.MOUSEMOTION:
                    if self.estado == "menu": self.menu_hover = next((i for i, r in enumerate(self.get_menu_rects()) if r.collidepoint(evento.pos)), -1)
                    elif self.estado == "jogo": self.escolha_hover = next((i for i, r in enumerate(self.get_escolha_rects()) if r.collidepoint(evento.pos)), -1)
                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    if self.estado == "menu":
                        if self.get_menu_rects()[0].collidepoint(evento.pos): self.estado = "jogo"; self._iniciar_cena(0)
                        elif self.get_menu_rects()[1].collidepoint(evento.pos): rodando = False
                    elif self.estado == "jogo":
                        if not self.texto_pronto: self._completar_texto()
                        else:
                            rects = self.get_escolha_rects()
                            idx = next((i for i, r in enumerate(rects) if r.collidepoint(evento.pos)), -1)
                            if idx != -1:
                                c = self._cena()
                                if c.personagem and c.escolhas[idx][2]: c.personagem.alterar_afinidade(c.escolhas[idx][2])
                                self._iniciar_cena(c.escolhas[idx][1])
                            elif not rects:
                                prox = self.cena_atual_id + 1
                                if prox in CENAS: self._iniciar_cena(prox)
                                else: self.estado = "fim"
                    elif self.estado == "fim": self.reiniciar_jogo()
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE and self.estado == "jogo": self.estado = "menu"
                    elif evento.key in (pygame.K_RETURN, pygame.K_SPACE) and self.estado == "jogo" and not self.get_escolha_rects():
                        if not self.texto_pronto: self._completar_texto()
                        else: self._iniciar_cena(self.cena_atual_id + 1) if (self.cena_atual_id + 1) in CENAS else setattr(self, 'estado', 'fim')

            screen.fill(PRETO)
            if self.estado == "menu": self.desenhar_menu(screen)
            elif self.estado == "jogo":
                self._desenhar_fundo(screen)
                for p in PARTICULAS: p.atualizar(); p.desenhar(screen)
                if self._cena().personagem: self._cena().personagem.desenhar_sprite(screen, WIDTH // 2 - 120, 60 + int(math.sin(pygame.time.get_ticks() / 1000 * 0.8) * 4))
                self._atualizar_texto()
                self._desenhar_caixa(screen)
                self._desenhar_escolhas(screen)
                self._desenhar_hud(screen)
                if self.fade_alpha > 0:
                    fade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); fade.fill((0, 0, 0, int(self.fade_alpha)))
                    screen.blit(fade, (0, 0))
                    if self.fade_in: self.fade_alpha = max(0, self.fade_alpha - 6); self.fade_in = self.fade_alpha > 0
            elif self.estado == "fim": self._desenhar_fim(screen)

            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()

if __name__ == "__main__":
    GerenciadorDeJogo().executar()