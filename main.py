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

#Draw the aorta
aorta_rect = pygame.Rect(150, 50, 300, 300) # invisible walls for the arch
AORTA_COLOR = (100, 100, 100) #grey

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
        start_y = 120 + random.uniform(-5, 5)

        #add randomness to speed of ejection fraction
        speed = abs((ejection_fraction * 12) + random.uniform(2, 4))
        lift = 10 + random.uniform(1, 1) #intial upward force of the contraction, with randomness add to lift
        blood_particles.append([start_x, start_y, speed, lift])

        # 3.1.1 ---- UPDATE AND DRAW THE PARTICLES ----
        
        gravity = 0.2 #pulls blood down aorta
        center_x, center_y = 200, 125


    for p in blood_particles[:]: #iterate over copy of the list
            # p[0] is x (horizontal),  p[1] is Y (vertical), p[2] is speed
            # add the 4th value: p[3] for vertical lift

            #Move the particle
            p[0] += p[2] #constant right upward flow 
            p[1] -= p[3] #intial upward blast from the ventricle
            p[3] -= gravity #apply the gravity

            # ---- COLLISION LOGIC ----
            dx = p[0] - center_x
            dy = p[1] - center_y
            distance = math.sqrt(dx**2 + dy**2)

            #1. Outer wall logic
            if distance > 150:
                 p[3] *= -0.5 #bounce down
                 p[1] += 2 #push back inside

            # 2. Inner wall logic
            if distance < 110 and p[0] > 250:
                 p[3] *= -0.5
                 p[1] -= 2

            # draw the blood drop
            pygame.draw.circle(screen,(220, 20, 60), (int(p[0]), int(p[1])), 4)

            #remove blood particles off screen to save memory
            if p[0] > 600:
                blood_particles.remove(p)


    # 4.0 ---- DRAW THE HEART ----

    # Circle is place holder for ventricle for now
    pygame.draw.circle(screen, (220, 20, 60), (200, 200), int(current_radius))

        #outer wall
    pygame.draw.arc(screen, AORTA_COLOR, aorta_rect, -0.2, 3.14, 5)

    #inner wall
    inner_rect = aorta_rect.inflate(-100, -100)
    pygame.draw.arc(screen, AORTA_COLOR, inner_rect, -0.1, 3.14, 5)
                   
    pygame.display.flip()
    t += 0.1 #speed of heartbeat
    clock.tick(60) #run at 60 FPS

    # 4.1 ---- AORTA WALLS ----
    # draw.arc(surface, color, rect, start_angle, stop_angle, width)
    # Angles are in Radians. 0 is Right, 3.14 is Left.


pygame.quit()