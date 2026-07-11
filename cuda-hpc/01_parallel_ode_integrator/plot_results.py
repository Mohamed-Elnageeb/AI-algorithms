"""Plot CPU vs GPU timings from results.csv into benchmark.png.

Run from this project folder after running benchmark.exe:
    python plot_results.py
"""
import csv
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
                n, cpu, gpu, speedup, match = line.split(",")
                rows.append((int(n), float(cpu), float(gpu)))
    return meta, rows


def crossover_n(rows):
    """First n where the GPU is faster, refined by log-log interpolation."""
    for i in range(1, len(rows)):
        n0, cpu0, gpu0 = rows[i - 1]
        n1, cpu1, gpu1 = rows[i]
        if gpu0 >= cpu0 and gpu1 < cpu1:  # speedup crosses 1 between these points
            import math
            # interpolate where (cpu-gpu) hits zero in log(n) space
            d0, d1 = cpu0 - gpu0, cpu1 - gpu1
            t = d0 / (d0 - d1)
            log_n = math.log10(n0) + t * (math.log10(n1) - math.log10(n0))
            return 10 ** log_n
    return None


def main():
    meta, rows = load(os.path.join(HERE, "results.csv"))
    ns  = [r[0] for r in rows]
    cpu = [r[1] for r in rows]
    gpu = [r[2] for r in rows]
    xover = crossover_n(rows)

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

    if xover:
        ax.axvline(xover, ls="--", color="gray", alpha=0.7)
        ax.annotate(f"GPU overtakes CPU\n≈ n = {xover:,.0f}",
                    xy=(xover, min(gpu)), xytext=(xover * 1.3, min(gpu) * 4),
                    fontsize=9, color="gray",
                    arrowprops=dict(arrowstyle="->", color="gray"))

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
    out = os.path.join(HERE, "benchmark.png")
    fig.savefig(out, dpi=130)
    print("wrote", out)
    if xover:
        print(f"crossover: GPU becomes faster at about n = {xover:,.0f}")


if __name__ == "__main__":
    main()
