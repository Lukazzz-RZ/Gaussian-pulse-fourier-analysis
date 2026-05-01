# Gaussian Pulse Fourier Analysis

## 📌 Introduction

This project explores the numerical approximation of Gaussian pulse trains using Fourier series.

The main objective is to analyze how the number of Fourier terms required for an accurate reconstruction depends on the ratio:

[
\frac{P}{\Delta t}
]

where:

* (P) is the signal period
* (\Delta t) is the width of the Gaussian pulse

The study focuses on time-domain reconstruction and error analysis.

---

## 📊 Fourier series approximation

The Fourier series of the signal is computed numerically, and the approximation is compared with the original Gaussian pulse train.

### Observations:

* For a fixed period, narrower Gaussian pulses (smaller (\Delta t)) require more Fourier terms.
* The approximation improves progressively as higher-frequency components are included.

### Example:

![Fourier approximation](figures/fourier_approximations.png)

The figure shows how the approximation converges as the number of terms increases.

---

## 📉 Convergence analysis

The approximation error is evaluated using different metrics:

* Maximum absolute error
* Mean squared error
* Relative (L^2) error

![Error evolution](figures/error_evolution.png)

### Observations:

1. The error decreases as more Fourier terms are included.
2. Convergence is slower for narrower pulses due to their higher frequency content.

---

## 📈 Results

Empirically, the number of terms required for a good approximation follows:

[
m \approx \frac{P}{2 \Delta t}
]

### Example values:

| (P/\Delta t) | Required Fourier terms |
| ------------ | ---------------------- |
| 10           | 5                      |
| 20           | 10                     |
| 30           | 15                     |
| 40           | 20                     |
| 50           | 25                     |

---

## 🧪 Signal behavior

Gaussian pulse trains with different widths illustrate the relationship between time-domain localization and spectral complexity:

![Pulse width comparison](figures/pulse_width_comparison.png)

### Observations:

* Narrow pulses → broader frequency spectrum → more Fourier terms required
* Wider pulses → smoother signal → fewer terms needed

---

## ⚙️ Usage

Install dependencies:

```bash
pip install numpy scipy matplotlib
```

Run the script:

```bash
python fourier_gaussian_pulse.py
```

---

## 📁 Project structure

```
.
├── fourier_gaussian_pulse.py
├── figures/
│   ├── fourier_approximations.png
│   ├── error_evolution.png
│   └── pulse_width_comparison.png
└── README.md
```

---

## 🏁 Conclusion

The accuracy of the Fourier approximation is governed primarily by the ratio (P / \Delta t), rather than by the absolute period.

This reflects a fundamental property of Fourier analysis:

> The spectral complexity of a signal is determined by its time-domain localization.

This project provides a simple numerical framework to visualize and understand this relationship.
