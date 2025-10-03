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
Erzeugt RedHat Installations-Pakete.
"""

import os
import re
import shutil
import subprocess
import tempfile

from pybm import *
from pybm.util import copy_customizable_file, copy_customizable_file_tree, shell_cmd, wheel_file_name
from pybm.wheel import build_wheel


RPM_WORK_SUBDIRS = ['BUILD', 'RPMS', 'SOURCES', 'SPECS', 'SRPMS', 'tmp']


def build_rpm(build_environment: dict, project: str, feature_set: str = None):
    """
    Erzeugt ein rpm-Paket für Projekt und Feature in <Projekt-Root>/dist.
    :param build_environment: Build-Environment
    :param project: Name des Projekts
    :param feature_set: optional Name des Feature-Sets
    """
    _project_root = build_environment[PAR_PROJECT_ROOT]
    _dist_path = os.path.join(_project_root, 'dist')
    _wheel_file_name = wheel_file_name(build_environment, feature_set)
    _install_path = os.path.join('/opt', project)
    if feature_set is None:
        print(f'Erzeuge rpm-Installationspaket für Projekt {project}')
        _feature_path = os.path.join(_project_root, 'build')
        _feature_data = build_environment[PAR_FEATURE_SETS]['']
        _source_data_path = os.path.join(_project_root, 'build', 'rpm', 'SOURCES')
        _spec_data_path = os.path.join(_project_root, 'build', 'rpm', 'SPECS')
    else:
        print(f'Erzeuge rpm-Installationspaket für Projekt {project}, Feature-Set {feature_set}')
        _feature_path = os.path.join(_project_root, 'build', 'featuresets', feature_set)
        _feature_data = build_environment[PAR_FEATURE_SETS][feature_set]
        _source_data_path = os.path.join(_project_root, 'build', 'featuresets', feature_set, 'rpm',
                                         'SOURCES')
        _spec_data_path = os.path.join(_project_root, 'build', 'featuresets', feature_set, 'rpm',
                                       'SPECS')
    _project_version = _feature_data[PAR_PROJECT_VERSION]
    _package_name = _feature_data[PAR_PACKAGE_NAME]
    _assembly_path = rpm_top_dir()
    _project_dir = f'{_package_name}-{_project_version}'
    _rpm_proj_dir = f'{project}-{_project_version}-root'
    _rpm_build_root = os.path.join(_assembly_path, 'tmp', _rpm_proj_dir)
    # Variablen-Ersetzungen
    _var_replacements = {'${VERSION}': _project_version, '${PACKAGE_NAME}': _package_name,
                         '${WHEEL_FILE_NAME}': _wheel_file_name, '${INSTALL_PATH}': _install_path,
                         '${RPM_BUILD_ROOT}': _rpm_build_root}
    # Arbeitsverzeichnis leeren
    shutil.rmtree(_assembly_path)
    os.mkdir(_assembly_path)
    for _sub_dir in RPM_WORK_SUBDIRS:
        os.mkdir(os.path.join(_assembly_path, _sub_dir))
    # Archiv mit den Projekt-Dateien erzeugen
    with tempfile.TemporaryDirectory() as _temp_path:
        _archive_project_root = os.path.join(_temp_path, _project_dir)
        _archive_file_name = f'{_project_dir}.tar.gz'
        os.mkdir(_archive_project_root, mode=0o755)
        # Python-Wheel erzeugen und in /opt/<project> ablegen
        build_wheel(build_environment, project, feature_set)
        _target_wheel_path = os.path.join(_archive_project_root, 'opt', project)
        os.makedirs(_target_wheel_path, mode=0o755, exist_ok=True)
        shutil.move(os.path.join(_dist_path, _wheel_file_name), _target_wheel_path)
        # projektspezifische Daten kopieren
        copy_customizable_file_tree(_source_data_path, _archive_project_root, _var_replacements)
        os.chdir(_temp_path)
        _cmd = ['tar', '-czf', _archive_file_name, _project_dir]
        _rc = shell_cmd(_cmd)
        if _rc != 0:
            raise RuntimeError(f'Konnte Archiv für {project} nicht erzeugen')
        _archive_target_path = os.path.join(_assembly_path, 'SOURCES')
        shutil.copy(os.path.join(_temp_path, _archive_file_name), _archive_target_path)
    # Steuerdateien kopieren
    _spec_target_path = os.path.join(_assembly_path, 'SPECS')
    for _f in os.listdir(_spec_data_path):
        copy_customizable_file(_spec_data_path, _f, _spec_target_path, _var_replacements)
    # rpm-Paket erstellen
    _cmd = ['rpmbuild', '-bb', os.path.join(_spec_target_path, f'{_package_name}.spec')]
    _rc = shell_cmd(_cmd)
    if _rc != 0:
        raise RuntimeError(f'Build rpm-Paket {project} fehlgeschlagen')
    _rpms_path = os.path.join(_assembly_path, 'RPMS', 'noarch')
    _dist_path = os.path.join(_project_root, 'dist')
    for _f in os.listdir(_rpms_path):
        shutil.copy(os.path.join(_rpms_path, _f), _dist_path)
    print(f'rpm Installationspaket erstellt.')


def rpm_top_dir() -> str:
    """
    :return: Root-Verzeichnis für rpmbuild
    """
    _top_dir = os.path.expanduser('~/rpmbuild')
    try:
        with open(os.path.expanduser('~/.rpmmacros'), 'r') as _f:
            _contents = _f.read().split(os.linesep)
            for _line in _contents:
                if _line.startswith('%_topdir '):
                    _value = _line[9:].strip()
                    _cmds = re.findall(r'(%\(.*\))', _value)
                    for _cmd in _cmds:
                        _os_cmd = _cmd[2:-1]
                        _res = subprocess.run([_os_cmd], shell=True, capture_output=True,
                                              encoding='utf-8')
                        if _res.returncode != 0:
                            raise RuntimeError()
                        _value = _value.replace(_cmd, _res.stdout.strip())
                    _top_dir = _value
                    break
    except (OSError, RuntimeError) as _e:
        print(_e)
    return _top_dir
