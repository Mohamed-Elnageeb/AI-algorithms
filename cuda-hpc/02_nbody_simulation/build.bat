@echo off
REM Build the N-body benchmark with the 64-bit MSVC toolchain, from any terminal.
set "VCVARS=C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
if not exist "%VCVARS%" (
  echo ERROR: vcvars64.bat not found at "%VCVARS%" - edit this path.
  exit /b 1
)
call "%VCVARS%"

set "PROJ=%~dp0"
nvcc -O2 -I"%PROJ%include" -o "%PROJ%nbody.exe" ^
  "%PROJ%src\benchmark.cpp" ^
  "%PROJ%src\nbody_cpu.cpp" ^
  "%PROJ%src\nbody_gpu.cu"

if %errorlevel%==0 ( echo. & echo Build OK: "%PROJ%nbody.exe" ) else ( echo. & echo Build FAILED %errorlevel% )
