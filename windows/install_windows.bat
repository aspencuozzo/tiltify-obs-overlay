@echo off
python -V 2>&1 | find "Python 3." >NUL 2>&1 && (@set pyp=python) && (goto :PYTHON_DOES_EXIST)
python3 -V 2>&1 | find "Python 3." >NUL 2>&1 && (@set pyp=python3) && (goto :PYTHON_DOES_EXIST)
py -V 2>&1 | find "Python 3." >NUL 2>&1 && (@set pyp=py) && (goto :PYTHON_DOES_EXIST)
goto :PYTHON_DOES_NOT_EXIST

:PYTHON_DOES_EXIST
%pyp% -m pip install -r ..\app\requirements.txt || (goto :ERROR_INSTALLING_PACKAGES)
echo: && echo The credentials file will now be opened for you to edit. Press any key to continue. && pause>nul
notepad ..\app\credentials_example.json || (goto :ERROR_OPENING_CREDS)
move ..\app\credentials_example.json ..\app\credentials.json >nul || (goto :ERROR_RENAMING_FILE)
goto :ADD_PATH_TO_SCRIPT

:ADD_PATH_TO_SCRIPT
echo @set pyp=%pyp%> run_windows_bat.new
type run_windows.bat>> run_windows_bat.new
type run_windows_bat.new> run_windows.bat
del run_windows_bat.new
goto :INSTALL_COMPLETE

:INSTALL_COMPLETE
echo: && echo All set! To start the program, simply run run_windows.bat && pause
goto :EOF

@REM Errors
:PYTHON_DOES_NOT_EXIST
echo ERROR: Python 3 could not be found. && pause
goto :EOF

:ERROR_INSTALLING_PACKAGES
echo ERROR: There was an error installing required packages. && pause
goto :EOF

:ERROR_OPENING_CREDS
echo ERROR: Could not open Notepad. && pause
goto :EOF

:ERROR_RENAMING_FILE
echo ERROR: Could not rename credentials file to credentials.json. Please do this manually before running the program. && pause
goto :INSTALL_COMPLETE