import pygame
import math
import random

# 1. ---- SETTINGS ----
pygame.init()
screen = pygame.display.set_mode((600, 400))
clock = pygame.time.Clock()

# CLINICAL DATA (change these to see the difference)
ejection_fraction = 0.65 #healthy
#ejection_fraction = 0.25 #HF

#---- PARTICLE LIST ----
blood_particles=[]

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

    # 3.1 ---- TRIGGER BLOOD FLOW ----
    # math.cos(t) helps us detect the down beat of the sine wave
    if math.cos(t) > 0.8:
        #create a new particle at the heart's center
        #speed is tied directly to ejection fraction
        speed = ejection_fraction * 15
        blood_particles.append([200, 200, speed])

        # 3.1.1 ---- UPDATE AND DRAW THE PARTICLES ----
        for p in blood_particles[:]: #iterate over copy of the list
            p[0] += p[2] #moves particle to the right based on the screen

            # draw the blood drop
            pygame.draw.circle(screen,(220, 20, 60), (int(p[0]), int(p[1])), 4)

            #remove blood particles off screen to save memory
            if p[0] > 600:
                blood_particles.remove(p)


    # 4. ---- DRAW THE HEART ----
    # Circle is place holder for ventricle for now

    pygame.draw.circle(screen, (220, 20, 60), (200, 200), int(current_radius))
                   
    pygame.display.flip()
    t += 0.1 #speed of heartbeat
    clock.tick(60) #run at 60 FPS

pygame.quit()