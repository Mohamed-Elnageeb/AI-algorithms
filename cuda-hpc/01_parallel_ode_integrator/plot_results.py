"""Plot CPU (1 core), CPU (all cores), and GPU timings from results.csv.

Run from this project folder after running benchmark.exe:
    python plot_results.py
Writes benchmark.png.
"""
import csv
import math
import os

import matplotlib
matplotlib.use("Agg")  # no display needed, just write a file
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))


def load(path):
    meta, rows = {}, []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):                       # "# key,value" metadata
                key, val = line[1:].strip().split(",", 1)
                meta[key] = val
            elif line.startswith("n,"):                     # column header
                continue
            else:
                parts = line.split(",")
                # n, cpu1_ms, cpu_par_ms, gpu_ms, ...
                rows.append((int(parts[0]), float(parts[1]),
                             float(parts[2]), float(parts[3])))
    return meta, rows


def crossover_n(ns, slower, faster):
    """First n where `faster` beats `slower`, refined in log space."""
    for i in range(1, len(ns)):
        d0 = slower[i - 1] - faster[i - 1]
        d1 = slower[i] - faster[i]
        if d0 <= 0 and d1 > 0:  # faster overtakes between these points
            t = -d0 / (d1 - d0)
            log_n = math.log10(ns[i - 1]) + t * (math.log10(ns[i]) - math.log10(ns[i - 1]))
            return 10 ** log_n
    return None


def main():
    meta, rows = load(os.path.join(HERE, "results.csv"))
    ns      = [r[0] for r in rows]
    cpu1    = [r[1] for r in rows]
    cpu_par = [r[2] for r in rows]
    gpu     = [r[3] for r in rows]

    threads = meta.get("cpu_threads", "?")

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(ns, cpu1, "o-", color="#d62728", label="CPU (1 core)")
    ax.plot(ns, cpu_par, "^-", color="#ff7f0e", label=f"CPU ({threads} threads)")
    ax.plot(ns, gpu, "s-", color="#2ca02c",
            label=f"GPU ({meta.get('gpu_name', 'GPU')})")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("number of oscillators (n)")
    ax.set_ylabel("time per run (ms)")
    ax.set_title("Batched ODE integration: CPU vs GPU")
    ax.grid(True, which="both", alpha=0.3)

    # Mark where the GPU overtakes the single-core CPU. (We use the 1-core
    # baseline for the marker because the parallel-CPU line is dominated by
    # thread-launch overhead at tiny n, so its crossover is not meaningful.)
    xover = crossover_n(ns, cpu1, gpu)
    if xover:
        ax.axvline(xover, ls="--", color="gray", alpha=0.7)
        ax.annotate(f"GPU overtakes CPU (1 core)\n≈ n = {xover:,.0f}",
                    xy=(xover, min(gpu)), xytext=(xover * 1.5, min(gpu) * 6),
                    fontsize=9, color="gray",
                    arrowprops=dict(arrowstyle="->", color="gray"))

    # Headline speedups at the largest n, where the hardware is saturated.
    big = max(range(len(ns)), key=lambda i: ns[i])
    peak = (f"at n = {ns[big]:,}:\n"
            f"  GPU is {cpu1[big] / gpu[big]:.0f}x faster than 1 core\n"
            f"  GPU is {cpu_par[big] / gpu[big]:.0f}x faster than {threads} threads")
    ax.text(0.98, 0.30, peak, transform=ax.transAxes, ha="right", va="top",
            fontsize=9, family="monospace",
            bbox=dict(boxstyle="round", fc="#f5f5f5", ec="gray", alpha=0.95))

    specs = (
        f"GPU: {meta.get('gpu_name', '?')}\n"
        f"   {meta.get('gpu_sms', '?')} SMs · {meta.get('gpu_cores', '?')} CUDA cores\n"
        f"CPU: {threads} logical cores\n"
        f"steps/run: {meta.get('num_steps', '?')}"
    )
    ax.text(0.02, 0.98, specs, transform=ax.transAxes, va="top", fontsize=9,
            family="monospace",
            bbox=dict(boxstyle="round", fc="white", ec="gray", alpha=0.9))

    ax.legend(loc="lower right")
    fig.tight_layout()
    out = os.path.join(HERE, "benchmark.png")
    fig.savefig(out, dpi=130)
    print("wrote", out)

    xover1 = crossover_n(ns, cpu1, gpu)
    if xover1:
        print(f"GPU beats 1-core CPU at about   n = {xover1:,.0f}")
    if xover:
        print(f"GPU beats {threads}-thread CPU at about n = {xover:,.0f}")


if __name__ == "__main__":
    main()
