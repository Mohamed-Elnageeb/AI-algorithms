@echo off
REM Build the benchmark with the 64-bit MSVC toolchain, from ANY terminal.
REM Run from the repo root:  cuda-hpc\01_parallel_ode_integrator\build.bat
REM (or cd into this folder and run build.bat)

REM --- locate the 64-bit Visual Studio environment ---
set "VCVARS=C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
if not exist "%VCVARS%" (
  echo.
  echo ERROR: could not find vcvars64.bat at:
  echo   "%VCVARS%"
  echo Edit build.bat and set VCVARS to your Visual Studio path.
  exit /b 1
)
call "%VCVARS%"

REM --- this script's own folder, so paths work from anywhere ---
set "PROJ=%~dp0"

nvcc -O2 -I"%PROJ%include" -o "%PROJ%benchmark.exe" ^
  "%PROJ%src\benchmark.cpp" ^
  "%PROJ%src\ode_solver_cpu.cpp" ^
  "%PROJ%src\ode_solver_gpu.cu"

if %errorlevel%==0 (
  echo.
  echo Build OK: "%PROJ%benchmark.exe"
) else (
  echo.
  echo Build FAILED with exit code %errorlevel%
)
