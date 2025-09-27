# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------
# pybm - Tools für die Entwicklung von Python-Projekten.
#
# Copyright (c) 2025, Frank Sommer.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# -----------------------------------------------------------------------------------------------

"""
Funktionen für Python build tools.
"""

import os
import re
import shutil
import subprocess

import tomli

from pybm import *

PROJECT_VERSION_PATTERN = re.compile(r'^\s*VERSION\s*=\s*(.*)$')


def shell_cmd(cmd: list[str]) -> int:
    """
    Führt den übergebenen Befehl in der Shell aus.
    :param cmd: auszuführender Befehl
    :return: return code.
    :raises subprocess.TimeoutException: falls bei der Kommunikation zum gestarteten Prozess ein Timeout auftritt
    """
    _res = subprocess.run(cmd, capture_output=True, encoding='utf-8')
    if len(_res.stderr) > 0: print(_res.stderr)
    if len(_res.stdout) > 0: print(_res.stdout)
    return _res.returncode


def copy_customizable_file(source_path: str, file_name: str, target_path: str, replacements: dict):
    """
    Kopiert eine Datei ins Build-Verzeichnis und ersetzt ggf. Variablen.
    :param source_path: Verzeichnis, in dem die Datei liegt
    :param file_name: Name der Datei
    :param target_path: Zielverzeichnis
    :param replacements: Daten für die Variablen-Ersetzungen
    """
    _source_fn = os.path.join(source_path, file_name)
    _target_fn = os.path.join(target_path, file_name)
    _contents = ''
    try:
        with open(_source_fn, 'r') as _f:
            _contents = _f.read()
    except UnicodeDecodeError:
        shutil.copy2(_source_fn, _target_fn)
        return
    _stat = os.stat(_source_fn)
    for _var, _value in replacements.items():
        _contents = _contents.replace(_var, _value)
    with open(_target_fn, 'w') as _f:
        _f.write(_contents)
    os.chmod(_target_fn, _stat.st_mode)


def copy_customizable_file_tree(source_path: str, target_path: str, replacements: dict):
    """
    Kopiert einen Verzeichnisbaum ins Build-Verzeichnis und ersetzt ggf. Variablen
    in den kopierten Dateien.
    :param source_path: Verzeichnis, in dem die Datei liegt
    :param target_path: Zielverzeichnis
    :param replacements: Daten für die Variablen-Ersetzungen
    """
    for _dir, _sub_dirs, _files in os.walk(source_path):
        _source_dir = _dir[len(source_path):].lstrip(os.sep)
        _target_dir = os.path.join(target_path, _source_dir)
        os.makedirs(_target_dir, mode=0o755, exist_ok=True)
        for _f in _files:
            copy_customizable_file(_dir, _f, _target_dir, replacements)


def py_config_info(project_root: str, file_path: str) -> dict:
    """
    :param project_root: Root-Verzeichnis des Projekts
    :param file_path: Name und Pfad der hatchling-Konfigurationsdatei
    :returns: relevante Daten der hatchling-Konfigurationsdatei
    """
    if not os.path.isfile(file_path):
        raise RuntimeError(f'Konfigurationsdatei {file_path} nicht gefunden')
    _version = None
    with open(file_path, "rb") as _config_file:
        _toml_data = tomli.load(_config_file)
        _py_package_name = _toml_data['project']['name']
        _version_fn = _toml_data['tool']['hatch']['version']['path']
        _version_file_path = os.path.join(project_root, _version_fn)
        with open(_version_file_path, 'r') as _src_file:
            _lines = _src_file.readlines()
            for _line in _lines:
                _vm = PROJECT_VERSION_PATTERN.match(_line.strip())
                if _vm:
                    _version = _vm.group(1).strip('"').strip("'")
                    break
    if _version is None:
        raise RuntimeError(f'Konnte Projekt-Version für Konfigurationsdatei {file_path} nicht ermitteln')
    return {PAR_PACKAGE_NAME: _py_package_name, PAR_PROJECT_VERSION: _version}


def build_env_for(project: str) -> dict:
    """
    Erzeugt ein Python wheel für das angegebenes Projekt und ggf. Feature-Set.
    :param project: Name des Projekts
    :return: Build-Umgebung.
    :raises RuntimeException: falls die Build-Umgebung nicht korrekt erstellt wurde
    """
    _projects_root = os.getenv(ENVA_PROJECTS_ROOT)
    if _projects_root is None or not os.path.isdir(_projects_root):
        raise RuntimeError(f'Umgebungsvariable {ENVA_PROJECTS_ROOT} nicht gesetzt oder kein Verzeichnis')
    _project_root = os.path.join(_projects_root, project)
    if not os.path.isdir(_project_root):
        raise RuntimeError(f'Projektverzeichnis {_project_root} existiert nicht')
    _testing_root = os.getenv(ENVA_TESTING_ROOT)
    _feature_sets = {}
    _feature_sets_path = os.path.join(_project_root, 'build', 'featuresets')
    if os.path.isdir(_feature_sets_path):
        for _feature_set in os.listdir(_feature_sets_path):
            _cfg_fn = os.path.join(_feature_sets_path, _feature_set, 'wheel', WHEEL_CFG_FILE_NAME)
            _feature_sets[_feature_set] = py_config_info(_project_root, _cfg_fn)
    else:
        _cfg_fn = os.path.join(_project_root, WHEEL_CFG_FILE_NAME)
        _feature_sets[''] = py_config_info(_project_root, _cfg_fn)
    _build_env = {PAR_FEATURE_SETS: _feature_sets, PAR_PROJECT_ROOT: _project_root,
                  PAR_TESTING_ROOT: _testing_root}
    return _build_env


def wheel_file_name(build_environment: dict, feature: str = None) -> str:
    """
    :param build_environment: Build-Umgebung
    :param feature: Name des Features
    :return: Name für das Python wheel für gegebenes Feature
    """
    _fs = '' if feature is None else feature
    _pkg_name = build_environment[PAR_FEATURE_SETS][_fs][PAR_PACKAGE_NAME]
    _version = build_environment[PAR_FEATURE_SETS][_fs][PAR_PROJECT_VERSION]
    return f'{_pkg_name}-{_version}-py3-none-any.whl'
