@echo off
set estado_archivo=estado_hecho.txt
:loop
python jose.py
:wait_for_file
if exist %estado_archivo% (
    echo Script Python ha completado la acción deseada. Deteniendo el bucle...
    del %estado_archivo%
    goto end
) else (
    goto loop
)
:end
echo El script ha terminado.
