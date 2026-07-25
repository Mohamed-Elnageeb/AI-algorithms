"""Plot benchmark results from results.csv, then open the main graph.

Produces two figures next to this script:
  - benchmark.png          : Euler — CPU vs GPU-total vs GPU-kernel-only
  - speedup_comparison.png : Euler vs RK4 speedup as n grows

Run from anywhere (benchmark.exe calls this automatically):
    python plot_results.py
"""
import math
import os
import subprocess
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))


def load(path):
    meta, by_method = {}, {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                key, val = line[1:].strip().split(",", 1)
                meta[key] = val
            elif line.startswith("method,"):
                continue
            else:
                method, n, cpu, gpu, kernel, speedup, match = line.split(",")
                by_method.setdefault(method, []).append(
                    (int(n), float(cpu), float(gpu), float(kernel)))
    return meta, by_method


def crossover_n(ns, slow, fast):
    for i in range(1, len(ns)):
        d0, d1 = slow[i - 1] - fast[i - 1], slow[i] - fast[i]
        if d0 <= 0 and d1 > 0:
            t = d0 / (d0 - d1)
            log_n = math.log10(ns[i - 1]) + t * (math.log10(ns[i]) - math.log10(ns[i - 1]))
            return 10 ** log_n
    return None


def open_image(path):
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.run(["open", path], check=False)
        else:
            subprocess.run(["xdg-open", path], check=False)
    except Exception:
        pass


def plot_main(meta, rows):
    """Euler: CPU vs GPU-total vs GPU-kernel-only."""
    ns     = [r[0] for r in rows]
    cpu    = [r[1] for r in rows]
    gpu    = [r[2] for r in rows]
    kernel = [r[3] for r in rows]

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(ns, cpu,    "o-", color="#d62728", label="CPU (1 core)")
    ax.plot(ns, gpu,    "s-", color="#2ca02c", label="GPU total (compute + transfer)")
    ax.plot(ns, kernel, "^--", color="#1f77b4", label="GPU kernel only (compute)")

    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("number of oscillators (n)")
    ax.set_ylabel("time per run (ms)")
    ax.set_title("Batched ODE integration (Euler): CPU vs GPU")
    ax.grid(True, which="both", alpha=0.3)

    xover = crossover_n(ns, cpu, gpu)
    if xover:
        ax.axvline(xover, ls="--", color="gray", alpha=0.6)
        ax.annotate(f"GPU overtakes CPU\n≈ n = {xover:,.0f}",
                    xy=(xover, min(kernel)), xytext=(xover * 1.6, min(kernel) * 10),
                    fontsize=9, color="gray",
                    arrowprops=dict(arrowstyle="->", color="gray"))

    big = max(range(len(ns)), key=lambda i: ns[i])
    ax.text(0.98, 0.30,
            f"at n = {ns[big]:,}:\n"
            f"  GPU {cpu[big] / gpu[big]:.0f}x faster than CPU\n"
            f"  transfer = {gpu[big] - kernel[big]:.1f} ms of {gpu[big]:.1f} ms total",
            transform=ax.transAxes, ha="right", va="top",
            fontsize=9, family="monospace",
            bbox=dict(boxstyle="round", fc="#f5f5f5", ec="gray", alpha=0.95))

    specs = (f"GPU: {meta.get('gpu_name', '?')}\n"
             f"   {meta.get('gpu_sms', '?')} SMs · {meta.get('gpu_cores', '?')} CUDA cores\n"
             f"CPU: 1 of {meta.get('cpu_threads', '?')} logical cores\n"
             f"steps/run: {meta.get('num_steps', '?')}")
    ax.text(0.02, 0.98, specs, transform=ax.transAxes, va="top", fontsize=9,
            family="monospace",
            bbox=dict(boxstyle="round", fc="white", ec="gray", alpha=0.9))

    ax.legend(loc="lower right")
    fig.tight_layout()
    out = os.path.join(HERE, "benchmark.png")
    fig.savefig(out, dpi=130)
    print("wrote", out)
    return out


def plot_speedup(by_method):
    """Speedup vs n, one line per method (Euler vs RK4)."""
    fig, ax = plt.subplots(figsize=(9, 6))
    colors = {"euler": "#2ca02c", "rk4": "#9467bd"}
    for method, rows in by_method.items():
        ns  = [r[0] for r in rows]
        spd = [r[1] / r[2] for r in rows]   # cpu / gpu_total
        ax.plot(ns, spd, "o-", color=colors.get(method, None),
                label=f"{method.upper()} speedup")

    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("number of oscillators (n)")
    ax.set_ylabel("speedup (CPU 1 core / GPU)")
    ax.set_title("Euler vs RK4 GPU speedup: more math helps until the kernel dominates")
    ax.grid(True, which="both", alpha=0.3)
    ax.axhline(1.0, ls=":", color="gray", alpha=0.7)
    ax.legend(loc="upper left")
    fig.tight_layout()
    out = os.path.join(HERE, "speedup_comparison.png")
    fig.savefig(out, dpi=130)
    print("wrote", out)


def main():
    meta, by_method = load(os.path.join(HERE, "results.csv"))
    main_png = None
    if "euler" in by_method:
        main_png = plot_main(meta, by_method["euler"])
    if len(by_method) > 1:
        plot_speedup(by_method)
    if main_png:
        open_image(main_png)


if __name__ == "__main__":
    main()
