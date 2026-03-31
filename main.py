import pygame
import math
import random

# 1. ---- SETTINGS ----
pygame.init()
pygame.font.init()
my_font = pygame.font.SysFont('arial', 24)
screen = pygame.display.set_mode((600, 500))
clock = pygame.time.Clock()

# CLINICAL DATA
healthy_ef = 0.65 # healthy
hf_ef = 0.25 # HF
is_healthy = True #start simulation in healthy state
ejection_fraction = healthy_ef

bpm = 60 #resting HR
vessel_friction = 0.99 # peripheral resistance factor
edv = 100 # end-diastolic volume (ml)

# Draw the aorta
aorta_rect = pygame.Rect(150, 50, 300, 300) # invisible walls for the arch
AORTA_COLOR = (100, 100, 100) # grey

# ---- DATA LIST ----
blood_particles = []
ecg_trace = []

# ---- ECG MATHS ENGINES ----
def get_ecg_value(time_val):
    phase = time_val % (2 * math.pi) #locks ecg to physical heartbeat
    p = 8 * math.exp(-((phase - 0.2) ** 2) / 0.05) # math bell curve to build the wave
    q = -10 * math.exp(-((phase - 0.55) ** 2) / 0.005)
    r = 45 * math.exp(-((phase - 0.65) ** 2) / 0.005)
    s = -15 * math.exp(-((phase - 0.75) ** 2) / 0.005)
    t = 12 * math.exp(-((phase - 2.5) ** 2) / 0.1)
    return -(p + q + r + s + t)


# 2. ---- MAIN LOOP ----
running = True
t = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # ---- KEYBOARD CONTROLS ----

            # ---- HEART RATE CONTROL ----
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                bpm = min(220, bpm + 10) # heart rate capped
            if event.key == pygame.K_DOWN:
                bpm = max(30, bpm - 10) # bradycardia

            # ---- EJECTION FRACTION SWITCH ----
            if event.key == pygame.K_SPACE:
                is_healthy = not is_healthy #flip the state
                ejection_fraction = healthy_ef if is_healthy else hf_ef

            # ---- PERIPHERAL RESISTANCE SWITCH ----
            if event.key == pygame.K_LEFT:
                vessel_friction = min(1.00, vessel_friction + 0.01) # increase resistance
            if event.key == pygame.K_RIGHT:
                vessel_friction = max(0.90, vessel_friction - 0.01) # decrease resistance

            #---- PRELOAD CONTROL ----
            if event.key == pygame.K_w:
                edv = min(160, edv + 10) # increase venous return
            if event.key == pygame.K_s:
                edv = max(40, edv - 10) # decrease venous return
        

    screen.fill((255, 255, 255)) # White background

    # 3. ---- BEAT LOGIC ----
    base_radius = 30 + (edv * 0.5) # preload effect on stroke volume
    pulse = math.cos(t) * (ejection_fraction * (edv * 0.4)) # pulse effect on stroke volume
    current_radius = pulse + base_radius

    # 3.1 ---- TRIGGER BLOOD FLOW ----
    if math.sin(t) > 0.8:
        # Spawn at the top-right of the heart circle
        num_particles = int(ejection_fraction * 100)
        for _ in range(num_particles):
            start_x = 220 + random.uniform(-15, 15)
            start_y = 120 + random.uniform(-15, 15)

            speed = abs((ejection_fraction * 10) + random.uniform(2, 4))
            lift = 12 + random.uniform(-1, 2) 
            blood_particles.append([start_x, start_y, speed, lift])

    # 3.1.1 ---- UPDATE AND DRAW THE PARTICLES ----
    gravity = 0.1 
    # Center must be x=300 to match aorta_rect(150, 50, 300, 300)
    center_x, center_y = 300, 200

    for p in blood_particles[:]: 
        # Move the particle
        p[0] += p[2] 
        p[1] -= p[3] 
        p[3] -= gravity 

        if p[0] > center_x:
            # Prevent negative velocity loop (wind trap)
            if p[2] > 0:
                p[2] -= 0.05 
                
        p[2] *= vessel_friction # apply peripheral resistance 

        # Aortic Valve (Kill Zone)
        if p[1] > 160 and p[3] < 0 and p[0] < 280:
            blood_particles.remove(p)
            continue

        # ---- COLLISION LOGIC ----
        dx = p[0] - center_x
        dy = p[1] - center_y
        distance = math.sqrt(dx**2 + dy**2)
        angle = math.atan2(dy, dx)

        # 1. Outer wall logic (Radius 150)
        if distance > 148 and angle < 0.2:
            p[0] = center_x + math.cos(angle) * 146
            p[1] = center_y + math.sin(angle) * 146

            # ZONE A: The Roof
            if angle < -0.5:
                p[3] = -abs(p[3] * 0.4) # Bounce down with reduced force
            # ZONE B: The Drop
            else:
                p[2] *= 0.5 # Kill horizontal momentum

        # 2. Inner wall logic (Radius 100)
        if distance < 105 and angle < 0.2 and p[0] > 280:
            p[3] *= -0.5
            p[0] = center_x + math.cos(angle) * 110
            p[1] = center_y + math.sin(angle) * 110

        # draw the blood drop
        pygame.draw.circle(screen, (220, 20, 60), (int(p[0]), int(p[1])), 4)

        # remove blood particles off screen
        if p[0] > 600 or p[1] > 400:
            blood_particles.remove(p)

    # 4.0 ---- DRAW THE HEART ----
    pygame.draw.circle(screen, (220, 20, 60), (200, 200), int(current_radius))

    # outer wall
    pygame.draw.arc(screen, AORTA_COLOR, aorta_rect, -0.2, 3.14, 5)

    # inner wall
    inner_rect = aorta_rect.inflate(-100, -100)
    pygame.draw.arc(screen, AORTA_COLOR, inner_rect, -0.1, 3.14, 5)

    # ---- ECG TRACE ----
    pygame.draw.rect(screen, (15, 15, 15), (0, 400, 600, 100)) # ECG background
    current_ecg_y = 450 + get_ecg_value(t) #calculate current ECG value
    ecg_trace.append(current_ecg_y) #add to trace list

    if len(ecg_trace) > 600: #limit trace length
        ecg_trace.pop(0)

    if len(ecg_trace) > 1:
        points = [(i, ecg_trace[i]) for i in range(len(ecg_trace))]
        pygame.draw.lines(screen, (50, 255, 50), False, points, 2)

    # Clinical monitor (BPM)
    status_text = "Healthy" if is_healthy else "Heart Failure"
    ef_display = int(ejection_fraction * 100)

    # Rounded friction display for user friendliness
    rounded_friction = round(vessel_friction, 2)

    #Peripheral resistance
    if rounded_friction == 0.99:
        tone_text = "Normal"
    elif rounded_friction < 0.99:
        tone_text = "High Afterload"
    else: 
        tone_text = "Low Afterload"

    # ---- BLOOD PRESSURE ESTIMATION ----
    base_diastolic = 80 + ((0.99 - vessel_friction) * 400)  # Normal tone (0.99) = 80 mmHg, High Afterload (0.90) = 116 mmHg
    arch_particles = [p for p in blood_particles if p[1] < 200]  # Sensor for arterial pressure, only detecting blood in the upper aorta
    pulse_pressure = len(arch_particles) * 0.06 # Multiply the active particles by pressure coefficient (0.6)
    #instant_bp = int(base_diastolic +   pulse_pressure) USABLE?
    systolic = int(base_diastolic + pulse_pressure)
    diastolic = int(base_diastolic)
    stroke_volume = int(ejection_fraction * edv)

    # ---- RENDER TEXT ----

    bpm_text = my_font.render(f"Heart Rate: {bpm} BPM", True, (50, 50, 50))
    status_render = my_font.render(f"Status: {status_text} (EF: {ef_display}%)", True, (50, 50, 50))
    tone_render = my_font.render(f"Vessel Tone: {tone_text}", True, (50, 50, 50))
    bp_render = my_font.render(f"Arterial Pressure: {systolic}/{diastolic} mmHg", True, (220, 20, 60))
    preload_render = my_font.render(f"Preload (EDV): {edv} mL | Stroke Volume: {stroke_volume} mL", True, (20, 100, 200))

    screen.blit(bpm_text, (20, 20))
    screen.blit(status_render, (20, 50))
    screen.blit(tone_render, (20, 80))
    screen.blit(bp_render, (20, 370))
    screen.blit(preload_render, (20, 340))


    pygame.display.flip()
    t += (bpm / 60) * 0.15 
    clock.tick(60)

pygame.quit()