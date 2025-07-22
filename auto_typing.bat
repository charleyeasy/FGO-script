@echo off
title auto_typing
nircmd win setsize title auto_typing 3020 1520 800 600
mode con: cols=60 lines=15
nircmd win settopmost title auto_typing 1
python auto_typing.py
