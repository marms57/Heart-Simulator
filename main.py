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
#aorta_rect = pygame.Rect(450, 50, 300, 300) 

# ---- DATA LIST ----
blood_particles = []
ecg_trace = []

# ---- AORTA POINTS ----
outer_wall = [
    (450,200), (450, 100), (465, 55), (500, 25),
    (550, 20), (600, 35), (650, 120), (650, 500)
]
inner_wall = [
    (500, 200), (500, 120), (515, 85), (530, 70),
    (560, 70), (585, 85), (600, 120), (600, 500)
]


# ---- MATHS AND PHYSICS ENGINES ----
def get_ecg_value(time_val):
    phase = time_val % (2 * math.pi) 
    p = 8 * math.exp(-((phase - 0.2) ** 2) / 0.05) 
    q = -10 * math.exp(-((phase - 0.55) ** 2) / 0.005)
    r = 45 * math.exp(-((phase - 0.65) ** 2) / 0.005)
    s = -15 * math.exp(-((phase - 0.75) ** 2) / 0.005)
    t = 12 * math.exp(-((phase - 2.5) ** 2) / 0.1)
    return -(p + q + r + s + t)

def closest_point_on_line(p, a, b):
    ap = (p[0] - a[0], p[1] - a[1])
    ab = (b[0] - a[0], b[1] - a[1])
    ab2 = ab[0]**2 + ab[1]**2
    if ab2 == 0: return a
    t = max(0, min(1, (ap[0]*ab[0] + ap[1]*ab[1]) / ab2))
    return (a[0] + ab[0] * t, a[1] + ab[1] * t)

def resolve_collision(particle, a, b):
    px, py, vx, vy = particle[0], particle[1], particle[2], -particle[3]

    cx, cy = closest_point_on_line((px, py), a, b)
    dx, dy = px - cx, py - cy
    dist = math.sqrt(dx**2 + dy**2)
    radius = 8

    if dist < radius and dist > 0:
        nx, ny = dx / dist, dy / dist
        overlap = radius - dist
        particle[0] += nx * overlap
        particle[1] += ny * overlap

        dot_product = vx * nx + vy * ny
        if dot_product < 0:
            bounce = 0.1
            slide = 0.98

            new_vx = (vx - (1 + bounce) * dot_product * nx) * slide
            new_vy = (vy - (1 + bounce) * dot_product * ny) * slide
            particle[2] = new_vx
            particle[3] = -new_vy

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
    is_systole = math.sin(t) > 0.8 # True when the heart is contracting
    #polygon math update
    base_stretch = 20 + (edv * 0.4) 
    pulse = math.cos(t) * (ejection_fraction * (edv * 0.4)) 
    current_stretch = pulse + base_stretch

    # 3.1 ---- TRIGGER BLOOD FLOW ----
    if is_systole:
        num_particles = int(ejection_fraction * edv)
        for _ in range(num_particles):
            start_x = 475 + random.uniform(-10, 10)
            start_y = 230 + random.uniform(-10, 15)
            speed = random.uniform(-1.0, 1.0)
            lift = abs((ejection_fraction * 15) + random.uniform(4, 7))
            blood_particles.append([start_x, start_y, speed, lift])

    # 3.1.1 ---- UPDATE AND DRAW THE PARTICLES ----
    gravity = 0.1 
    center_x, center_y = 600, 200
    
    for p in blood_particles[:]: 
        p[3] -= gravity
        steps = 3
        
        # Start of Sub-step loop
        for _ in range(steps):
            p[0] += p[2] / steps
            p[1] -= p[3] / steps
                
            # FIX: These collision checks MUST be indented inside the steps loop!
            # ---- COLLISION WITH AORTA WALLS ----
            for i in range(len(outer_wall) - 1):
                resolve_collision(p, outer_wall[i], outer_wall[i + 1])

            for i in range(len(inner_wall) - 1):
                resolve_collision(p, inner_wall[i], inner_wall[i + 1])
        # End of Sub-step loop

        p[2] *= vessel_friction 

        # Valve Kill Zone
        if p[1] > 200 and p[3] < 0 and p[0] < 550:
            blood_particles.remove(p)
            continue

        pygame.draw.circle(screen, BLOOD_COLOR, (int(p[0]), int(p[1])), 4)

        # Adjusted off-screen removal width to 900
        if p[0] > 900 or p[1] > 500:
            blood_particles.remove(p)

    # 4.0 ---- DRAW THE HEART & PLUMBING ----
    pygame.draw.lines(screen, AORTA_COLOR, False, outer_wall, 6)
    pygame.draw.lines(screen, AORTA_COLOR, False, inner_wall, 6)

    # ---- 4.1 LEFT VENTRICLE POLYGON ----
    apex_x  = 475
    apex_y  = 200 + (current_stretch * 2.0)
    lw_x    = 475 - (current_stretch * 0.9)
    lw_y    = 200 + (current_stretch * 0.8)
    rw_x    = 475 + (current_stretch * 0.9)
    rw_y    = 200 + (current_stretch * 0.8)

    lv_points = [
        (450, 200),         # Left aortic root
        (lw_x, lw_y),       # Left free wall
        (apex_x, apex_y),   # Apex
        (rw_x, rw_y),       # Septum
        (500, 200)          # Right aortic root
    ]
    pygame.draw.polygon(screen, HEART_COLOR, lv_points)
    pygame.draw.polygon(screen, (150, 20, 40), lv_points, 4)

    # ---- 4.2 Valve ----
    if is_systole:
        pygame.draw.line(screen, (220, 220, 220), (450, 200), (455, 160), 4)
        pygame.draw.line(screen, (220, 220, 220), (500, 200), (495, 160), 4)
    else:
        pygame.draw.line(screen, (220, 220, 220), (450, 200), (475, 208), 4)
        pygame.draw.line(screen, (220, 220, 220), (500, 200), (475, 208), 4)

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