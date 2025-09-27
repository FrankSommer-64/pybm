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
Erzeugt NSIS Windows-Installer.
"""

import os
import re
import shutil
import tempfile

from pybm import *
from pybm.util import copy_customizable_file_tree, shell_cmd, wheel_file_name
from pybm.wheel import build_wheel


NSIS_COMPILER_EXE = 'makensis.exe'
OUTFILE_PATTERN = re.compile(r'OutFile\s+(.*?)$', re.DOTALL|re.MULTILINE|re.IGNORECASE)


def build_nsis(build_environment: dict, project: str, _feature_set: str):
    """
    Erzeugt einen Installer für Projekt und Feature in <Projekt-Root>/dist.
    :param build_environment: Build-Environment
    :param project: Name des Projekts
    :param _feature_set: Name des Feature-Sets, immer 'all'
    """
    _project_root = build_environment[PAR_PROJECT_ROOT]
    _dist_path = os.path.join(_project_root, 'dist')
    _cur_path = os.getcwd()
    _installer_files = []
    with tempfile.TemporaryDirectory() as _temp_path:
        _temp_data_path = os.path.join(_temp_path, 'data')
        os.mkdir(_temp_data_path, mode=0o755)
        # Daten für den/die Installer zusammenstellen
        for _fs_name, _fs_data in build_environment[PAR_FEATURE_SETS].items():
            _project_version = _fs_data[PAR_PROJECT_VERSION]
            _var_replacements = {'${VERSION}': _project_version}
            # Python-Wheel erzeugen und in data ablegen
            _wheel_file_name = wheel_file_name(build_environment, _fs_name)
            build_wheel(build_environment, project, _fs_name)
            shutil.move(os.path.join(_dist_path, _wheel_file_name), _temp_data_path)
            # projektspezifische Daten kopieren
            if len(_fs_name) == 0:
                _source_path = os.path.join(_project_root, 'build', 'nsis')
            else:
                _source_path = os.path.join(_project_root, 'build', 'featuresets', _fs_name, 'nsis')
            copy_customizable_file_tree(str(_source_path), _temp_path, _var_replacements)
        # Installer erstellen
        _mk_nsis = nsis_compiler()
        os.chdir(_temp_path)
        for _f in os.listdir('.'):
            if not _f.endswith('.nsi'):
                continue
            _installer_files.append(read_outfile(os.path.join(_temp_path, _f)))
            _cmd = [_mk_nsis, _f]
            _rc = shell_cmd(_cmd)
            if _rc != 0:
                raise RuntimeError(f'Build NSIS-Installer {project} fehlgeschlagen')
        # Installer ins dist-Verzeichnis kopieren
        for _f in _installer_files:
            shutil.copy(os.path.join(_temp_path, _f), _dist_path)
        os.chdir(_cur_path)
    print(f'NSIS windows-Installer erstellt.')


def read_outfile(nsi_file_path: str) -> str:
    """
    :param nsi_file_path: Name und Pfad der nsi-Datei zum Erzeugen des Installers
    :return: vom NSIS compiler erzeugte Installer-Datei
    """
    with open(nsi_file_path, 'r', encoding='latin_1') as _nsi_file:
        _contents = _nsi_file.read()
        _m = OUTFILE_PATTERN.search(_contents)
        if not _m:
            raise RuntimeError(f'OutFile in nsi-Datei {nsi_file_path} nicht gefunden')
        return _m.group(1).strip()


def nsis_compiler() -> str:
    """
    :return: Executable des NSIS-Compilers inkl. Pfad
    """
    _nsis_path = os.environ.get(ENVA_NSIS_PATH)
    if _nsis_path is not None:
        if not os.path.isdir(_nsis_path):
            raise RuntimeError(f'Umgebungsvariable {ENVA_NSIS_PATH} zeigt auf nicht existierendes Verzeichnis')
        _nsis_exe = os.path.join(_nsis_path, NSIS_COMPILER_EXE)
        if not os.path.isfile(_nsis_exe):
            raise RuntimeError(f'NSIS Compiler {_nsis_exe} nicht gefunden')
        return _nsis_exe
    _nsis_exe = f'C:\\Program Files (x86)\\NSIS\\{NSIS_COMPILER_EXE}'
    if os.path.isfile(_nsis_exe):
        return _nsis_exe
    _nsis_exe = f'C:\\Program Files\\NSIS\\{NSIS_COMPILER_EXE}'
    if os.path.isfile(_nsis_exe):
        return _nsis_exe
    raise RuntimeError(f'NSIS Compiler nicht gefunden')
