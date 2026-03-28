import pygame
import math
import random

# 1. ---- SETTINGS ----
pygame.init()
screen = pygame.display.set_mode((600, 400))
clock = pygame.time.Clock()

# CLINICAL DATA (change these to see the difference)
#ejection_fraction = 0.70 #healthy
ejection_fraction = 0.25 #HF

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
        #add scatter to the starting point of the heart

        start_x = 200 + random.uniform(-5, 5)
        start_y = 200 + random.uniform(-5, 5)

        #add randomness to speed of ejection fraction
        speed = (ejection_fraction * 10) + random.uniform(5, -5)
        lift = 8 + random.uniform(1, -1.5) #intial upward force of the contraction, with randomness add to lift
        blood_particles.append([200, 200, speed, lift])

        # 3.1.1 ---- UPDATE AND DRAW THE PARTICLES ----
        
        gravity = 0.2 #pulls blood down aorta


    for p in blood_particles[:]: #iterate over copy of the list
            # p[0] is x (horizontal),  p[1] is Y (vertical), p[2] is speed
            # add the 4th value: p[3] for vertical lift

            #Move the particle
            p[0] += p[2] #constant right upward flow 
            p[1] -= p[3] #intial upward blast from the ventricle

            #apply the gravity
            p[3] -= gravity

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