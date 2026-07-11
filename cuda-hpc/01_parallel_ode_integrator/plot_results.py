"""Plot CPU vs GPU timings from results.csv into benchmark.png, then open it.

Run from this project folder (benchmark.exe does this automatically):
    python plot_results.py
"""
import csv
import math
import os
import subprocess
import sys

import matplotlib
matplotlib.use("Agg")  # render to a file; we open it ourselves afterwards
import matplotlib.pyplot as plt


def load(path):
    meta, rows = {}, []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):                  # "# key,value" metadata
                key, val = line[1:].strip().split(",", 1)
                meta[key] = val
            elif line.startswith("n,"):                # column header
                continue
            else:
                parts = line.split(",")
                rows.append((int(parts[0]), float(parts[1]), float(parts[2])))
    return meta, rows


def crossover_n(ns, slow, fast):
    """First n where `fast` overtakes `slow`, refined by log-log interpolation."""
    for i in range(1, len(ns)):
        d0, d1 = slow[i - 1] - fast[i - 1], slow[i] - fast[i]
        if d0 <= 0 and d1 > 0:  # slow-minus-fast crosses zero => fast pulls ahead
            t = d0 / (d0 - d1)
            log_n = math.log10(ns[i - 1]) + t * (math.log10(ns[i]) - math.log10(ns[i - 1]))
            return 10 ** log_n
    return None


def open_image(path):
    """Open the PNG in the OS default viewer (best-effort; never fatal)."""
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.run(["open", path], check=False)
        else:
            subprocess.run(["xdg-open", path], check=False)
    except Exception:
        pass  # headless / no viewer -> the PNG is still written


def main():
    meta, rows = load("results.csv")
    ns  = [r[0] for r in rows]
    cpu = [r[1] for r in rows]
    gpu = [r[2] for r in rows]

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(ns, cpu, "o-", color="#d62728", label="CPU (1 core)")
    ax.plot(ns, gpu, "s-", color="#2ca02c",
            label=f"GPU ({meta.get('gpu_name', 'GPU')})")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("number of oscillators (n)")
    ax.set_ylabel("time per run (ms)")
    ax.set_title("Batched ODE integration: CPU vs GPU")
    ax.grid(True, which="both", alpha=0.3)

    xover = crossover_n(ns, cpu, gpu)
    if xover:
        ax.axvline(xover, ls="--", color="gray", alpha=0.7)
        ax.annotate(f"GPU overtakes CPU\n≈ n = {xover:,.0f}",
                    xy=(xover, min(gpu)), xytext=(xover * 1.6, min(gpu) * 8),
                    fontsize=9, color="gray",
                    arrowprops=dict(arrowstyle="->", color="gray"))

    # Headline speedup at the largest n, where the hardware is saturated.
    big = max(range(len(ns)), key=lambda i: ns[i])
    ax.text(0.98, 0.28,
            f"at n = {ns[big]:,}:\n  GPU is {cpu[big] / gpu[big]:.0f}x faster",
            transform=ax.transAxes, ha="right", va="top",
            fontsize=10, family="monospace",
            bbox=dict(boxstyle="round", fc="#f5f5f5", ec="gray", alpha=0.95))

    specs = (
        f"GPU: {meta.get('gpu_name', '?')}\n"
        f"   {meta.get('gpu_sms', '?')} SMs · {meta.get('gpu_cores', '?')} CUDA cores\n"
        f"CPU: 1 of {meta.get('cpu_threads', '?')} logical cores\n"
        f"steps/run: {meta.get('num_steps', '?')}"
    )
    ax.text(0.02, 0.98, specs, transform=ax.transAxes, va="top", fontsize=9,
            family="monospace",
            bbox=dict(boxstyle="round", fc="white", ec="gray", alpha=0.9))

    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig("benchmark.png", dpi=130)
    print("wrote benchmark.png")
    if xover:
        print(f"crossover: GPU becomes faster at about n = {xover:,.0f}")
    open_image("benchmark.png")


if __name__ == "__main__":
    main()
