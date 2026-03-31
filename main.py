import pygame
import math
import random

# 1. ---- SETTINGS ----
pygame.init()
pygame.font.init()

# Using a slightly sleeker default font if available, fallback to arial
my_font = pygame.font.SysFont('trebuchetms', 22) 
bold_font = pygame.font.SysFont('trebuchetms', 24, bold=True)

# FIX 1: Expanded screen width from 600 to 900 for a true dashboard layout
screen = pygame.display.set_mode((900, 500))
clock = pygame.time.Clock()

# CLINICAL DATA
healthy_ef = 0.65 
hf_ef = 0.25 
is_healthy = True 
ejection_fraction = healthy_ef

bpm = 60 
vessel_friction = 0.99 
edv = 100 

# ---- UI COLORS (DARK MODE) ----
BG_COLOR = (25, 28, 36)          
PANEL_COLOR = (40, 45, 55)       
AORTA_COLOR = (120, 125, 140)    
HEART_COLOR = (240, 40, 70)      
BLOOD_COLOR = (255, 60, 90)      
TEXT_MUTED = (180, 185, 200)     
COLOR_HR = (50, 255, 100)        
COLOR_BP = (255, 80, 80)         
COLOR_VOL = (80, 200, 255)       

# FIX 2: Shifted Aorta 300px to the right
aorta_rect = pygame.Rect(450, 50, 300, 300) 

# ---- DATA LIST ----
blood_particles = []
ecg_trace = []

# ---- ECG MATHS ENGINES ----
def get_ecg_value(time_val):
    phase = time_val % (2 * math.pi) 
    p = 8 * math.exp(-((phase - 0.2) ** 2) / 0.05) 
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
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                bpm = min(220, bpm + 10) 
            if event.key == pygame.K_DOWN:
                bpm = max(30, bpm - 10) 
            if event.key == pygame.K_SPACE:
                is_healthy = not is_healthy 
                ejection_fraction = healthy_ef if is_healthy else hf_ef
            if event.key == pygame.K_LEFT:
                vessel_friction = min(1.00, vessel_friction + 0.01) 
            if event.key == pygame.K_RIGHT:
                vessel_friction = max(0.90, vessel_friction - 0.01) 
            if event.key == pygame.K_w:
                edv = min(160, edv + 10) 
            if event.key == pygame.K_s:
                edv = max(40, edv - 10) 
        
    screen.fill(BG_COLOR) 

    # 3. ---- BEAT LOGIC ----
    base_radius = 30 + (edv * 0.5) 
    pulse = math.cos(t) * (ejection_fraction * (edv * 0.4)) 
    current_radius = pulse + base_radius

    # 3.1 ---- TRIGGER BLOOD FLOW ----
    if math.sin(t) > 0.8:
        num_particles = int(ejection_fraction * edv)
        for _ in range(num_particles):
            # Shifted spawn location 300px to the right
            start_x = 520 + random.uniform(-15, 15)
            start_y = 120 + random.uniform(-15, 15)
            speed = abs((ejection_fraction * 10) + random.uniform(2, 4))
            lift = 12 + random.uniform(-1, 2) 
            blood_particles.append([start_x, start_y, speed, lift])

    # 3.1.1 ---- UPDATE AND DRAW THE PARTICLES ----
    gravity = 0.1 
    # Shifted center of physics engine 300px to the right
    center_x, center_y = 600, 200

    for p in blood_particles[:]: 
        p[0] += p[2] 
        p[1] -= p[3] 
        p[3] -= gravity 

        if p[0] > center_x:
            if p[2] > 0:
                p[2] -= 0.05 
                
        p[2] *= vessel_friction 

        # Shifted Valve Kill Zone
        if p[1] > 160 and p[3] < 0 and p[0] < 580:
            blood_particles.remove(p)
            continue

        dx = p[0] - center_x
        dy = p[1] - center_y
        distance = math.sqrt(dx**2 + dy**2)
        angle = math.atan2(dy, dx)

        if distance > 148 and angle < 0.2:
            p[0] = center_x + math.cos(angle) * 146
            p[1] = center_y + math.sin(angle) * 146
            if angle < -0.5:
                p[3] = -abs(p[3] * 0.4) 
            else:
                p[2] *= 0.5 

        # Shifted Inner Wall Logic
        if distance < 105 and angle < 0.2 and p[0] > 580:
            p[3] *= -0.5
            p[0] = center_x + math.cos(angle) * 110
            p[1] = center_y + math.sin(angle) * 110

        pygame.draw.circle(screen, BLOOD_COLOR, (int(p[0]), int(p[1])), 4)

        # Adjusted off-screen removal width to 900
        if p[0] > 900 or p[1] > 400:
            blood_particles.remove(p)

    # 4.0 ---- DRAW THE HEART & PLUMBING ----
    inner_rect = aorta_rect.inflate(-100, -100)
    pygame.draw.arc(screen, AORTA_COLOR, inner_rect, -0.1, 3.14, 6)
    pygame.draw.arc(screen, AORTA_COLOR, aorta_rect, -0.2, 3.14, 6)
    
    # Shifted Ventricle to the right
    pygame.draw.circle(screen, HEART_COLOR, (500, 200), int(current_radius))
    pygame.draw.circle(screen, (150, 20, 40), (500, 200), int(current_radius), 3) 

    # 5.0 ---- TELEMETRY ECG TRACE ----
    # Expanded ECG background width to 900
    pygame.draw.rect(screen, (10, 20, 15), (0, 400, 900, 100)) 
    
    # Expanded Grid
    for i in range(0, 900, 25):
        pygame.draw.line(screen, (20, 45, 30), (i, 400), (i, 500))
    for i in range(400, 500, 25):
        pygame.draw.line(screen, (20, 45, 30), (0, i), (900, i))

    current_ecg_y = 450 + get_ecg_value(t) 
    ecg_trace.append(current_ecg_y) 

    # Expanded trace limit to 900
    if len(ecg_trace) > 900: 
        ecg_trace.pop(0)

    if len(ecg_trace) > 1:
        points = [(i, ecg_trace[i]) for i in range(len(ecg_trace))]
        pygame.draw.lines(screen, COLOR_HR, False, points, 2)

    # 6.0 ---- CLINICAL DASHBOARD (UI PANELS) ----
    
    # FIX 3: Expanded Panel Widths from 250 to 340 to prevent text overflow!
    pygame.draw.rect(screen, PANEL_COLOR, (15, 15, 340, 95), border_radius=8)
    pygame.draw.rect(screen, PANEL_COLOR, (15, 290, 340, 95), border_radius=8)

    # Variables for text
    status_text = "Healthy" if is_healthy else "Heart Failure"
    ef_display = int(ejection_fraction * 100)
    rounded_friction = round(vessel_friction, 2)
    if rounded_friction == 0.99: tone_text = "Normal"
    elif rounded_friction < 0.99: tone_text = "High Afterload"
    else: tone_text = "Low Afterload"

    base_diastolic = 80 + ((0.99 - vessel_friction) * 400)  
    arch_particles = [p for p in blood_particles if p[1] < 200]  
    pulse_pressure = len(arch_particles) * 0.06 
    systolic = int(base_diastolic + pulse_pressure)
    diastolic = int(base_diastolic)
    stroke_volume = int(ejection_fraction * edv)

    # ---- RENDER TEXT TO PANELS ----
    bpm_text = bold_font.render(f"HR: {bpm} BPM", True, COLOR_HR)
    status_render = my_font.render(f"LV Status: {status_text} ({ef_display}%)", True, TEXT_MUTED)
    tone_render = my_font.render(f"Tone: {tone_text}", True, TEXT_MUTED)
    
    screen.blit(bpm_text, (25, 22))
    screen.blit(status_render, (25, 52))
    screen.blit(tone_render, (25, 77))

    bp_text = bold_font.render(f"Arterial BP: {systolic}/{diastolic} mmHg", True, COLOR_BP)
    preload_text = my_font.render(f"Preload (EDV): {edv} mL", True, COLOR_VOL)
    sv_text = my_font.render(f"Stroke Volume: {stroke_volume} mL", True, COLOR_VOL)

    screen.blit(bp_text, (25, 298))
    screen.blit(preload_text, (25, 328))
    screen.blit(sv_text, (25, 353))

    pygame.display.flip()
    t += (bpm / 60) * 0.15 
    clock.tick(60)

pygame.quit()