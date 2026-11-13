@echo off
title Seed Datos - El Taller del Maestro
cd /d "c:\Users\PC-Solution 30-9-24\Proyectos\proyecto_taller_mecanico"
echo Ejecutando seed de datos...
echo.
entorno\Scripts\python.exe seed_datos.py
echo.
echo --- Finalizado ---
pause

