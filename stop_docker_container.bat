@echo off
for /f %%i in ('docker ps -q') do docker stop %%i
