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
Erzeugt Debian Installations-Pakete.
"""

import os
import shutil
import tempfile

from pybm import *
from pybm.util import copy_customizable_file, copy_customizable_file_tree, shell_cmd, wheel_file_name
from pybm.wheel import build_wheel


CONTROL_ARCHIVE_FILE_NAME = 'control.tar.xz'
DATA_ARCHIVE_FILE_NAME = 'data.tar.xz'
PACKAGE_VERSION_FILE_NAME = 'debian-binary'


def build_deb(build_environment: dict, project: str, feature_set: str = None):
    """
    Erzeugt ein Debian-Installationspaket für angegebenes Projekt und ggf. Feature-Set.
    :param build_environment: Build-Environment
    :param project: Name des Projekts
    :param feature_set: optional Name des Feature-Sets
    """
    _project_root = build_environment[PAR_PROJECT_ROOT]
    _dist_path = os.path.join(_project_root, 'dist')
    _wheel_file_name = wheel_file_name(build_environment, feature_set)
    _install_path = os.path.join('/opt', project)
    if feature_set is None:
        print(f'Erzeuge Debian-Installationspaket für Projekt {project}')
        _feature_path = os.path.join(_project_root, 'build')
        _feature_data = build_environment[PAR_FEATURE_SETS]['']
        _source_data_path = os.path.join(_project_root, 'build', 'deb', 'data')
        _source_control_path = os.path.join(_project_root, 'build', 'deb', 'control')
        _ver_file = os.path.join(_project_root, 'build', 'deb', PACKAGE_VERSION_FILE_NAME)
        _deb_project_name = project
    else:
        print(f'Erzeuge Debian-Installationspaket für Projekt {project}, Feature-Set {feature_set}')
        _feature_path = os.path.join(_project_root, 'build', 'featuresets', feature_set)
        _feature_data = build_environment[PAR_FEATURE_SETS][feature_set]
        _source_data_path = os.path.join(_project_root, 'build', 'featuresets', feature_set,
                                         'deb', 'data')
        _source_control_path = os.path.join(_project_root, 'build', 'featuresets', feature_set,
                                            'deb', 'control')
        _ver_file = os.path.join(_project_root, 'build', 'featuresets', feature_set, 'deb',
                                 PACKAGE_VERSION_FILE_NAME)
        _deb_project_name = f'{project}-{feature_set}'
    _project_version = _feature_data[PAR_PROJECT_VERSION]
    _package_name = _feature_data[PAR_PACKAGE_NAME]
    # Variablen-Ersetzungen
    _var_replacements = {'${VERSION}': _project_version, '${PACKAGE_NAME}': _package_name,
                         '${WHEEL_FILE_NAME}': _wheel_file_name, '${INSTALL_PATH}': _install_path}
    # data-Archiv erzeugen
    with tempfile.TemporaryDirectory() as _temp_path:
        # Python-Wheel erzeugen und in /opt/<project> ablegen
        build_wheel(build_environment, project, feature_set)
        _target_wheel_path = os.path.join(_temp_path, 'opt', project)
        os.makedirs(_target_wheel_path, mode=0o755, exist_ok=True)
        shutil.move(os.path.join(_dist_path, _wheel_file_name), _target_wheel_path)
        # projektspezifische Daten kopieren
        copy_customizable_file_tree(_source_data_path, _temp_path, _var_replacements)
        _data_elements = os.listdir(_temp_path)
        os.chdir(_temp_path)
        _cmd = ['tar', '-cJf', DATA_ARCHIVE_FILE_NAME]
        _cmd.extend(_data_elements)
        _rc = shell_cmd(_cmd)
        if _rc != 0:
            raise RuntimeError(f'Konnte data-Archiv für {project} nicht erzeugen')
        shutil.copy(os.path.join(_temp_path, DATA_ARCHIVE_FILE_NAME), _dist_path)
    # control-Archiv erzeugen
    with tempfile.TemporaryDirectory() as _temp_path:
        # Steuerdateien kopieren
        for _f in os.listdir(_source_control_path):
            copy_customizable_file(_source_control_path, _f, _temp_path, _var_replacements)
        # control-Archiv erzeugen
        _control_elements = os.listdir(_temp_path)
        os.chdir(_temp_path)
        _cmd = ['tar', '-cJf', CONTROL_ARCHIVE_FILE_NAME]
        _cmd.extend(_control_elements)
        _rc = shell_cmd(_cmd)
        if _rc != 0:
            raise RuntimeError(f'Konnte control-Archiv für {project} nicht erzeugen')
        shutil.copy(os.path.join(_temp_path, CONTROL_ARCHIVE_FILE_NAME), _dist_path)
    # Debian-Package-Version kopieren
    shutil.copy(_ver_file, _dist_path)
    # deb-Datei erzeugen
    _deb_package_name = f'{_package_name}-{_project_version}.deb'.replace('_', '-')
    os.chdir(_dist_path)
    _cmd = ['ar', 'cvr', _deb_package_name, PACKAGE_VERSION_FILE_NAME]
    _rc = shell_cmd(_cmd)
    if _rc != 0:
        raise RuntimeError(f'Konnte Debian-Installationspaket für {project} nicht erzeugen')
    _cmd = ['ar', 'vr', _deb_package_name, CONTROL_ARCHIVE_FILE_NAME]
    _rc = shell_cmd(_cmd)
    if _rc != 0:
        raise RuntimeError(f'Konnte Debian-Installationspaket für {project} nicht erzeugen')
    _cmd = ['ar', 'vr', _deb_package_name, DATA_ARCHIVE_FILE_NAME]
    _rc = shell_cmd(_cmd)
    if _rc != 0:
        raise RuntimeError(f'Konnte Debian-Installationspaket für {project} nicht erzeugen')
    os.remove(os.path.join(_dist_path, CONTROL_ARCHIVE_FILE_NAME))
    os.remove(os.path.join(_dist_path, DATA_ARCHIVE_FILE_NAME))
    os.remove(os.path.join(_dist_path, PACKAGE_VERSION_FILE_NAME))
    print(f'Debian Installationspaket {_deb_package_name} erstellt.')
