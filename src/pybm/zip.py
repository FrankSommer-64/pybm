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
Erzeugt ZIP-Archive für eine manuelle Installation.
"""

import os
import shutil
import tempfile
import zipfile

from pybm import *
from pybm.util import wheel_file_name
from pybm.wheel import build_wheel


def build_zip(build_environment: dict, project: str, feature_set: str = None):
    """
    Erzeugt ein ZIP-Archiv für angegebenes Projekt und ggf. Feature-Set.
    :param build_environment: Build-Environment
    :param project: Name des Projekts
    :param feature_set: optional Name des Feature-Sets
    """
    _project_root = build_environment[PAR_PROJECT_ROOT]
    _dist_path = os.path.join(_project_root, 'dist')
    _wheel_file_name = wheel_file_name(build_environment, feature_set)
    if feature_set is None:
        print(f'Erzeuge ZIP-Archiv für Projekt {project}')
        _feature_path = os.path.join(_project_root, 'build')
        _project_version = build_environment[PAR_FEATURE_SETS][''][PAR_PROJECT_VERSION]
        _package_name = build_environment[PAR_FEATURE_SETS][''][PAR_PACKAGE_NAME]
    else:
        print(f'Erzeuge ZIP-Archiv für Projekt {project}, Feature-Set {feature_set}')
        _feature_path = os.path.join(_project_root, 'build', 'featuresets', feature_set)
        _project_version = build_environment[PAR_FEATURE_SETS][feature_set][PAR_PROJECT_VERSION]
        _package_name = build_environment[PAR_FEATURE_SETS][feature_set][PAR_PACKAGE_NAME]
    _archive_file_name = f'{_package_name}-{_project_version}.zip'
    with tempfile.TemporaryDirectory() as _temp_path:
        # Wheel erzeugen
        build_wheel(build_environment, project, feature_set)
        shutil.copy2(str(os.path.join(_dist_path, _wheel_file_name)), _temp_path)
        # Installations-Skript
        _is_path = os.path.join(_feature_path, 'zip')
        for _f in os.listdir(_is_path):
            shutil.copy2(str(os.path.join(_is_path, _f)), _temp_path)
        # weitere Dateien
        _aux_root_path = os.path.join(_feature_path, 'deb', 'data')
        for _path, _dirs, _files in os.walk(_aux_root_path):
            for _file in _files:
                _file_path = os.path.join(_path, _file)
                shutil.copy2(str(_file_path), _temp_path)
        # ZIP-Archiv erzeugen
        _archive_file_path = os.path.join(_dist_path, _archive_file_name)
        with zipfile.ZipFile(_archive_file_path, 'w') as _zf:
            for _path, _dirs, _files in os.walk(_temp_path):
                _arc_path = _path[len(_temp_path):]
                _zf.write(_path, _arc_path)
                for _file in _files:
                    _zf.write(str(os.path.join(_path, _file)), str(os.path.join(_arc_path, _file)))
        print(f'ZIP-Archiv {_archive_file_name} erstellt.')
