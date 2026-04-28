# -*- coding: utf-8 -*-
"""
Berramdane Model V12.1 – النسخة العربية (واجهة عربية / جدول إنجليزي)
Author : Al Moalim Berramdane
License: CC BY 4.0

- جميع عناصر التحكم والشروح بالعربية.
- الجدول باللغة الإنجليزية لتجنب مشاكل الاتجاه.
- المقارنة مع Jönsson تظهر فقط في وضع الإلكترون.
"""

import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import interact, FloatSlider, Checkbox, IntSlider, Dropdown, Button, Output
from scipy.signal import find_peaks
import pandas as pd
from IPython.display import display
import warnings
warnings.filterwarnings('ignore')

# === الثوابت ===
h = 6.626e-34
m = 9.109e-31
c = 3e8
REF_SPACING_MM = 0.18   # Jönsson 1961
REF_V = 70000.0
REF_A = 0.3e-6
REF_D = 1.0e-6

# === دوال الفيزياء (كما هي) ===
def de_broglie_wavelength(v):
    return h / (m * v)

def double_slit_intensity_by_wavelength(x, wavelength, L, a_width, d_slit):
    beta = (np.pi * d_slit * x) / (wavelength * L)
    interference = np.cos(beta)**2
    alpha = (np.pi * a_width * x) / (wavelength * L)
    envelope = np.sinc(alpha / np.pi)**2
    return interference * envelope

def double_slit_intensity_with_spread(x, v_mean, delta_v, L, a_width, d_slit, n_samples=100):
    velocities = np.random.normal(v_mean, delta_v, n_samples)
    total = np.zeros_like(x)
    for v in velocities:
        lam = de_broglie_wavelength(v)
        total += double_slit_intensity_by_wavelength(x, lam, L, a_width, d_slit)
    return total / n_samples

def particle_like_pattern(x, wavelength, L, a_width, d_slit):
    sigma = a_width * L / wavelength
    I_left = np.exp(-(x + d_slit/2)**2 / (2 * sigma**2))
    I_right = np.exp(-(x - d_slit/2)**2 / (2 * sigma**2))
    return 0.5 * (I_left + I_right)

def compute_visibility(x, I):
    peaks, _ = find_peaks(I, distance=len(x)//30)
    if len(peaks) < 2:
        return 0.0
    I_max = np.max(I[peaks])
    center_idx = np.argmin(np.abs(x))
    search = np.where(np.abs(x - x[center_idx]) < 5e-3)[0]
    I_min = np.min(I[search]) if len(search) > 0 else np.min(I)
    return (I_max - I_min) / (I_max + I_min) if (I_max + I_min) > 0 else 0

def white_light_pattern_rgb(x, L, a_width, d_slit):
    lam_R, lam_G, lam_B = 650e-9, 532e-9, 450e-9
    I_R = double_slit_intensity_by_wavelength(x, lam_R, L, a_width, d_slit)
    I_G = double_slit_intensity_by_wavelength(x, lam_G, L, a_width, d_slit)
    I_B = double_slit_intensity_by_wavelength(x, lam_B, L, a_width, d_slit)
    max_val = max(np.max(I_R), np.max(I_G), np.max(I_B))
    if max_val > 0:
        I_R, I_G, I_B = I_R/max_val, I_G/max_val, I_B/max_val
    return I_R, I_G, I_B

# === زر التصدير ===
current_x, current_I = None, None
export_button = Button(description="📥 تحميل البيانات (CSV)", button_style='success')
export_output = Output()

def on_export_clicked(b):
    global current_x, current_I
    with export_output:
        export_output.clear_output()
        if current_x is not None and current_I is not None:
            pd.DataFrame({'Position_mm': current_x*1000, 'Intensity': current_I}).to_csv('berramdane_data.csv', index=False)
            print("✅ تم التصدير بنجاح")
        else:
            print("❌ لا توجد بيانات. شغل المحاكاة أولاً.")
export_button.on_click(on_export_clicked)

# ========== الواجهة العربية ==========
@interact(
    mode=Dropdown(options=['إلكترون (دي برولي)', 'فوتون (أحادي اللون)', 'ضوء أبيض (RGB)'], 
                  value='إلكترون (دي برولي)', description='نمط المحاكاة'),
    L_mm=FloatSlider(value=350, min=10, max=1000, step=5, description='المسافة L (مم)', continuous_update=False),
    v_mean=FloatSlider(value=REF_V, min=20000, max=150000, step=1000, description='سرعة الإلكترون (م/ث)', continuous_update=False),
    delta_v=FloatSlider(value=0.0, min=0.0, max=20000, step=1000, description='انتشار السرعة Δv (م/ث)', continuous_update=False),
    wavelength_nm=FloatSlider(value=532, min=380, max=750, step=1, description='الطول الموجي (نانومتر)', continuous_update=False),
    a_width=FloatSlider(value=REF_A, min=0.1e-6, max=2.0e-6, step=0.01e-6, description='عرض الشق (متر)', continuous_update=False),
    d_slit=FloatSlider(value=REF_D, min=0.1e-6, max=2.0e-6, step=0.01e-6, description='تباعد الشقين (متر)', continuous_update=False),
    observer_active=Checkbox(value=False, description='مكتشف المسار (ON)'),
    meas_strength=FloatSlider(value=0.0, min=0.0, max=1.0, step=0.05, description='قوة القياس'),
    temperature=FloatSlider(value=0.0, min=0, max=1000, step=10, description='ضجيج الكاشف (كلفن)', continuous_update=False),
    show_buildup=Checkbox(value=False, description='تراكم الجسيمات التدريجي'),
    n_particles=IntSlider(value=300, min=50, max=1000, step=50, description='عدد الجسيمات')
)
def run_lab_ar(mode, L_mm, v_mean, delta_v, wavelength_nm, a_width, d_slit,
               observer_active, meas_strength, temperature, show_buildup, n_particles):
    
    global current_x, current_I
    L = L_mm / 1000.0
    
    # تحديد الوضع الفعلي للدوال
    if 'إلكترون' in mode:
        physical_mode = 'Electron'
        lam = de_broglie_wavelength(v_mean)
    elif 'فوتون' in mode:
        physical_mode = 'Photon'
        lam = wavelength_nm * 1e-9
    else:
        physical_mode = 'White'
        lam = 532e-9
    
    # المدى الديناميكي
    spacing = lam * L / d_slit
    x_limit = max(0.002, 3 * spacing)
    x = np.linspace(-x_limit, x_limit, 1500)
    current_x = x
    
    # نمط التداخل
    if physical_mode == 'Electron' and delta_v > 0:
        I_interf = double_slit_intensity_with_spread(x, v_mean, delta_v, L, a_width, d_slit, n_samples=80)
    elif physical_mode == 'White':
        I_R, I_G, I_B = white_light_pattern_rgb(x, L, a_width, d_slit)
        I_interf = (I_R + I_G + I_B) / 3.0
    else:
        I_interf = double_slit_intensity_by_wavelength(x, lam, L, a_width, d_slit)
    
    # نمط جسيمي
    if physical_mode == 'White':
        I_particle = particle_like_pattern(x, 532e-9, L, a_width, d_slit)
    else:
        I_particle = particle_like_pattern(x, lam, L, a_width, d_slit)
    
    # تأثير القياس
    if observer_active:
        I = (1 - meas_strength) * I_interf + meas_strength * I_particle
    else:
        I = I_interf
    
    # تراكم تدريجي
    if show_buildup and n_particles > 0:
        cumulative = np.zeros_like(x)
        for _ in range(n_particles):
            if physical_mode == 'Electron' and delta_v > 0:
                I_one = double_slit_intensity_with_spread(x, v_mean, delta_v, L, a_width, d_slit, n_samples=20)
            elif physical_mode == 'White':
                I_R1, I_G1, I_B1 = white_light_pattern_rgb(x, L, a_width, d_slit)
                I_one = (I_R1 + I_G1 + I_B1) / 3.0
            else:
                I_one = double_slit_intensity_by_wavelength(x, lam, L, a_width, d_slit)
            if observer_active:
                I_one = (1 - meas_strength) * I_one + meas_strength * I_particle
            cumulative += I_one
        I = cumulative / n_particles
    
    # ضوضاء
    if temperature > 0:
        noise = (temperature / 1000.0) * 0.15 * np.max(I)
        I += np.random.normal(0, noise, len(I))
        I = np.maximum(I, 0)
    
    if np.max(I) > 0:
        I /= np.max(I)
    current_I = I
    
    visibility = compute_visibility(x, I)
    sim_spacing_mm = spacing * 1000
    sim_first_min_mm = (lam * L / a_width) * 1000
    
    # حساب النسبة المئوية (مع حد أقصى 999% لمنع الأرقام الضخمة)
    if physical_mode == 'Electron':
        err_spacing = min(999, abs(sim_spacing_mm - REF_SPACING_MM) / REF_SPACING_MM * 100)
        err_min = min(999, abs(sim_first_min_mm - REF_SPACING_MM) / REF_SPACING_MM * 100)
    else:
        err_spacing = err_min = 0  # لن تستخدم
    
    # === الرسم ===
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    ax1, ax2, ax3, ax4 = axes[0,0], axes[0,1], axes[1,0], axes[1,1]
    
    # النمط الرئيسي
    ax1.plot(x*1000, I, 'b-', lw=1.5)
    ax1.fill_between(x*1000, I, alpha=0.3)
    title = f'{mode} | وضوح الأهداب = {visibility:.1%} | L = {L_mm} mm'
    if observer_active:
        title += f' | قوة القياس = {meas_strength:.2f}'
    if physical_mode == 'Electron' and delta_v > 0:
        title += f' | Δv = {delta_v/1e3:.0f} كم/ث'
    if temperature > 0:
        title += f' | ضوضاء = {temperature:.0f} K'
    ax1.set_title(title)
    ax1.set_xlabel('الموقع (مم)')
    ax1.set_ylabel('الشدة')
    ax1.set_xlim(-x_limit*1000, x_limit*1000)
    ax1.grid(alpha=0.3)
    
    # شاشة الكاشف
    if physical_mode == 'White':
        I_R, I_G, I_B = white_light_pattern_rgb(x, L, a_width, d_slit)
        screen_rgb = np.zeros((150, len(x), 3))
        screen_rgb[:,:,0] = np.tile(I_R, (150,1))
        screen_rgb[:,:,1] = np.tile(I_G, (150,1))
        screen_rgb[:,:,2] = np.tile(I_B, (150,1))
        ax2.imshow(screen_rgb, aspect='auto', extent=[-x_limit*1000, x_limit*1000, 0, 1])
    else:
        screen = np.tile(I, (150,1))
        im = ax2.imshow(screen, cmap='hot', aspect='auto', extent=[-x_limit*1000, x_limit*1000, 0, 1])
        plt.colorbar(im, ax=ax2, label='الشدة', shrink=0.8)
    ax2.set_title('شاشة الكاشف')
    ax2.set_xlabel('الموقع (مم)')
    ax2.set_yticks([])
    
    # مقارنة التكاملية
    I_interf_norm = I_interf / np.max(I_interf) if np.max(I_interf) > 0 else I_interf
    I_particle_norm = I_particle / np.max(I_particle) if np.max(I_particle) > 0 else I_particle
    ax3.plot(x*1000, I_interf_norm, 'b--', lw=1, alpha=0.7, label='موجة خالصة (تداخل)')
    ax3.plot(x*1000, I_particle_norm, 'r--', lw=1, alpha=0.7, label='جسيم خالص (مسار محدد)')
    ax3.plot(x*1000, I, 'k-', lw=2, label='الحالة الحالية')
    ax3.set_xlim(-x_limit*1000, x_limit*1000)
    ax3.set_ylim(0, 1.05)
    ax3.set_title('مبدأ التكاملية (بور)')
    ax3.set_xlabel('الموقع (مم)')
    ax3.set_ylabel('شدة طبيعية')
    ax3.legend(fontsize=8, loc='upper right')
    ax3.grid(alpha=0.3)
    
    # الجدول (باللغة الإنجليزية)
    ax4.axis('off')
    if physical_mode == 'Electron':
        ax4.text(0.5, 0.92, "📊 Comparison with Jönsson 1961 (Electrons)",
                 transform=ax4.transAxes, ha='center', va='top', fontsize=12, weight='bold')
        data = [
            ["Quantity", "Simulation (mm)", "Reference (mm)", "Error (%)"],
            ["Fringe spacing", f"{sim_spacing_mm:.3f}", f"{REF_SPACING_MM:.2f}", f"{err_spacing:.1f}"],
            ["First minimum", f"{sim_first_min_mm:.3f}", f"{REF_SPACING_MM:.2f}", f"{err_min:.1f}"]
        ]
        table = ax4.table(cellText=data, loc='center', cellLoc='center', bbox=[0.1, 0.35, 0.8, 0.5])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.8)
        for (i, j), cell in table.get_celld().items():
            if i == 0:
                cell.set_facecolor('#dddddd')
                cell.set_text_props(weight='bold')
        explanation = (
            "Note: Reference values from Jönsson (1961) for electrons at 70 km/s,\n"
            "slit width 0.3 µm, separation 1.0 µm. Adjust L to reduce error."
        )
        ax4.text(0.5, 0.08, explanation, transform=ax4.transAxes, ha='center', va='bottom',
                 fontsize=8, style='italic')
    else:
        ax4.text(0.5, 0.7, "📊 Jönsson 1961 comparison applies only to electron mode.",
                 transform=ax4.transAxes, ha='center', va='center', fontsize=11, style='italic')
        theoretical_info = (
            f"Theoretical fringe spacing: {sim_spacing_mm:.3f} mm\n"
            f"Theoretical first minimum: {sim_first_min_mm:.3f} mm"
        )
        ax4.text(0.5, 0.4, theoretical_info, transform=ax4.transAxes, ha='center', va='center',
                 fontsize=10, family='monospace')
    
    plt.tight_layout()
    plt.show()
    
    # مخرجات طرفية
    print(f"✅ وضوح الأهداب: {visibility:.1%}")
    print(f"📏 تباعد المحاكاة: {sim_spacing_mm:.2f} مم")
    if physical_mode == 'Electron':
        print(f"⏱️ زمن طيران الإلكترون: {L/v_mean*1e9:.2f} نانوثانية")
    elif physical_mode == 'Photon':
        print(f"⏱️ زمن طيران الفوتون: {L/c*1e9:.2f} نانوثانية")
    else:
        print("⏱️ زمن الطيران: يختلف حسب اللون (≈ 7.3 نانوثانية للضوء)")

display(export_button, export_output)
run_lab_ar
