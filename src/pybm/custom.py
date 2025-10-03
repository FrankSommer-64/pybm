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
Erzeugt ein ZIP-Archiv für eine manuelle Installation.
"""

import os
import shutil
import tempfile
import zipfile

from pybm import *
from pybm.util import wheel_file_name
from pybm.wheel import build_wheel


def build_custom(build_environment: dict, project: str, feature_set: str = None):
    """
    Erzeugt ein ZIP-Archiv für das angegebene Projekt.
    :param build_environment: Build-Environment
    :param project: Name des Projekts
    :param feature_set: Name des Feature-Sets, wird ignoriert
    """
    _project_root = build_environment[PAR_PROJECT_ROOT]
    _dist_path = os.path.join(_project_root, 'dist')
    _project_version = next(iter(build_environment[PAR_FEATURE_SETS].values()))[PAR_PROJECT_VERSION]
    _archive_file_name = f'{project}-{_project_version}-custom.zip'
    with tempfile.TemporaryDirectory() as _temp_path:
        _target_path = os.path.join(_temp_path, f'{project}-{_project_version}')
        os.mkdir(_target_path)
        for _fs_name, _fs_data in build_environment[PAR_FEATURE_SETS].items():
            if len(_fs_name) == 0:
                _feature_path = os.path.join(_project_root, 'build')
            else:
                _feature_path = os.path.join(_project_root, 'build', 'featuresets', str(_fs_name))
            # Wheel erzeugen
            _wheel_file_name = wheel_file_name(build_environment, _fs_name)
            build_wheel(build_environment, project, _fs_name)
            shutil.move(os.path.join(_dist_path, _wheel_file_name), _target_path)
            # Zusatzdaten kopieren
            _custom_data_path = os.path.join(_feature_path, 'custom')
            for _path, _dirs, _files in os.walk(_custom_data_path):
                for _file in _files:
                    _file_path = os.path.join(_path, _file)
                    shutil.copy2(str(_file_path), _target_path)
            _aux_root_path = os.path.join(_feature_path, 'deb', 'data')
            for _path, _dirs, _files in os.walk(_aux_root_path):
                for _file in _files:
                    _file_path = os.path.join(_path, _file)
                    shutil.copy2(str(_file_path), _target_path)
        # ZIP-Archiv erzeugen
        _archive_file_path = os.path.join(_dist_path, _archive_file_name)
        with zipfile.ZipFile(_archive_file_path, 'w') as _zf:
            for _path, _dirs, _files in os.walk(_temp_path):
                _arc_path = _path[len(_temp_path):]
                _zf.write(_path, _arc_path)
                for _file in _files:
                    _zf.write(str(os.path.join(_path, _file)), str(os.path.join(_arc_path, _file)))
        print(f'ZIP-Archiv {_archive_file_name} erstellt.')
