#include <cstdio>
#include <cstdlib>   // system()
#include <string>
#include <vector>
#include <chrono>
#include <cmath>
#include <algorithm>
#include <thread>    // hardware_concurrency (for the info line only)

#ifdef _WIN32
#include <windows.h>  // GetModuleFileNameA
#endif

#include "ode_solver.h"

// Function-pointer types for the two integrator variants, so we can loop over
// the "euler" and "rk4" methods instead of duplicating the timing code.
using CpuFn = void (*)(OscillatorState*, const OscillatorParams*, int, float, int);
using GpuFn = void (*)(OscillatorState*, const OscillatorParams*, int, float, int, float*);

struct Method { const char* name; CpuFn cpu; GpuFn gpu; };

// Directory this executable lives in, so results.csv and the plot script are
// found no matter which folder the program is launched from.
static std::string exe_dir(const char* argv0) {
    std::string path;
#ifdef _WIN32
    char buf[1024];
    DWORD len = GetModuleFileNameA(NULL, buf, sizeof(buf));
    path.assign(buf, len);
#else
    path = argv0 ? argv0 : "";
#endif
    size_t slash = path.find_last_of("/\\");
    return (slash == std::string::npos) ? std::string(".") : path.substr(0, slash);
}

static void make_data(std::vector<OscillatorState>& states,
                      std::vector<OscillatorParams>& params, int n) {
    states.resize(n);
    params.resize(n);
    for (int i = 0; i < n; i++) {
        states[i].x = 1.0f + (i % 10) * 0.1f;
        states[i].v = 0.0f;
        params[i].omega = 1.0f + (i % 5) * 0.05f;
        params[i].zeta  = 0.05f;
    }
}

// Run `run` K times (calling `reset` before each, un-timed); return median ms.
template <class Reset, class Run>
static double median_ms(Reset reset, Run run, int K) {
    std::vector<double> times;
    for (int k = 0; k < K; k++) {
        reset();
        auto a = std::chrono::steady_clock::now();
        run();
        auto b = std::chrono::steady_clock::now();
        times.push_back(std::chrono::duration<double, std::milli>(b - a).count());
    }
    std::sort(times.begin(), times.end());
    return times[times.size() / 2];
}

int main(int argc, char** argv) {
    const float dt = 0.001f;
    const int num_steps = 1000;
    const int sizes[] = {1, 3, 10, 30, 100, 300, 1000, 3000,
                         10000, 30000, 100000, 300000, 1000000};

    const Method methods[] = {
        {"euler", integrate_cpu,     integrate_gpu},
        {"rk4",   integrate_cpu_rk4, integrate_gpu_rk4},
    };

    const std::string dir = exe_dir(argv[0]);

    DeviceInfo dev;
    get_device_info(&dev);
    unsigned cpu_threads = std::thread::hardware_concurrency();

    printf("GPU: %s  |  %d SMs x %d = %d CUDA cores  |  %.1f GB\n",
           dev.name, dev.sms, dev.cores_per_sm, dev.total_cores, dev.mem_gb);
    printf("CPU baseline: single-threaded (machine has %u logical cores)\n", cpu_threads);
    printf("steps per run: %d\n", num_steps);

    // Warm-up: absorb the one-time CUDA context-creation cost.
    {
        std::vector<OscillatorState> ws;
        std::vector<OscillatorParams> wp;
        make_data(ws, wp, 1000);
        integrate_gpu(ws.data(), wp.data(), 1000, dt, num_steps);
    }

    // CSV columns: method, n, CPU time, GPU total time, GPU kernel-only time,
    // speedup (CPU/GPU total), correctness flag.
    std::string csv_path = dir + "/results.csv";
    FILE* csv = fopen(csv_path.c_str(), "w");
    fprintf(csv, "# gpu_name,%s\n", dev.name);
    fprintf(csv, "# gpu_cores,%d\n", dev.total_cores);
    fprintf(csv, "# gpu_sms,%d\n", dev.sms);
    fprintf(csv, "# cpu_threads,%u\n", cpu_threads);
    fprintf(csv, "# num_steps,%d\n", num_steps);
    fprintf(csv, "method,n,cpu_ms,gpu_ms,gpu_kernel_ms,speedup,match\n");

    for (const Method& m : methods) {
        printf("\n=== method: %s ===\n", m.name);
        printf("%12s %12s %12s %12s %12s %8s\n",
               "n", "cpu_ms", "gpu_ms", "kernel_ms", "speedup", "match");
        printf("--------------------------------------------------------------------------\n");

        for (int n : sizes) {
            std::vector<OscillatorState> s0;
            std::vector<OscillatorParams> p;
            make_data(s0, p, n);
            int K = (n <= 1000) ? 9 : (n <= 100000 ? 3 : 1);

            std::vector<OscillatorState> work;
            double cpu_ms = median_ms(
                [&]() { work = s0; },
                [&]() { m.cpu(work.data(), p.data(), n, dt, num_steps); }, K);
            std::vector<OscillatorState> cpu_result = work;

            // Total GPU time (transfer + kernel), no event overhead in the loop.
            double gpu_ms = median_ms(
                [&]() { work = s0; },
                [&]() { m.gpu(work.data(), p.data(), n, dt, num_steps, nullptr); }, K);
<<<<<<< HEAD
            std::vector<OscillatorState> gpu_result = work;

            // One extra call to capture kernel-only time via CUDA events.
=======

            // One extra call to capture kernel-only time via CUDA events.
            // `work` holds the GPU result afterwards, so we diff against it directly.
>>>>>>> 3f85511881955fa392e8b50388fbf2834dcab2f7
            float kernel_ms = 0.0f;
            work = s0;
            m.gpu(work.data(), p.data(), n, dt, num_steps, &kernel_ms);

            double max_err = 0.0;
            for (int i = 0; i < n; i++) {
<<<<<<< HEAD
                max_err = fmax(max_err, fabs(cpu_result[i].x - gpu_result[i].x));
                max_err = fmax(max_err, fabs(cpu_result[i].v - gpu_result[i].v));
=======
                max_err = fmax(max_err, fabs(cpu_result[i].x - work[i].x));
                max_err = fmax(max_err, fabs(cpu_result[i].v - work[i].v));
>>>>>>> 3f85511881955fa392e8b50388fbf2834dcab2f7
            }
            const char* match = (max_err < 1e-3) ? "OK" : "FAIL";

            printf("%12d %12.3f %12.3f %12.3f %11.1fx %8s\n",
                   n, cpu_ms, gpu_ms, kernel_ms, cpu_ms / gpu_ms, match);
            fprintf(csv, "%s,%d,%.4f,%.4f,%.4f,%.3f,%s\n",
                    m.name, n, cpu_ms, gpu_ms, kernel_ms, cpu_ms / gpu_ms, match);
        }
    }

    fclose(csv);
    printf("\nWrote %s\n", csv_path.c_str());

    printf("Plotting results...\n");
    std::string script = "\"" + dir + "/plot_results.py\"";
    if (system(("python " + script).c_str()) != 0)
        system(("python3 " + script).c_str());

    return 0;
}
