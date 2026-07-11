@echo off
REM Run the benchmark and auto-plot the graph.
REM Build first with build.bat, then run this from anywhere:
REM   cuda-hpc\01_parallel_ode_integrator\run.bat

REM cd into this script's own folder so benchmark.exe, results.csv and
REM plot_results.py all sit in the current directory (the plot step needs this).
cd /d "%~dp0"

if not exist benchmark.exe (
  echo benchmark.exe not found. Build it first:
  echo   build.bat
  exit /b 1
)

benchmark.exe
REM benchmark.exe writes results.csv and then calls plot_results.py, which
REM renders benchmark.png and opens it in your image viewer.
