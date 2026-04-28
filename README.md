
markdown
![Berramdane Model Result](images/Result-v12.1-ar.png)
markdown
![Berramdane Model Result](images/Result-v12.1-en.png)


# Double‑Slit Quantum Simulator | محاكاة الشق المزدوج الكمي

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YOUR_USERNAME/DoubleSlit-Quantum-Simulator/blob/main/DoubleSlit_Simulator_EN.ipynb)

**Interactive educational tool** for Young's double‑slit experiment with electrons, photons, and white light. Features complementarity principle, real‑time parameter tuning, and experimental validation against Jönsson (1961).

أداة تعليمية تفاعلية لتجربة الشق المزدوج للإلكترونات والضوء، مع مبدأ التكاملية، تحكم فوري بالمتحولات، وتحقق علمي من تجربة Jönsson 1961.

## ✨ Features | الميزات
- Three modes: **Electron** (de Broglie), **Photon** (monochromatic), **White light** (RGB mixing)
- **Complementarity slider**: gradual transition from interference to particle‑like pattern
- **Distance control L (mm)** to calibrate with real experiments
- **Jönsson 1961 validation** table (error %)
- **CSV Export** for further analysis
- Fully interactive (sliders, checkboxes) – runs in Colab / Jupyter

## 🚀 Quick Start | التشغيل السريع

### 🇬🇧 English version:
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YOUR_USERNAME/DoubleSlit-Quantum-Simulator/blob/main/DoubleSlit_Simulator_EN.ipynb)

### 🇸🇦 النسخة العربية:
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YOUR_USERNAME/DoubleSlit-Quantum-Simulator/blob/main/DoubleSlit_Simulator_AR.ipynb)

## 🧪 Validation | التحقق العلمي
Default settings match **Jönsson (1961)** electron experiment:  
`v = 70 000 m/s`, `a = 0.3 µm`, `d = 1.0 µm`, `L = 35 cm` → fringe spacing ≈ 0.18 mm.

## 📦 Requirements | المتطلبات
```bash
numpy, matplotlib, ipywidgets, scipy, pandas
