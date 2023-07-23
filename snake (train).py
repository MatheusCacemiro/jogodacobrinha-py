# -*- coding: utf-8 -*-

import pygame
import random
import cv2
import mediapipe as mp

pygame.init()
pygame.display.set_caption('Snake')
largura, altura = 1000, 800
tela = pygame.display.set_mode((largura, altura))
relogio = pygame.time.Clock()

# cores RGB
preto = (0, 0, 0)
branco = (255, 255, 255)
vermelho = (255, 0, 0)
verde = (0, 255, 0)

# parâmetro cobra
tamanho_quadrado = 8
velocidade_cobra = 30

# pontuacao
pontuacao = 0

# gerar_comida
def gerar_comida():
    comida_x = round(random.randrange(
        0, largura - tamanho_quadrado) / 20.0) * 20.0
    comida_y = round(random.randrange(
        0, altura - tamanho_quadrado) / 20.0) * 20.0
    return comida_x, comida_y

def desenhar_comida(tamanho, comida_x, comida_y):
    pygame.draw.rect(tela, vermelho, [comida_x, comida_y, tamanho, tamanho])

def desenhar_cobra(tamanho, pixels):
    for pixel in pixels:
        pygame.draw.rect(tela, branco, [pixel[0], pixel[1], tamanho, tamanho])

video = cv2.VideoCapture(0)

hand = mp.solutions.hands
Hand = hand.Hands(max_num_hands=2)
mpDraw = mp.solutions.drawing_utils

def dedos_levantados(pontos):
    dedos = [False, False, False, False, False]  # Inicialmente, nenhum dedo está levantado
    if pontos:
        for i in range(5):
            dedos[i] = pontos[i][1] < pontos[i - 2][1]
    return dedos

def jogo():
    fim_jogo = False
    x = largura / 2
    y = altura / 2
    velocidade_x = 0
    velocidade_y = 0
    tamanho_cobra = 1
    pixels = []
    comida_x, comida_y = gerar_comida()
    start_ticks = pygame.time.get_ticks()

    while not fim_jogo:
        tela.fill(preto)

        seconds = (pygame.time.get_ticks() - start_ticks) / 1000
        min, sec = divmod(seconds, 60)
        hour, min = divmod(min, 60)
        fonte = pygame.font.SysFont('Prosa', 25)
        texto = fonte.render(f"{int(hour)}:{int(min)}:{int(sec)}",  True, verde)
        tela.blit(texto, [10, 35])

        formatted_time = f"{int(hour)}:{int(min)}:{int(sec)}"

        check, img = video.read()
        imgRBG = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = Hand.process(imgRBG)
        handsPoints = results.multi_hand_landmarks
        h, w, _ = img.shape
        pontos = []
        if handsPoints:
            for points in handsPoints:
                mpDraw.draw_landmarks(img, points, hand.HAND_CONNECTIONS)
                for id, cord in enumerate(points.landmark):
                    cx, cy = int(cord.x * w), int(cord.y * h)
                    pontos.append((cx, cy))

        dedo = [8, 12, 16, 20]

        cv2.imshow('Imagem', img)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                fim_jogo = True

        # Lógica de controle da cobrinha pelo teclado
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and velocidade_y == 0:
            velocidade_x = 0
            velocidade_y = -tamanho_quadrado
        elif keys[pygame.K_DOWN] and velocidade_y == 0:
            velocidade_x = 0
            velocidade_y = tamanho_quadrado
        elif keys[pygame.K_RIGHT] and velocidade_x == 0:
            velocidade_x = tamanho_quadrado
            velocidade_y = 0
        elif keys[pygame.K_LEFT] and velocidade_x == 0:
            velocidade_x = -tamanho_quadrado
            velocidade_y = 0

        # Lógica de controle da cobrinha pelos gestos da mão
        if pontos:
            dedos = dedos_levantados(pontos)
            if dedos[0]:  # Dedão levantado (esquerda)
                velocidade_x = -tamanho_quadrado
                velocidade_y = 0
            elif dedos[1]:  # Indicador levantado (cima)
                velocidade_x = 0
                velocidade_y = -tamanho_quadrado
            elif dedos[4]:  # Mindinho levantado (direita)
                velocidade_x = tamanho_quadrado
                velocidade_y = 0
            elif dedos[2]:  # Dedo do meio levantado (baixo)
                velocidade_x = 0
                velocidade_y = tamanho_quadrado

        desenhar_comida(tamanho_quadrado, comida_x, comida_y)

        x += velocidade_x
        y += velocidade_y

        pixels.append([x, y])
        if len(pixels) > tamanho_cobra:
            del pixels[0]

        for pixel in pixels[:-1]:
            if pixel == [x, y]:
                fim_jogo = True

        if x < 0 or x >= largura or y < 0 or y >= altura:
            fim_jogo = True

        desenhar_cobra(tamanho_quadrado, pixels)

        pontuacao = tamanho_cobra - 1
        fonte = pygame.font.SysFont('Prosa', 25)
        texto = fonte.render(f"Pontos: {pontuacao}", True, verde)
        tela.blit(texto, [10, 10])

        if x == comida_x and y == comida_y:
            tamanho_cobra += 1
            comida_x, comida_y = gerar_comida()

        if fim_jogo:
            print(f"Pontuacao final: {pontuacao}")
            print(f"Tempo final: {formatted_time}")

        pygame.display.update()
        relogio.tick(velocidade_cobra)

jogo()
