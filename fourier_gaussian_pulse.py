import numpy as np
import scipy.integrate as spi
import matplotlib.pyplot as plt
from dataclasses import dataclass
from pathlib import Path

"""
Fourier approximation of Gaussian pulse trains.

This script studies how the number of Fourier terms required for a good
approximation depends on the ratio P / delta_t.
"""

# =============================================================================
# Configuration
# =============================================================================

@dataclass
class SimulationConfig:
    t_start: float = -3.0
    t_end: float = 6.0
    resolution: int = 10_000

    period: float = 3.0
    ratio: float = 50.0  # P / delta_t

    min_terms: int = 5
    max_terms: int = 30
    step: int = 5

    error_tolerance: float = 0.005

    save_figures: bool = False
    output_dir: str = "figures"

    @property
    def delta_t(self):
        return self.period / self.ratio


# =============================================================================
# Signal definition
# =============================================================================

def gaussian(t, center, width):
    """Gaussian pulse centered at `center` with width `width`."""
    return np.exp(-((t - center) / width) ** 2)


def gaussian_pulse_train(t, period, width):
    """Gaussian pulse train over three consecutive periods."""
    centers = [-period / 2, period / 2, 3 * period / 2]

    signal = np.zeros_like(t, dtype=float)

    for center in centers:
        signal += gaussian(t, center, width)

    return signal


# =============================================================================
# Fourier series
# =============================================================================

def compute_fourier_coefficients(func, period, n_terms):
    """Compute Fourier coefficients a_n and b_n up to n_terms."""
    coefficients = np.zeros((n_terms + 1, 2))

    for n in range(n_terms + 1):
        a_n = (2 / period) * spi.quad(
            lambda t: func(t) * np.cos(2 * np.pi * n * t / period),
            0,
            period
        )[0]

        b_n = (2 / period) * spi.quad(
            lambda t: func(t) * np.sin(2 * np.pi * n * t / period),
            0,
            period
        )[0]

        coefficients[n] = [a_n, b_n]

    return coefficients


def reconstruct_fourier_series(t, coefficients, period):
    """Reconstruct a signal from its Fourier coefficients."""
    series = np.full_like(t, coefficients[0, 0] / 2, dtype=float)

    for n in range(1, len(coefficients)):
        a_n, b_n = coefficients[n]

        series += (
            a_n * np.cos(2 * np.pi * n * t / period)
            + b_n * np.sin(2 * np.pi * n * t / period)
        )

    return series


# =============================================================================
# Error metrics
# =============================================================================

def max_absolute_error(original, approximation):
    """Maximum absolute error."""
    return np.max(np.abs(original - approximation))


def mean_squared_error(original, approximation):
    """Mean squared error."""
    return np.mean((original - approximation) ** 2)


def relative_l2_error(original, approximation):
    """Relative L2 error."""
    numerator = np.linalg.norm(original - approximation)
    denominator = np.linalg.norm(original)

    if denominator == 0:
        return np.inf

    return numerator / denominator


# =============================================================================
# Analysis
# =============================================================================

def analyze_fourier_approximation(config):
    """Compute Fourier approximations and errors."""
    t_values = np.linspace(config.t_start, config.t_end, config.resolution)

    def signal(t):
        return gaussian_pulse_train(t, config.period, config.delta_t)

    original_signal = signal(t_values)

    results = []

    for n_terms in range(config.min_terms, config.max_terms + 1, config.step):
        coefficients = compute_fourier_coefficients(
            signal,
            config.period,
            n_terms
        )

        approximation = reconstruct_fourier_series(
            t_values,
            coefficients,
            config.period
        )

        max_error = max_absolute_error(original_signal, approximation)
        mse = mean_squared_error(original_signal, approximation)
        rel_l2 = relative_l2_error(original_signal, approximation)

        results.append({
            "n_terms": n_terms,
            "coefficients": coefficients,
            "approximation": approximation,
            "max_error": max_error,
            "mse": mse,
            "relative_l2_error": rel_l2,
        })

    return t_values, original_signal, results


def find_sufficient_terms(results, tolerance):
    """Find the first number of terms below the error tolerance."""
    for result in results:
        if result["max_error"] < tolerance:
            return result["n_terms"]

    return None


# =============================================================================
# Plotting
# =============================================================================

def plot_approximations(t_values, original_signal, results, config):
    """Plot original signal against several Fourier approximations."""
    n_plots = len(results)
    cols = 2
    rows = int(np.ceil(n_plots / cols))

    fig, axes = plt.subplots(rows, cols, figsize=(12, 4 * rows))
    axes = np.array(axes).flatten()

    fig.suptitle(
        f"Fourier approximation of a Gaussian pulse train\n"
        f"P = {config.period}, P/Δt = {config.ratio}",
        fontsize=14
    )

    for index, result in enumerate(results):
        ax = axes[index]

        ax.plot(t_values, original_signal, label="Original signal")
        ax.plot(
            t_values,
            result["approximation"],
            label="Fourier approximation"
        )

        ax.set_title(
            f"N = {result['n_terms']} | "
            f"Max error = {result['max_error']:.4f}"
        )

        ax.set_xlabel("t")
        ax.set_ylabel("f(t)")
        ax.grid(True)
        ax.legend()

    for index in range(len(results), len(axes)):
        axes[index].axis("off")

    plt.tight_layout()

    return fig


def plot_error_evolution(results, config):
    """Plot approximation error as a function of Fourier terms."""
    n_terms = [result["n_terms"] for result in results]
    max_errors = [result["max_error"] for result in results]
    mse_errors = [result["mse"] for result in results]
    relative_errors = [result["relative_l2_error"] for result in results]

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(n_terms, max_errors, marker="o", label="Max absolute error")
    ax.plot(n_terms, mse_errors, marker="o", label="Mean squared error")
    ax.plot(n_terms, relative_errors, marker="o", label="Relative L2 error")

    ax.axhline(
        config.error_tolerance,
        linestyle="--",
        label=f"Tolerance = {config.error_tolerance}"
    )

    ax.set_title("Error evolution with Fourier terms")
    ax.set_xlabel("Number of Fourier terms")
    ax.set_ylabel("Error")
    ax.grid(True)
    ax.legend()

    plt.tight_layout()

    return fig


def save_figure(fig, filename, config):
    """Save a matplotlib figure if enabled in the config."""
    if not config.save_figures:
        return

    output_path = Path(config.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    fig.savefig(output_path / filename, dpi=300)


# =============================================================================
# Main
# =============================================================================

def main():
    config = SimulationConfig(
        ratio=50,
        min_terms=5,
        max_terms=30,
        step=5,
        error_tolerance=0.005,
        save_figures=False
    )

    t_values, original_signal, results = analyze_fourier_approximation(config)

    sufficient_terms = find_sufficient_terms(
        results,
        config.error_tolerance
    )

    if sufficient_terms is None:
        print("No sufficient approximation found.")
        print(f"Last max error: {results[-1]['max_error']:.6f}")
    else:
        print(f"Sufficient number of terms: {sufficient_terms}")

    print("\nError summary:")
    for result in results:
        print(
            f"N = {result['n_terms']:>3} | "
            f"max error = {result['max_error']:.6f} | "
            f"MSE = {result['mse']:.6e} | "
            f"relative L2 = {result['relative_l2_error']:.6f}"
        )

    fig_approx = plot_approximations(
        t_values,
        original_signal,
        results,
        config
    )

    fig_error = plot_error_evolution(results, config)

    save_figure(fig_approx, "fourier_approximations.png", config)
    save_figure(fig_error, "error_evolution.png", config)

    plt.show()


if __name__ == "__main__":
    main()