import pygame
import math

# 1. ---- SETTINGS ----
pygame.init()
screen = pygame.display.set_mode((400, 400))
clock = pygame.time.Clock()

# CLINICAL DATA (change these to see the difference)
ejection_fraction = 0.65 #healthy
#ejection_fraction = 0.25 #HF

# 2. ---- MAIN LOOP ----
running = True
t = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255)) #White background

    # 3. ---- BEAT LOGIC ----
    # Sine wave creates a pulse.
    # We multiply by ejection fraction to control the strength
    pulse = math.sin(t) * (ejection_fraction * 40)
    current_radius = 80 + pulse

    # 4. ---- DRAW THE HEART ----
    # Circle is place holder for ventricle for now

    pygame.draw.circle(screen, (220, 20, 60), (200, 200), int(current_radius))
                   
    pygame.display.flip()
    t += 0.1 #speed of heartbeat
    clock.tick(60) #run at 60 FPS

pygame.quit()