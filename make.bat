@echo on
set PY_FILE=text_editor.py
set PROJECT_NAME=PES WE J League Text Editor
set VERSION=1.0.0
set FILE_VERSION=file_version_info.txt
set EXTRA_ARG=

pyinstaller --onefile --window "%PY_FILE%" --name "%PROJECT_NAME%_%VERSION%"  %EXTRA_ARG% --version-file "%FILE_VERSION%"

Rem This command below is just specific for this script

Xcopy /E ".\config\" ".\dist\config\"

Rem end of extra command

cd dist
tar -acvf "%PROJECT_NAME%_%VERSION%.zip" * config
pause
