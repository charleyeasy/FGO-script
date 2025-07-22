@echo off
title maple
nircmd win setsize title maple 3020 1520 800 600
mode con: cols=60 lines=15
nircmd win settopmost title maple 1
python maplestory_up.py
