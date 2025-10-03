@echo off
setlocal

rem -------------------------------------------------------------------------------------------------
rem Funktionen zum Erstellen von Installationspaketen für ein Python-Projekt.
rem Benötigt ein Python virtual environment mit den Packages hatchling, pybm und tomli.
rem Benötigt folgende Umgebungsvariablen:
rem   PYBM_PROJECTS_ROOT Root-Verzeichnis für Projekte
rem   PYBM_VENV_PATH Verzeichnis, in dem das Python virtual environment mit pybm liegt
rem
rem Aufruf: build_py <Paket-Typ> <Projekt> [<Feature-Umfang>]
rem   Paket-Typen: wheel | deb | rpm | nsis | custom
rem
rem -------------------------------------------------------------------------------------------------

rem Parameter prüfen
if -%1-==-- (
  echo Kein Paket-Typ angegeben
  exit /b
)
set "pkg_type=%1"
shift
if -%1-==-- (
  echo Kein Projekt angegeben
  exit /b
)
set "project=%1"
shift

rem Verzeichnis mit dem Python virtual environment prüfen
if -%PYBM_VENV_PATH%-==-- (
  echo Umgebungsvariable PYBM_VENV_PATH nicht gesetzt
  exit /b
)
if not exist %PYBM_VENV_PATH% (
  echo Python virtual environment $PYBM_VENV_PATH nicht gefunden
  exit 1
)
set "act_script=%PYBM_VENV_PATH%/Scripts/activate.bat"
set "deact_script=%PYBM_VENV_PATH%/Scripts/deactivate.bat"
if not exist %act_script% (
  echo Aktivierungsskript für Python virtual environment %act_script% nicht gefunden
  exit /b
)

rem Python virtual environment aktivieren
call %act_script%

rem Build ausführen
echo build_%pkg_type%
echo %project%
echo %*
pybm build_%pkg_type% %project% %1 %2
call %deact_script%
