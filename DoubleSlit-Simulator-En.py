# -*- coding: utf-8 -*-
"""
Berramdane Model V12.1 – Complete English Version
Author : Al Moalim Berramdane
License: CC BY 4.0

A professional interactive simulation of the double‑slit experiment for:
- Electrons (de Broglie wavelength)
- Monochromatic photons
- White light (RGB mixing)

Features complementarity principle (gradual which‑path measurement),
Jönsson 1961 validation table, full parameter control, and CSV export.
"""

import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import interact, FloatSlider, Checkbox, IntSlider, Dropdown, Button, Output
from scipy.signal import find_peaks
import pandas as pd
from IPython.display import display
import warnings
warnings.filterwarnings('ignore')

# ========================= CONSTANTS =========================
h = 6.626e-34          # Planck constant (J·s)
m = 9.109e-31          # Electron mass (kg)
c = 3e8                # Speed of light (m/s)

# Jönsson 1961 reference values (for electrons)
REF_SPACING_MM = 0.18   # Fringe spacing & first minimum (mm)
REF_V = 70000.0         # Electron velocity (m/s)
REF_A = 0.3e-6          # Slit width (m)
REF_D = 1.0e-6          # Slit separation (m)

# ========================= CORE PHYSICS =========================
def de_broglie_wavelength(v):
    """Compute de Broglie wavelength from velocity"""
    return h / (m * v)

def double_slit_intensity_by_wavelength(x, wavelength, L, a_width, d_slit):
    """
    Intensity pattern for a given wavelength.
    Combines double‑slit interference and single‑slit diffraction.
    """
    beta = (np.pi * d_slit * x) / (wavelength * L)
    interference = np.cos(beta)**2
    alpha = (np.pi * a_width * x) / (wavelength * L)
    envelope = np.sinc(alpha / np.pi)**2
    return interference * envelope

def double_slit_intensity_with_spread(x, v_mean, delta_v, L, a_width, d_slit, n_samples=100):
    """
    Intensity pattern averaged over a Gaussian velocity distribution.
    Simulates thermal / energy spread.
    """
    velocities = np.random.normal(v_mean, delta_v, n_samples)
    total = np.zeros_like(x)
    for v in velocities:
        lam = de_broglie_wavelength(v)
        total += double_slit_intensity_by_wavelength(x, lam, L, a_width, d_slit)
    return total / n_samples

def particle_like_pattern(x, wavelength, L, a_width, d_slit):
    """
    Particle‑like pattern when which‑path information is fully known.
    Two Gaussian peaks centered behind each slit.
    """
    sigma = a_width * L / wavelength
    I_left = np.exp(-(x + d_slit/2)**2 / (2 * sigma**2))
    I_right = np.exp(-(x - d_slit/2)**2 / (2 * sigma**2))
    return 0.5 * (I_left + I_right)

def compute_visibility(x, I):
    """Calculate fringe visibility (contrast) from the intensity pattern."""
    peaks, _ = find_peaks(I, distance=len(x)//30)
    if len(peaks) < 2:
        return 0.0
    I_max = np.max(I[peaks])
    center_idx = np.argmin(np.abs(x))
    search = np.where(np.abs(x - x[center_idx]) < 5e-3)[0]
    I_min = np.min(I[search]) if len(search) > 0 else np.min(I)
    return (I_max - I_min) / (I_max + I_min) if (I_max + I_min) > 0 else 0

def white_light_pattern_rgb(x, L, a_width, d_slit):
    """
    White light simulation: mix red (650 nm), green (532 nm), blue (450 nm).
    Returns normalised intensity for each colour channel.
    """
    lam_R, lam_G, lam_B = 650e-9, 532e-9, 450e-9
    I_R = double_slit_intensity_by_wavelength(x, lam_R, L, a_width, d_slit)
    I_G = double_slit_intensity_by_wavelength(x, lam_G, L, a_width, d_slit)
    I_B = double_slit_intensity_by_wavelength(x, lam_B, L, a_width, d_slit)
    max_val = max(np.max(I_R), np.max(I_G), np.max(I_B))
    if max_val > 0:
        I_R, I_G, I_B = I_R/max_val, I_G/max_val, I_B/max_val
    return I_R, I_G, I_B

# ========================= CSV EXPORT BUTTON =========================
current_x, current_I = None, None
export_button = Button(description="📥 Download CSV Data", button_style='success')
export_output = Output()

def on_export_clicked(b):
    global current_x, current_I
    with export_output:
        export_output.clear_output()
        if current_x is not None and current_I is not None:
            df = pd.DataFrame({'Position_mm': current_x * 1000, 'Intensity': current_I})
            df.to_csv('berramdane_double_slit_data.csv', index=False)
            print("✅ Data exported successfully to berramdane_double_slit_data.csv")
        else:
            print("❌ No data to export. Run the simulation first.")
export_button.on_click(on_export_clicked)

# ========================= INTERACTIVE USER INTERFACE =========================
@interact(
    mode=Dropdown(options=['Electron (de Broglie)', 'Photon (monochromatic)', 'White light (RGB)'],
                  value='Electron (de Broglie)', description='Simulation mode'),
    L_mm=FloatSlider(value=350, min=10, max=1000, step=5, description='Distance L (mm)', continuous_update=False),
    v_mean=FloatSlider(value=REF_V, min=20000, max=150000, step=1000, description='Electron velocity (m/s)', continuous_update=False),
    delta_v=FloatSlider(value=0.0, min=0.0, max=20000, step=1000, description='Velocity spread Δv (m/s)', continuous_update=False),
    wavelength_nm=FloatSlider(value=532, min=380, max=750, step=1, description='Wavelength (nm)', continuous_update=False),
    a_width=FloatSlider(value=REF_A, min=0.1e-6, max=2.0e-6, step=0.01e-6, description='Slit width (m)', continuous_update=False),
    d_slit=FloatSlider(value=REF_D, min=0.1e-6, max=2.0e-6, step=0.01e-6, description='Slit separation (m)', continuous_update=False),
    observer_active=Checkbox(value=False, description='Which‑path detector ON'),
    meas_strength=FloatSlider(value=0.0, min=0.0, max=1.0, step=0.05, description='Measurement strength'),
    temperature=FloatSlider(value=0.0, min=0, max=1000, step=10, description='Detector noise (K)', continuous_update=False),
    show_buildup=Checkbox(value=False, description='Temporal buildup'),
    n_particles=IntSlider(value=300, min=50, max=1000, step=50, description='Number of particles')
)
def run_lab(mode, L_mm, v_mean, delta_v, wavelength_nm, a_width, d_slit,
            observer_active, meas_strength, temperature, show_buildup, n_particles):
    
    global current_x, current_I
    L = L_mm / 1000.0   # convert mm → m
    
    # Determine physical mode and effective wavelength
    if 'Electron' in mode:
        phys_mode = 'Electron'
        lam = de_broglie_wavelength(v_mean)
    elif 'Photon' in mode:
        phys_mode = 'Photon'
        lam = wavelength_nm * 1e-9
    else:  # White light
        phys_mode = 'White'
        lam = 532e-9   # central wavelength for range estimation
    
    # Dynamic x‑range (ensures at least 3 visible fringes)
    spacing = lam * L / d_slit
    x_limit = max(0.002, 3 * spacing)
    x = np.linspace(-x_limit, x_limit, 1500)
    current_x = x
    
    # ---- Interference pattern ----
    if phys_mode == 'Electron' and delta_v > 0:
        I_interf = double_slit_intensity_with_spread(x, v_mean, delta_v, L, a_width, d_slit, n_samples=80)
    elif phys_mode == 'White':
        I_R, I_G, I_B = white_light_pattern_rgb(x, L, a_width, d_slit)
        I_interf = (I_R + I_G + I_B) / 3.0
    else:
        I_interf = double_slit_intensity_by_wavelength(x, lam, L, a_width, d_slit)
    
    # ---- Particle‑like pattern (two‑peak) ----
    if phys_mode == 'White':
        I_particle = particle_like_pattern(x, 532e-9, L, a_width, d_slit)
    else:
        I_particle = particle_like_pattern(x, lam, L, a_width, d_slit)
    
    # ---- Complementarity (observer effect) ----
    if observer_active:
        I = (1 - meas_strength) * I_interf + meas_strength * I_particle
    else:
        I = I_interf
    
    # ---- Temporal buildup (optional) ----
    if show_buildup and n_particles > 0:
        cumulative = np.zeros_like(x)
        for _ in range(n_particles):
            if phys_mode == 'Electron' and delta_v > 0:
                I_one = double_slit_intensity_with_spread(x, v_mean, delta_v, L, a_width, d_slit, n_samples=20)
            elif phys_mode == 'White':
                I_R1, I_G1, I_B1 = white_light_pattern_rgb(x, L, a_width, d_slit)
                I_one = (I_R1 + I_G1 + I_B1) / 3.0
            else:
                I_one = double_slit_intensity_by_wavelength(x, lam, L, a_width, d_slit)
            if observer_active:
                I_one = (1 - meas_strength) * I_one + meas_strength * I_particle
            cumulative += I_one
        I = cumulative / n_particles
    
    # ---- Detector noise ----
    if temperature > 0:
        noise = (temperature / 1000.0) * 0.15 * np.max(I)
        I += np.random.normal(0, noise, len(I))
        I = np.maximum(I, 0)
    
    if np.max(I) > 0:
        I /= np.max(I)
    current_I = I
    
    # ---- Compute observables ----
    visibility = compute_visibility(x, I)
    sim_spacing_mm = spacing * 1000
    sim_first_min_mm = (lam * L / a_width) * 1000
    
    # Error relative to Jönsson 1961 (capped at 999% for readability)
    if phys_mode == 'Electron':
        err_spacing = min(999, abs(sim_spacing_mm - REF_SPACING_MM) / REF_SPACING_MM * 100)
        err_min = min(999, abs(sim_first_min_mm - REF_SPACING_MM) / REF_SPACING_MM * 100)
    else:
        err_spacing = err_min = 0  # only used in electron mode
    
    # ========================= PLOTTING =========================
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    ax1, ax2, ax3, ax4 = axes[0,0], axes[0,1], axes[1,0], axes[1,1]
    
    # --- Main interference pattern ---
    ax1.plot(x*1000, I, 'b-', lw=1.5)
    ax1.fill_between(x*1000, I, alpha=0.3)
    title = f'{mode} | Visibility = {visibility:.1%} | L = {L_mm} mm'
    if observer_active:
        title += f' | Measurement strength = {meas_strength:.2f}'
    if phys_mode == 'Electron' and delta_v > 0:
        title += f' | Δv = {delta_v/1e3:.0f} km/s'
    if temperature > 0:
        title += f' | Noise = {temperature:.0f} K'
    ax1.set_title(title)
    ax1.set_xlabel('Position (mm)')
    ax1.set_ylabel('Intensity')
    ax1.set_xlim(-x_limit*1000, x_limit*1000)
    ax1.grid(alpha=0.3)
    
    # --- Detector screen (coloured for white light) ---
    if phys_mode == 'White':
        I_R, I_G, I_B = white_light_pattern_rgb(x, L, a_width, d_slit)
        screen_rgb = np.zeros((150, len(x), 3))
        screen_rgb[:,:,0] = np.tile(I_R, (150, 1))
        screen_rgb[:,:,1] = np.tile(I_G, (150, 1))
        screen_rgb[:,:,2] = np.tile(I_B, (150, 1))
        ax2.imshow(screen_rgb, aspect='auto', extent=[-x_limit*1000, x_limit*1000, 0, 1])
    else:
        screen = np.tile(I, (150, 1))
        im = ax2.imshow(screen, cmap='hot', aspect='auto', extent=[-x_limit*1000, x_limit*1000, 0, 1])
        plt.colorbar(im, ax=ax2, label='Intensity', shrink=0.8)
    ax2.set_title('Detector screen')
    ax2.set_xlabel('Position (mm)')
    ax2.set_yticks([])
    
    # --- Complementarity comparison ---
    I_interf_norm = I_interf / np.max(I_interf) if np.max(I_interf) > 0 else I_interf
    I_particle_norm = I_particle / np.max(I_particle) if np.max(I_particle) > 0 else I_particle
    ax3.plot(x*1000, I_interf_norm, 'b--', lw=1, alpha=0.7, label='Pure wave (interference)')
    ax3.plot(x*1000, I_particle_norm, 'r--', lw=1, alpha=0.7, label='Pure particle (which‑path)')
    ax3.plot(x*1000, I, 'k-', lw=2, label='Current state')
    ax3.set_xlim(-x_limit*1000, x_limit*1000)
    ax3.set_ylim(0, 1.05)
    ax3.set_title('Complementarity principle (Bohr)')
    ax3.set_xlabel('Position (mm)')
    ax3.set_ylabel('Normalized intensity')
    ax3.legend(fontsize=8, loc='upper right')
    ax3.grid(alpha=0.3)
    
    # --- Bottom‑right panel: comparison table (English only) ---
    ax4.axis('off')
    if phys_mode == 'Electron':
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
        table.scale(1.3, 1.8)
        for (i, j), cell in table.get_celld().items():
            if i == 0:
                cell.set_facecolor('#dddddd')
                cell.set_text_props(weight='bold')
        footnote = (
            "Note: Reference values from Jönsson (1961) for electrons at 70 km/s,\n"
            "slit width 0.3 µm, separation 1.0 µm. Adjust L (distance) to reduce error."
        )
        ax4.text(0.5, 0.08, footnote, transform=ax4.transAxes, ha='center', va='bottom',
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
    
    # ---- Console output ----
    print(f"✅ Visibility: {visibility:.1%}")
    print(f"📏 Simulated fringe spacing: {sim_spacing_mm:.2f} mm")
    if phys_mode == 'Electron':
        print(f"⏱️ Electron flight time: {L/v_mean*1e9:.2f} ns")
    elif phys_mode == 'Photon':
        print(f"⏱️ Photon flight time: {L/c*1e9:.2f} ns")
    else:
        print("⏱️ Flight time: varies by colour (≈ 7.3 ns for visible light)")

# Display the interactive controls and the export button
display(export_button, export_output)
run_lab
