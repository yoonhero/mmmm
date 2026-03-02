@echo off
setlocal

set "MINGW_BIN=C:\msys64\mingw64\bin"
set "WINDRES=%MINGW_BIN%\windres.exe"
set "GPP=%MINGW_BIN%\g++.exe"

if not exist dist mkdir dist
if not exist build mkdir build

"%WINDRES%" resources\brainfuck_snake.rc -O coff -o build\brainfuck_snake_res.o
if errorlevel 1 exit /b 1

"%GPP%" brainfuck.cpp renderer.cpp build\brainfuck_snake_res.o ^
  -o dist\BrainfuckSnake.exe ^
  -IC:\msys64\mingw64\include\SDL2 -DSDL_MAIN_HANDLED ^
  -LC:\msys64\mingw64\lib ^
  -static -static-libgcc -static-libstdc++ ^
  -lSDL2 -lsetupapi -limm32 -lversion -lole32 -loleaut32 -lwinmm -lgdi32 -lcfgmgr32 -lws2_32 ^
  -mwindows
if errorlevel 1 exit /b 1

echo Build complete: dist\BrainfuckSnake.exe
exit /b 0
