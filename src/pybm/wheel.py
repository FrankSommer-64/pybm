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
Erzeugt Python wheels per hatchling.
"""

import os
import shutil

from pybm import *
from pybm.util import shell_cmd


def build_wheel(build_environment: dict, project: str, feature_set: str = None):
    """
    Erzeugt ein Python wheel für angegebenes Projekt und ggf. Feature-Set.
    :param build_environment: Build-Environment
    :param project: Name des Projekts
    :param feature_set: optional Name des Feature-Sets
    """
    _cfg_file_path = os.path.join(build_environment[PAR_PROJECT_ROOT], WHEEL_CFG_FILE_NAME)
    _rm_cfg_file = False
    try:
        if feature_set is not None:
            print(f'Erzeuge Python wheel für Projekt {project}, Feature-Set {feature_set}')
            # Konfigurationsdatei des Feature-Sets ins Projekt-Rootverzeichnis kopieren
            _f_cfg_file_path = os.path.join(build_environment[PAR_PROJECT_ROOT], 'build',
                                            'featuresets', feature_set, 'wheel', WHEEL_CFG_FILE_NAME)
            if not os.path.isfile(_f_cfg_file_path):
                raise RuntimeError(f'Konfigurationsdatei {_f_cfg_file_path} nicht gefunden')
            shutil.copy(str(_f_cfg_file_path), str(_cfg_file_path))
            _rm_cfg_file = True
        else:
            print(f'Erzeuge Python wheel für Projekt {project}')
        if not os.path.isfile(_cfg_file_path):
            raise RuntimeError(f'Konfigurationsdatei {_cfg_file_path} nicht gefunden')
        os.chdir(build_environment[PAR_PROJECT_ROOT])
        _cmd = ['hatchling', 'build']
        if shell_cmd(_cmd) != 0:
            raise RuntimeError('Build fehlgeschlagen')
    finally:
        if _rm_cfg_file and os.path.exists(_cfg_file_path):
            os.remove(_cfg_file_path)
